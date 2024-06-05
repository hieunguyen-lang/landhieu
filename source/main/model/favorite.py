from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class Favorite(db.Model):
    __tablename__ = 'Favorite'
    FavoriteID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    PostID = db.Column(db.Integer, db.ForeignKey('ForumPosts.PostID'))
    FavoriteType = db.Column(db.Boolean, default=False)
    FavoriteTime = db.Column(db.DateTime, default=db.func.current_timestamp())
