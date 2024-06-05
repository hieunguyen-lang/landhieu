from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class ForumPosts(db.Model):
    __tablename__ = 'ForumPosts'
    PostID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    GroupID = db.Column(db.Integer, db.ForeignKey('Groups.GroupID'))
    Title = db.Column(db.Text)
    Content = db.Column(db.Text)
    PostTime = db.Column(db.DateTime, default=db.func.current_timestamp())
    IPPosted = db.Column(db.String(45))
    PostLatitude = db.Column(db.Numeric(10, 8))
    PostLongitude = db.Column(db.Numeric(11, 8))
    UpdatePostAt = db.Column(db.DateTime, default=db.func.current_timestamp())

