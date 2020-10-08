from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import Config
from app.database.models import Base

engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    recreate_database()