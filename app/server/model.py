from datetime import date
from sqlalchemy import Column, Integer, String
from json import dumps
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class HandledMsg(Base):
    __tablename__ = 'handled_msg'

    update_id = Column(String, primary_key=True)
    from_id = Column(String)
    date = Column(Integer)


