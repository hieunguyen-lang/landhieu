from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class MessagePhotos(db.Model):
    __tablename__ = 'MessagePhotos'
    PhotoID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MessageID = db.Column(db.Integer, db.ForeignKey('Messages.MessageID'))
    PhotoURL = db.Column(db.String(255), nullable=False)
    UploadTime = db.Column(db.DateTime, default=db.func.current_timestamp())
