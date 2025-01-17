from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from database import Base, engine

# Таблицы ассоциаций
likes_association = Table(
    "likes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("post_id", Integer, ForeignKey("tweets.id"), primary_key=True),
)

subscriptions_association = Table(
    "subscriptions",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("followed_id", Integer, ForeignKey("users.id"), primary_key=True),
)

media_association = Table(
    "tweet_media",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("tweets.id"), primary_key=True),
    Column("media_id", Integer, ForeignKey("media.id"), primary_key=True),
)


# Модели
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    last_name = Column(String, index=True)
    api_key = Column(String)

    user_tweets = relationship("Tweets", back_populates="user", cascade="all, delete-orphan")
    liked_posts = relationship(
        "Tweets", secondary=likes_association, back_populates="liked_by_users"
    )
    followers = relationship(
        "Users",
        secondary=subscriptions_association,
        primaryjoin=id == subscriptions_association.c.followed_id,
        secondaryjoin=id == subscriptions_association.c.follower_id,
        backref="following",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "api_key": self.api_key,
            "followers": [follower.id for follower in self.followers],
            "following": [followed.id for followed in self.following],
        }


class Tweets(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    post_data = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="user_tweets")
    liked_by_users = relationship(
        "Users", secondary=likes_association, back_populates="liked_posts"
    )
    media_ids = relationship(
        "Media", secondary=media_association, back_populates="tweets"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "post_data": self.post_data,
            "likes": [user.to_dict() for user in self.liked_by_users],
            "media": [media.to_dict() for media in self.media_ids],
        }


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)

    tweets = relationship(
        "Tweets", secondary=media_association, back_populates="media_ids"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "file_path": self.file_path,
        }


Base.metadata.create_all(bind=engine)
