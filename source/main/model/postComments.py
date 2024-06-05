from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class PostComments(db.Model):
    __tablename__ = 'PostComments'
    CommentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PostID = db.Column(db.Integer, db.ForeignKey('ForumPosts.PostID'))
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Content = db.Column(db.Text)
    CommentTime = db.Column(db.DateTime, default=db.func.current_timestamp())
    CommentUpdateTime = db.Column(db.DateTime, default=db.func.current_timestamp())
