from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class Messages(db.Model):
    __tablename__ = 'Messages'
    MessageID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SenderID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    ReceiverID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Content = db.Column(db.Text)
    MessageTime = db.Column(db.DateTime, default=db.func.current_timestamp())
    Image = db.Column(db.LargeBinary, default = None)
    IsSeen = db.Column(db.SmallInteger, default=0)

   