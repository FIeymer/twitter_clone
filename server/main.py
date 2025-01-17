import os
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, File, Header, UploadFile
from pydantic import BaseModel
from starlette.responses import FileResponse

import models
from database import session

app = FastAPI()

UPLOAD_DIRECTORY = "media_files"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


class TweetRequest(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[list[int]] = None


user_error = {
    "result": False,
    "error": "Invalid API Key",
    "error_message": "API ключ не найден",
}


@app.get("/index")
async def read_main():
    return FileResponse("../client/static/index.html")


@app.get("/create_new_user")
async def root(
    api_key: str = Header(...),
):
    new_user = models.Users(
        name="test_name", api_key=api_key, last_name="test_last_name"
    )
    session.add(new_user)
    session.commit()
    return 200


@app.post("/api/tweets")
async def create_tweet(
    tweet: TweetRequest,
    api_key: str = Header(...),
):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if not user:
        return user_error
    new_tweet = models.Tweets(
        post_data=tweet.tweet_data,
        user_id=user.id,
        media_ids=(
            [
                session.query(models.Media).filter(models.Media.id == media_id).first()
                for media_id in tweet.tweet_media_ids
            ]
            if tweet.tweet_media_ids
            else []
        ),
    )

    session.add(new_tweet)
    session.commit()
    session.refresh(new_tweet)

    return {"result": True, "tweet_id": new_tweet.id}


@app.post("/api/medias")
async def load_media(
    api_key: str = Header(...),
    file: UploadFile = File(...),
):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if not file or not user:
        return {
            "result": False,
            "error": "",
            "error_message": "",
        }

    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    new_media = models.Media(
        file_path=file_path,
    )

    session.add(new_media)
    session.commit()
    session.refresh(new_media)

    return {
        "result": True,
        "media_id": new_media.id,
    }


@app.delete("/api/tweets/{post_id}")
def delete_tweet(
    post_id: int,
    api_key: str = Header(...),
):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if user:
        if post_id == user.id:
            session.query(models.Tweets).filter(models.Tweets.id == post_id).delete()
            session.commit()
            return {"result": True}
        else:
            return {
                "result": False,
                "error_type": "",
                "error_message": "Пост не принадлежит пользователю",
            }
    else:
        return user_error


@app.post("/api/tweets/{post_id}/likes")
def like_tweet(
    post_id: int,
    api_key: str = Header(...),
):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if user:
        tweet = session.query(models.Tweets).filter(models.Tweets.id == post_id).first()
        tweet.liked_by_users.append(user)
        session.commit()
        return {"result": True}
    else:
        return user_error


@app.delete("/api/tweets/{post_id}/likes")
def delete_like(
    post_id: int,
    api_key: str = Header(...),
):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if user:
        tweet = session.query(models.Tweets).filter(models.Tweets.id == post_id).first()
        tweet.liked_by_users.remove(user)
        session.commit()
        return {"result": True}
    else:
        return user_error


@app.post("/api/users/{user_id}/follow")
def follow_user(user_id: int, api_key: str = Header(...)):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if user:
        user_to_followed = (
            session.query(models.Users).where(models.Users.id == user_id).first()
        )
        user.following.append(user_to_followed)
        session.commit()
        return {"result": True}
    else:
        return user_error


@app.delete("/api/users/{user_id}/follow")
def unfollow_user(user_id: int, api_key: str = Header(...)):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if user:
        user_to_followed = (
            session.query(models.Users).where(models.Users.id == user_id).first()
        )
        user.following.remove(user_to_followed)
        session.commit()
        return {"result": True}
    else:
        return user_error


@app.get("/api/tweets")
def get_tweets(api_key: str = Header(...)):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if user:
        following_users = user.following
        tweets = (
            session.query(models.Tweets)
            .all()
        )
        data_tweet = []
        for tweet in tweets:
            attachments = [post_media.file_path for post_media in tweet.media_ids]
            data_tweet.append(
                {
                    "id": tweet.id,
                    "content": tweet.post_data,
                    "attachments": attachments,
                    "author": {"id": tweet.user_id, "name": tweet.user.name},
                    "likes": [
                        {"user_id": user_like.id, "name": user_like.name}
                        for user_like in tweet.liked_by_users
                    ],
                }
            )
        return {"result": True, "tweets": data_tweet}
    else:
        return user_error


@app.get("/api/users/me")
def get_me(api_key: str = Header(...)):
    user = session.query(models.Users).where(models.Users.api_key == api_key).first()
    if user:
        return {
            "result": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "followers": [
                    {"id": followers.id, "name": followers.name}
                    for followers in user.followers
                ],
                "following": [
                    {"id": following.id, "name": following.name}
                    for following in user.following
                ],
            },
        }
    else:
        return user_error


@app.get("/api/users/{user_id}")
def get_user(user_id: int, api_key: str = Header(...)):
    main_user = (
        session.query(models.Users).where(models.Users.api_key == api_key).first()
    )
    if main_user:
        user = session.query(models.Users).where(models.Users.id == user_id).first()
        if user:
            return {
                "result": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "followers": [
                        {"id": followers.id, "name": followers.name}
                        for followers in user.followers
                    ],
                    "following": [
                        {"id": following.id, "name": following.name}
                        for following in user.following
                    ],
                },
            }
        else:
            return {
                "result": False,
                "error": "",
                "error_message": "Пользователь не найден",
            }
    else:
        return user_error
