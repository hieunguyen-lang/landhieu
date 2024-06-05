from source import db
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from source.main.model.users import Users

from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

class Relationship(db.Model):
    __tablename__ = 'relationship'
    id = Column(Integer, primary_key=True, autoincrement=True)
    idSend = Column(Integer, nullable=False)
    idReceive=Column(Integer, ForeignKey(Users.id),nullable=False)
    relation=Column(Boolean, nullable=False , default="True")
    qh = relationship("Users", backref="relationship")