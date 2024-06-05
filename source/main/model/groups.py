from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db


class Groups(db.Model):
    __tablename__ = "Groups"
    GroupID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey("Users.UserID"))
    GroupName = db.Column(db.String(50), unique=True, nullable=False)
    CreateAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    avatarLink = db.Column(db.LargeBinary, unique=True, nullable=True)
    userNumber = db.Column(db.Integer, nullable=True)
