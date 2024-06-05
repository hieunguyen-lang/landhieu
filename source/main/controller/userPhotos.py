from source import app, mail
from source.main.function.userPhotos import *
from flask import jsonify, make_response, request, url_for
from itsdangerous import URLSafeTimedSerializer
from flask_mail import *
from sqlalchemy import or_
from source.main.model.users import Users
from source.main.model.userPhotos import UserPhotos
from postmarker.core import PostmarkClient
from passlib.hash import pbkdf2_sha256
import random


#add image
app.add_url_rule('/api/profile/add_image/<id>', methods=['POST'], view_func=addImage)

#Set Avatar From Profile
app.add_url_rule('/api/profile/setAvatar/<id>', methods=['PATCH'], view_func=setAvatarFromProfile)

#View all image user
app.add_url_rule('/api/profile/viewAllImage/<id>', methods=['GET'], view_func=viewAllImage)

#View all image user
app.add_url_rule('/api/profile/viewSingleImage/<id>', methods=['GET'], view_func=viewSingleImage)

#Delete Image
app.add_url_rule('/api/profile/deleteImageUser/<id>', methods=['DELETE'], view_func=deleteImageUser)