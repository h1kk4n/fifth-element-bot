from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

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


class User(Base):
    __tablename__ = 'users'
    tg_chat_id = Column(Integer, primary_key=True)
    surname = Column(String)
    name = Column(String)
    patronymic = Column(String)
    score = Column(Integer)
