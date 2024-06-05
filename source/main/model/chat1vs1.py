from sqlalchemy import Column, DateTime, ForeignKey, Integer, String,Text
from sqlalchemy.sql import func
from source.main.model.users import Users
from source import db
import random
import string
from sqlalchemy.orm import relationship

def generate_random_id(length):
    characters = string.ascii_letters + string.digits  # Bao gồm chữ cái và chữ số
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id

class Chat1vs1(db.Model):
    __tablename__ = 'chat1vs1'
    id=Column(Integer,nullable=False,primary_key=True,autoincrement=True)
    idReceive=Column(Integer, ForeignKey(Users.UserID),nullable=False)
    idSend=Column(Integer,nullable=False)
    room=Column(Text,nullable=False)
    text=Column(Text,nullable=True)
    img=Column(Text,nullable=True)
    type=Column(Text,nullable=False,default="text")
    state=Column(Text,nullable=True,default="not seen")
    sendAt=Column(DateTime(timezone=True),default=func.now())
    chat = relationship("Users", backref="chat1vs1")
