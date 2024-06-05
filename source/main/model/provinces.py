from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from source import db

class Provinces(db.Model):
    __tablename__ = 'Provinces'
    ProvinceID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProvinceName = db.Column(db.String(50), unique=True, nullable=False)