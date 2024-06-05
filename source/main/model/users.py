from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db


class Users(db.Model):
    __tablename__ = "Users"
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FullName = db.Column(db.String(50), nullable=False)
    Username = db.Column(db.String(50), unique=True, nullable=True)
    Password = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Phone = db.Column(db.String(20))
    Gender = db.Column(db.Enum("Nam", "Nữ", "Đồng tính nữ", "Đồng tính nam"))
    BirthDate = db.Column(db.Date)
    BirthTime = db.Column(db.Time)
    ProvinceID = db.Column(db.Integer, db.ForeignKey("Provinces.ProvinceID"))
    IsAnonymous = db.Column(db.SmallInteger, nullable=True)
    RegistrationIP = db.Column(db.String(45))
    LastLoginIP = db.Column(db.String(45))
    LastActivityTime = db.Column(db.DateTime)
    IsLoggedIn = db.Column(db.Boolean, default=False)
    Role = db.Column(db.Boolean, nullable=False)
    avatarLink = db.Column(db.LargeBinary, nullable=True)
    Bio = db.Column(db.String(255), nullable=True)
    CurrentAdd = db.Column(db.String(255), nullable=True)
    BirthPlace = db.Column(db.String(255), nullable=True)