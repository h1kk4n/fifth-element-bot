from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()


class Code(Base):
    __tablename__ = 'codes'
    id = Column(Integer)
    value = Column(String, primary_key=True)
    cost = Column(Integer)

    def __repr__(self):
        return f'№{self.id} {self.value} - стоимость {self.cost}'


class Speaker(Base):
    __tablename__ = 'speakers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __repr__(self):
        return f"<b>{self.name}</b>\n\n" \
               f"{self.description}"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_chat_id = Column(Integer, default=None)
    surname = Column(String)
    name = Column(String)
    patronymic = Column(String)
    score = Column(Integer, default=0)
    auth_code = Column(String)

    def __repr__(self):
        return f"Вы <b>{self.surname} {self.name}</b>>\n" \
               f"У вас {self.score} очков"


class Moderators(Base):
    __tablename__ = 'moderators'
    tg_chat_id = Column(Integer, primary_key=True)
