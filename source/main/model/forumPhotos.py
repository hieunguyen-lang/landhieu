from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class ForumPhotos(db.Model):
    __tablename__ = 'ForumPhotos'
    PhotoID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PostID = db.Column(db.Integer, db.ForeignKey('ForumPosts.PostID'))
    PhotoURL = db.Column(db.LargeBinary, nullable=False)
    UploadTime = db.Column(db.DateTime, default=db.func.current_timestamp())
