from sqlalchemy import  Column, ForeignKey, Integer, String

from source import db
from source.main.model.users import Users

class Images(db.Model):
    __tablename__ = 'Images'
    id_user = Column(Integer, ForeignKey(Users.UserID), nullable=False)
    image_url = Column(String(255), nullable=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
