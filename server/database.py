import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Создаем базовый класс для моделей
Base = declarative_base()

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Создаем движок и сессию
engine = create_engine(
    "postgresql+psycopg2://admin:admin@postgres_db:5432/twitter_db", echo=True
)
Session = sessionmaker(bind=engine)
session = Session()
