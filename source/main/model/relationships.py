from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class Relationships(db.Model):
    __tablename__ = 'Relationships'
    RelationshipID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    RelatedUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    RelationshipType = db.Column(db.Enum('block', 'other', 'favorite'), nullable=False)
    relation= db.Column(db.Boolean, nullable=False , default="True")
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    CreateTime = db.Column(db.DateTime, default=db.func.current_timestamp())
