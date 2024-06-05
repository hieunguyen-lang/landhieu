from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db


class Locations(db.Model):
    __tablename__ = "Locations"
    LocationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey("Users.UserID"))
    Latitude = db.Column(db.Numeric(10, 8))
    Longitude = db.Column(db.Numeric(11, 8))
    Type = db.Column(db.Enum("registration", "login", "current"), default="current")
    UpdateTime = db.Column(db.DateTime, default=db.func.current_timestamp())
    LastLoginIP = db.Column(db.String(200), nullable=False)
