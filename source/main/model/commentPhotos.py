from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class CommentPhotos(db.Model):
    __tablename__ = 'CommentPhotos'
    PhotoID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CommentID = db.Column(db.Integer, db.ForeignKey('PostComments.CommentID'))
    PhotoURL = db.Column(db.LargeBinary, nullable=False)
    UploadTime = db.Column(db.DateTime, default=db.func.current_timestamp())
