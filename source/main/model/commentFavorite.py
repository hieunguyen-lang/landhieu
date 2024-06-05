from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class CommentFavorite(db.Model):
    __tablename__ = 'CommentFavorite'
    CommentFavoriteID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    CommentID = db.Column(db.Integer, db.ForeignKey('PostComments.CommentID'))
    FavoriteType = db.Column(db.Boolean, default=False)
    FavoriteTime = db.Column(db.DateTime, default=db.func.current_timestamp())
