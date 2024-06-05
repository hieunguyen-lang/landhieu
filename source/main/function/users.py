from flask import jsonify, request, make_response, send_from_directory, url_for
from source import app, db
from source.main.model.users import Users
from source.main.model.locations import Locations
from source.main.model.userPhotos import UserPhotos
from source.main.extend import *
from source import app
from flask_jwt_extended import create_access_token
from sqlalchemy import or_, text, and_
import time
import jwt
from itsdangerous import URLSafeTimedSerializer
from flask_mail import *
from postmarker.core import PostmarkClient
from sqlalchemy.exc import IntegrityError
import random
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
import requests
import secrets
import ipaddress
import string
import json
import re

client = PostmarkClient(server_token=app.config["POSTMARK_API"])
s = URLSafeTimedSerializer(app.config["SECRET_KEY"])


def isUserOffline(user):
    current_time = datetime.now()
    last_request_time = user.LastActivityTime

    if last_request_time is not None:
        if (current_time - last_request_time) > timedelta(minutes=1):
            return True
    return False


def isUserOffline(user):
    current_time = datetime.now()
    last_request_time = user.LastActivityTime

    if last_request_time is not None:
        if (current_time - last_request_time) > timedelta(minutes=1):
            return True
    return False


def formatTimeDelta(time_delta):
    days = time_delta.days
    seconds = time_delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days} ngày"
    elif hours > 0:
        return f"{hours} giờ"
    elif minutes > 0:
        return f"{minutes} phút"
    else:
        return "ít hơn 1 phút"


def checkOnline(UserID):
    user = Users.query.get(UserID)
    try:
        if isUserOffline(user):
            time_since_last_activity = datetime.now() - user.LastActivityTime
            formatted_time = formatTimeDelta(time_since_last_activity)
            response_data = {
                "Status": "Offline",
                "UserID": user.UserID,
                "Username": user.Username,
                "OfflineTime": formatted_time,
            }
            return make_response(jsonify(response_data), 200)
        else:
            response_data = {"Status": 200, "Message": "Online"}
            return make_response(jsonify(response_data), 200)

    except Exception as e:
        return make_response(
            jsonify({"Status": 500, "message": "An error occurred"}), 500
        )


def checkOnlineForAllUsers():
    try:
        users = Users.query.all()

        online_users = []
        offline_users = []

        for user in users:
            if isUserOffline(user):
                time_since_last_activity = datetime.now() - user.LastActivityTime
                formatted_time = formatTimeDelta(time_since_last_activity)
                offline_users.append(
                    {
                        "UserID": user.UserID,
                        "Username": user.Username,
                        "OfflineTime": formatted_time,
                    }
                )
            else:
                online_users.append({"UserID": user.UserID, "Username": user.Username})

        response_data = {
            "Status": 200,
            "OnlineUsers": online_users,
            "OfflineUsers": offline_users,
        }

        return make_response(jsonify(response_data), 200)

    except Exception as e:
        print(e)
        return make_response(
            jsonify({"Status": 500, "message": "An error occurred"}), 500
        )


def isValidEmail(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return email_regex.match(email) and " " not in email


def isValidUsername(username):
    username_regex = re.compile(r"^[a-zA-Z0-9_]+$")
    return username_regex.match(username) and " " not in username


def isAnonymous(username):
    user = Users.query.filter(Users.Username == username).first()
    print(user)
    print(username)
    if user.IsAnonymous == 1:
        return 1
    return 0


def isAnonymousByID(idUser):
    user = Users.query.filter(Users.UserID == idUser).first()
    print(user)
    print(idUser)
    if user.IsAnonymous == 1:
        return 1
    return 0


def viewProfileById(idUser):
    try:
        if isAnonymousByID(idUser):
            return make_response(
                jsonify({"Status": 404, "message": "Username is Anonymous!"})
            )

        data = []
        user = Users.query.filter(Users.UserID == idUser).first()
        if user:
            user_data = {
                "UserID": user.UserID,
                "Username": user.Username,
                "FullName": user.FullName,
                "Email": user.Email,
                "Phone": user.Phone,
                "Password": user.Password,
                "Gender": user.Gender,
                "avatarLink":  byteToString(user.avatarLink),
                "BirthDate": (
                    user.BirthDate.strftime("%Y-%m-%d") if user.BirthDate else None
                ),
                "BirthTime": (
                    user.BirthTime.strftime("%H:%M:%S") if user.BirthTime else None
                ),
                "RegistrationIP": user.RegistrationIP,
                "LastLoginIP": user.LastLoginIP,
                "LastActivityTime": user.LastActivityTime,
                "IsLoggedIn": user.IsLoggedIn,
                "Role": user.Role,
                "ProvinceID": user.ProvinceID,
            }
            print(user.avatarLink)
            images = UserPhotos.query.filter_by(UserID=user.UserID).all()
            photo_urls = [byteToString(image.PhotoURL) for image in images]

            if photo_urls:
                user_data["PhotoURL"] = photo_urls
            data.append(user_data)
            print(data)
            return {"status": 200, "Users": data}
        else:
            return make_response(
                jsonify({"status": 404, "message": "User not found"}), 404
            )
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": 500, "message": str(e)}), 500)


def viewProfile(username):
    try:
        if not isValidUsername(username):
            return make_response(
                jsonify(
                    {
                        "Status": 400,
                        "message": "Username can only contain alphanumeric characters and underscores.",
                    }
                )
            )

        if isAnonymous(username):
            return make_response(
                jsonify({"Status": 404, "message": "Username is Anonymous!"})
            )

        dataReturn = []
        user = Users.query.filter(Users.Username == username).first()
        if user:
            user_data = {
                "UserID": user.UserID,
                "Username": user.Username,
                "FullName": user.FullName,
                "Email": user.Email,
                "Phone": user.Phone,
                "Password": user.Password,
                "Gender": user.Gender,
                "avatarLink": byteToString(user.avatarLink),
                "BirthDate": (
                    user.BirthDate.strftime("%Y-%m-%d") if user.BirthDate else None
                ),
                "BirthTime": (
                    user.BirthTime.strftime("%H:%M:%S") if user.BirthTime else None
                ),
                "RegistrationIP": user.RegistrationIP,
                "LastLoginIP": user.LastLoginIP,
                "LastActivityTime": user.LastActivityTime,
                "IsLoggedIn": user.IsLoggedIn,
                "Role": user.Role,
                "ProvinceID": user.ProvinceID,
                "Bio": user.Bio,
                "CurrentAdd": user.CurrentAdd,
                "BirthPlace": user.BirthPlace,
            }
            images = UserPhotos.query.filter_by(UserID=user.UserID).all()
            photo_urls = [byteToString(image.PhotoURL) for image in images]

            if photo_urls:
                user_data["PhotoURL"] = photo_urls
            dataReturn.append(user_data)
            print(str(user.avatarLink))
            return {"status": 200, "Users": dataReturn}
        else:
            return make_response(
                jsonify({"status": 404, "message": "User not found"}), 404
            )
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": 500, "message": str(e)}), 500)


def verifyLink():
    try:
        json = request.json
        print(json)
        if bool(json):
            print(json["Username"])
            user = Users.query.filter(
                or_(Users.Username == json["Username"], Users.Email == json["Email"])
            ).first()
            if not user:
                token = s.dumps(json, salt=app.config["SECURITY_PASSWORD_SALT"])
                link = url_for("confirm", token=token, _external=True)
                response = client.emails.send(
                    From="admin@samnotes.online",
                    To=json["Email"],
                    Subject="Confirm",
                    TextBody="IUDI thanks for using our service. Your confirmation link is: \n "
                    + link,
                )
                return {"status": 200, "message": "Please check your email or spam"}
            else:
                return make_response(
                    jsonify(
                        {"status": 400, "message": "Account or gmail already exists"}
                    ),
                    400,
                )
        else:
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )
    except Exception as e:
        return make_response(jsonify({"status": 500, "message": str(e)}), 500)


def confirm(token):
    try:
        json = s.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=3600)
        user = Users.query.filter_by(Email=json["Email"]).first()
        if user:
            return "Your account was already"
        else:
            createUser(json)
    except:
        return "Your link was expired. Try again"
    return "Confirm successfully. Try to login"


def createUser(data):
    try:
        json_data = data
        user = Users(
            Username=json_data["Username"],
            FullName=json_data["FullName"],
            Email=json_data["Email"],
            Password=pbkdf2_sha256.hash(json_data["Password"]),
            RegistrationIP=request.remote_addr,
            Role=0,
        )
        db.session.add(user)
        db.session.commit()

        user = Users.query.filter_by(Username=json_data["Username"]).first()

        if user:
            user_id = user.UserID

            location_register = Locations(
                UserID=user_id,
                Latitude=json_data["Latitude"],
                Longitude=json_data["Longitude"],
                Type="registration",
                UpdateTime=datetime.now(),
            )
            db.session.add(location_register)
            db.session.commit()

            location_login = Locations(
                UserID=user_id,
                Latitude=json_data["Latitude"],
                Longitude=json_data["Longitude"],
                Type="login",
                UpdateTime=datetime.now(),
            )
            db.session.add(location_login)
            db.session.commit()

            location_current = Locations(
                UserID=user_id,
                Latitude=json_data["Latitude"],
                Longitude=json_data["Longitude"],
                Type="current",
                UpdateTime=datetime.now(),
            )
            db.session.add(location_current)
            db.session.commit()

            return "Create Successfully!"
        else:
            return "User not found."

    except IntegrityError as e:
        db.session.rollback()
        print(f"Error: {e}")
        return "User with the same FullName already exists."

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return "An error occurred while creating the user."


# change password
def change(data):
    try:
        json = data
        user = Users.query.filter(Users.gmail == json["Email"]).first()
        user.Password = pbkdf2_sha256.hash(json["Password"])
        db.session.commit()
    except Exception as e:
        print(e)
        return "Updated!"


def timeOffline(UserID):
    try:
        User = Users.query.filter(Users.UserID == id).first()
        if User:
            if User.IsLoggedIn:
                return "User Online!"
            else:
                LastActivityTime = User.LastActivityTime
                current_time = datetime.now()
                time_difference = current_time - LastActivityTime
                return f"Online: {time_difference}"
        else:
            return "User does not exist!"
    except Exception as e:
        print(e)
        return "Unable to calculate time."


def create_user():
    try:
        json_data = request.json
        username = json_data.get("Username")
        email = json_data.get("Email")

        if not username or not email:
            return "Username and Email are required."

        user = Users.query.filter(
            or_(Users.Username == username, Users.Email == email)
        ).first()

        if not user:
            new_user = Users(
                Username=username,
                FullName=json_data.get("FullName"),
                Email=email,
                Password=pbkdf2_sha256.hash(json_data.get("Password")),
                RegistrationIP=request.remote_addr,
                
            )
            db.session.add(new_user)
            db.session.commit()
            return "Create successfully!"
        else:
            return "Username or Email already exists!"

    except Exception as e:
        return str(e)


def createUsers():
    try:
        json_data = request.json

        if json_data["Latitude"] == "" and json_data["Longitude"] == "":
            print("------", str(json_data))
            print(str(json_data["Latitude"]) + "________" + str(json_data["Longitude"]))
            return make_response(
                jsonify(
                    {"Status": 500, "message": "Latitude and Longitude need require!"}
                ),
                500,
            )
        if json_data["Gender"] not in ["Nam", "Nữ", "Đồng tính nữ", "Đồng tính nam"]:
            print(str(json_data["Gender"]) + " invalid!")
            return make_response(
                jsonify(
                    {"Status": 500, "message": "Gender invalid!"}
                ),
                500,
            )
        if not isValidEmail(json_data["Email"]):
            return make_response(
                jsonify({"Status": 400, "message": "Invalid email format."}, 400)
            )

        if not isValidUsername(json_data["Username"]):
            return make_response(
                jsonify(
                    {
                        "Status": 400,
                        "message": "Username can only contain alphanumeric characters and underscores.",
                    }
                ),
                400,
            )
        if json_data["avatarLink"] == "":
            print("please insert avatarLink")
            return make_response(
                jsonify(
                    {
                        "Status": 400,
                        "message": "please insert avatarLink",
                    }
                ),
                400,
            )
        if json_data["LastLoginIP"] == "":
            print("please insert LastLoginIP")
            return make_response(
                jsonify(
                    {
                        "Status": 400,
                        "message": "please insert LastLoginIP - please parse json from http://ip-api.com/json/ for get current IP in front end",
                    }
                ),
                400,
            )
        print(json_data["LastLoginIP"])
        user = Users(
            Username=json_data["Username"],
            FullName=json_data["FullName"],
            Email=json_data["Email"],
            Password=pbkdf2_sha256.hash(json_data["Password"]),
            RegistrationIP=request.remote_addr,
            LastActivityTime=datetime.now(),
            Role=0,
            avatarLink=base64ToByte(json_data["avatarLink"]),
            LastLoginIP=json_data["LastLoginIP"],
            Gender=json_data["Gender"]
        )
        db.session.add(user)
        db.session.commit()
        print(str(user))
        user = Users.query.filter_by(Username=json_data["Username"]).first()

        if user:
            username = user.Username

            location_register = Locations(
                UserID=user.UserID,
                Latitude=json_data["Latitude"],
                Longitude=json_data["Longitude"],
                Type="registration",
                UpdateTime=datetime.now(),
                LastLoginIP=json_data["LastLoginIP"],
            )
            db.session.add(location_register)
            db.session.commit()

            location_login = Locations(
                UserID=user.UserID,
                Latitude=json_data["Latitude"],
                Longitude=json_data["Longitude"],
                Type="login",
                UpdateTime=datetime.now(),
                LastLoginIP=json_data["LastLoginIP"],
            )
            db.session.add(location_login)
            db.session.commit()

            location_current = Locations(
                UserID=user.UserID,
                Latitude=json_data["Latitude"],
                Longitude=json_data["Longitude"],
                LastLoginIP=json_data["LastLoginIP"],
                Type="current",
                UpdateTime=datetime.now(),
            )
            db.session.add(location_current)
            db.session.commit()
            return viewProfile(username)
        else:
            return make_response(
                jsonify({"Status": 400, "message": "Username or Gmail exist."}), 400
            )

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        error = str(e)
        return make_response(
            jsonify(
                {
                    "Status": 500,
                    "message": "Username and Gmail exist ",
                    "debugMess": error,
                }
            ),
            500,
        )


def loginUser():
    if request.method == "POST":
        json_data = request.json
        try:
            user = Users.query.filter(
                or_(
                    Users.Username == json_data.get("Username"),
                    Users.Email == json_data.get("Email"),
                )
            ).first()

            if user:
                print(json_data.get("Password"))
                print(user.Password)
                if pbkdf2_sha256.verify(json_data.get("Password"), user.Password):
                    print(request.remote_addr)
                    print(json_data.get("LastLoginIP"))
                    user.LastLoginIP = json_data.get("LastLoginIP")
                    user.IsLoggedIn = True
                    user.LastActivityTime = datetime.now()
                    db.session.commit()

                    user_id = user.UserID
                    username = user.Username

                    location_login = Locations.query.filter_by(
                        UserID=user_id, Type="login"
                    ).first()

                    if location_login:
                        location_login.Latitude = json_data.get("Latitude")
                        location_login.Longitude = json_data.get("Longitude")
                        location_login.LastLoginIP = json_data.get("LastLoginIP")
                        location_login.UpdateTime = datetime.now()
                    else:
                        location_login = Locations(
                            UserID=user_id,
                            Latitude=json_data.get("Latitude"),
                            Longitude=json_data.get("Longitude"),
                            LastLoginIP=json_data.get("LastLoginIP"),
                            Type="login",
                            UpdateTime=datetime.now(),
                        )
                        db.session.add(location_login)

                    db.session.commit()

                    return {
                        "status": 200,
                        "message": "Login successfully",
                        "user": viewProfile(username),
                        "jwt": create_access_token(
                            identity={"UserID": user.UserID, "Email": user.Email}
                        ),
                    }, 200

            return make_response(
                jsonify(
                    {"status": 400, "message": "Password or user name is incorrect"}
                ),
                400,
            )
        except Exception as e:
            print(e)
            return make_response(jsonify({"status": 400, "message": str(e)}), 400)


def logout(id):
    if request.method == "POST":
        User = Users.query.filter(Users.UserID == id).first()
        User.LastActivityTime = datetime.now()
        User.IsLoggedIn = False
        db.session.commit()
    return {"LastActivityTime": User.LastActivityTime, "IsLoggedIn": User.IsLoggedIn}


def stateLogin():
    if request.method == "GET":
        try:
            data = []
            all_user = db.session.execute(text("SELECT * FROM Users"))
            for user in all_user:
                data.append(
                    {
                        "UserID": user.UserID,
                        "Username": user.Username,
                        "FullName": user.FullName,
                        "Email": user.Email,
                        "Phone": user.Phone,
                        "Password": user.Password,
                        "Gender": user.Gender,
                        "BirthDate": user.BirthDate.strptime("%Y-%m-%d"),
                        "BirthTime": user.BirthTime.strptime("%H:%M:%S"),
                    }
                )
            return {"status": 200, "Users": data}
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "States has some wrong"}), 400
            )


def cofirmToken():
    if request.method == "GET":
        token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjgzOGMwNmM2MjA0NmMyZDk0OGFmZmUxMzdkZDUzMTAxMjlmNGQ1ZDEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI5NDYyNjQ1NzQ2MDAtNDVscGxkMWMyZGlic2tzaGw1NWQ3OWxhdWh0ZWY4cmsuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI5NDYyNjQ1NzQ2MDAtNDVscGxkMWMyZGlic2tzaGw1NWQ3OWxhdWh0ZWY4cmsuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTA0Nzc3OTE0MzgyMzQ0NzA2MzMiLCJlbWFpbCI6InBodWNwaHVjMTkxMjAwMUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmJmIjoxNjkzOTc0MTM1LCJuYW1lIjoiUGjDumMgTmd1eeG7hW4gVsSDbiIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQWNIVHRkMGhEemkzb1p6c3Axekl0UG5NeU9fVnViMGZrWEkyVl9zUEYySGZaYzRJZz1zOTYtYyIsImdpdmVuX25hbWUiOiJQaMO6YyIsImZhbWlseV9uYW1lIjoiTmd1eeG7hW4gVsSDbiIsImxvY2FsZSI6InZpIiwiaWF0IjoxNjkzOTc0NDM1LCJleHAiOjE2OTM5NzgwMzUsImp0aSI6IjQzYzYwOTRlZjhiYTg4MzgwNWYxZDhmYjZjOWJhZmE4MWFmMzI5MzMifQ.DvgHH6Wg5I2BIsSjsJ0wjmP52Bdh6yKzF2RC6pM4pPeqq7efuS3QgJ0zgIYYsH4ooLYIZFmizEZ_5m0PmAcmkXvZGBBwzPy3OKDWgcwMh_5un7zm_vZOGRQBneaHEfHCf7kD9n5IC0u7nJMGLarQYlc_s8Bon82A6oO6d--__2f9vKNmHSE1b9zHB8iTvJ899ia8mgKV5vaQFOzbuU0T68fY8-Mw7CcrvuW3uW3e65bXjxX2rQ3u2kUIWvFF5bIzzDme-2FwACVV9HY_Y9ZkCAqLeZ5fptFila41BafsDVd8DMFJ3FCzYItJ28zOJSQ4iQSANPaKzJ5tUkvesr6kAA"
        secret_key = "devsenior"
        try:
            decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
            print(decoded_token)
            return decoded_token
        except jwt.ExpiredSignatureError:
            return "Token hết hạn"
        except jwt.InvalidTokenError:
            return "Token không hợp lệ"


def change():
    if request.method == "PATCH":
        json_data = request.json
        user = Users.query.filter(Users.Password == json_data["Password"]).first()

        if user:
            user.Password = pbkdf2_sha256.hash(json_data["NewPassword"])
            db.session.commit()
            return "Successfully!"
        else:
            return "1"


# reset password
def forgotPassword():
    json = request.json
    try:
        if bool(json):
            user = Users.query.filter(Users.Email == json["Email"]).first()
            if user:
                token = s.dumps(user.Email, salt=app.config["SECURITY_PASSWORD_SALT"])
                msg = Message(
                    "Password reset request",
                    sender=app.config["MAIL_USERNAME"],
                    recipients=[json["Email"]],
                )
                link = url_for("confirmForgotPassword", token=token, _external=True)
                random_password = "".join(
                    random.choice(string.ascii_letters + string.digits)
                    for _ in range(8)
                )
                response = client.emails.send(
                    From="admin@samnotes.online",
                    To=user.Email,
                    Subject="Password reset request!",
                    TextBody="New Password IUDI is: " + random_password,
                )
                user.Password = pbkdf2_sha256.encrypt(str(random_password))
                db.session.commit()
                return {
                    "status": 200,
                    "message": "Please check your email or spam " + link,
                }
            else:
                return make_response(
                    jsonify({"status": 400, "message": "Account or gmail no exists"}),
                    400,
                )
        else:
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )
    except Exception as e:
        return make_response(
            jsonify({"status": 400, "message": "Request fail. Please try again"}), 400
        )


def forgot(Email):
    try:
        json = request.json
        user = Users.query.filter(Users.Email == Email).first()
        if not user:
            return "Your account does not exist!"
        else:
            user.Password = pbkdf2_sha256.hash(json["Password"])
            db.session.commit()
            return "Updated password successfully!"
    except Exception as e:
        return e


def confirmForgotPassword(token):
    try:
        json = s.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
        forgot(json)

    except Exception as e:
        print(e)
        return "Your link was expired!!!!. Try again"
    return "Updated password succsess "


def changePassword(id):
    print("_____changePassword___")
    if request.method == "PATCH":
        try:
            json = request.json
            user = Users.query.filter(Users.UserID == id).first()
            passHash = pbkdf2_sha256.encrypt(json["Password"])
            print("old pass =>", json["Password"])
            print("send old pass =>", passHash)
            print("user old pass =>", user.Password)
            if pbkdf2_sha256.verify(json.get("Password"), user.Password):
                # if pbkdf2_sha256.verify(passHash, user.Password):
                new_password = pbkdf2_sha256.encrypt(json["NewPassword"])
                user.Password = new_password
                db.session.commit()
                # print(user.BirthDate.strftime("%Y-%m-%d"))
                # print(user.BirthTime.strftime("%H:%M:%S"))
                return make_response(
                    {
                        "UserID": id,
                        "Username": user.Username,
                        "FullName": user.FullName,
                        "Email": user.Email,
                        "Phone": user.Phone,
                        "Password": json["NewPassword"],
                        "Gender": user.Gender,
                        # "BirthDate": str(user.BirthDate),
                        # "BirthTime": str(user.BirthTime),
                        "RegistrationIP": user.RegistrationIP,
                        "LastLoginIP": user.LastLoginIP,
                        "LastActivityTime": user.LastActivityTime,
                        "IsLoggedIn": user.IsLoggedIn,
                        "Message": "Change Password Sucessfully!",
                    },
                    200,
                )

            else:
                print("Current password is not correct")
                return "Current password is not correct"
        except Exception as e:
            print(e)
            return "An error occurred " + str(e)


def confirmEmail(token):
    try:
        json = s.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
        change(json)
        return "Updated password succsess "
    except Exception as e:
        print(e)
        return "Your link was expired!!!!."


# Anonymous
def changeAnonymous(id):
    try:
        if request.method == "PATCH":
            User = Users.query.filter(Users.UserID == id).first()
            if User.IsAnonymous == False:
                User.IsAnonymous = True
                db.session.commit()
                return {
                    "UserID": user.UserID,
                    "Username": user.Username,
                    "FullName": user.FullName,
                    "Email": user.Email,
                    "Phone": user.Phone,
                    "Password": user.Password,
                    "Gender": user.Gender,
                    "BirthDate": user.BirthDate.strftime("%Y-%m-%d"),
                    "BirthTime": user.BirthTime.strftime("%H:%M:%S"),
                    "RegistrationIP": user.RegistrationIP,
                    "LastLoginIP": user.LastLoginIP,
                    "LastActivityTime": user.LastActivityTime,
                    "IsLoggedIn": user.IsLoggedIn,
                    "IsAnonymous": False,
                    "Message": "Change Sucessfully!",
                }
            else:
                User.IsAnonymous = False
                db.session.commit()
                return {
                    "UserID": user.UserID,
                    "Username": user.Username,
                    "FullName": user.FullName,
                    "Email": user.Email,
                    "Phone": user.Phone,
                    "Password": user.Password,
                    "Gender": user.Gender,
                    "BirthDate": user.BirthDate.strftime("%Y-%m-%d"),
                    "BirthTime": user.BirthTime.strftime("%H:%M:%S"),
                    "RegistrationIP": user.RegistrationIP,
                    "LastLoginIP": user.LastLoginIP,
                    "LastActivityTime": user.LastActivityTime,
                    "IsLoggedIn": user.IsLoggedIn,
                    "IsAnonymous": True,
                }
    except:
        print(e)
        return "An error occurred"


# Gender
def changeGender(id):
    try:
        if request.method == "PATCH":
            json_data = request.json
            gender = json_data.get("Gender")

            allowed_genders = ["Nam", "Nữ", "Đồng tính nam", "Đồng tính nữ"]
            if gender in allowed_genders:
                user = Users.query.filter(Users.UserID == id).first()

                if user:
                    user.Gender = gender
                    db.session.commit()
                    return {
                        "UserID": user.UserID,
                        "Username": user.Username,
                        "FullName": user.FullName,
                        "Email": user.Email,
                        "Phone": user.Phone,
                        "Password": user.Password,
                        "Gender": gender,
                        "BirthDate": user.BirthDate.strftime("%Y-%m-%d"),
                        "BirthTime": user.BirthTime.strftime("%H:%M:%S"),
                        "RegistrationIP": user.RegistrationIP,
                        "LastLoginIP": user.LastLoginIP,
                        "LastActivityTime": user.LastActivityTime,
                        "IsLoggedIn": user.IsLoggedIn,
                        "IsAnonymous": user.IsAnonymous,
                        "Message": "Change Sucessfully!",
                    }
                else:
                    return "User not found"
            else:
                return "Invalid gender value. Allowed values are: male, female, lesbian, gay man"
    except Exception as e:
        print(e)
        return "An error occurred"


# Change Phone Number
def changePhone(id):
    try:
        if request.method == "PATCH":
            json_data = request.json
            phone = json_data.get("Phone")

            user = Users.query.filter(Users.UserID == id).first()

            if user:
                if phone:
                    user.Phone = phone
                    db.session.commit()
                    return {
                        "UserID": user.UserID,
                        "Username": user.Username,
                        "FullName": user.FullName,
                        "Email": user.Email,
                        "Phone": phone,
                        "Password": user.Password,
                        "Gender": user.Gender,
                        "BirthDate": user.BirthDate.strftime("%Y-%m-%d"),
                        "BirthTime": user.BirthTime.strftime("%H:%M:%S"),
                        "RegistrationIP": user.RegistrationIP,
                        "LastLoginIP": user.LastLoginIP,
                        "LastActivityTime": user.LastActivityTime,
                        "IsLoggedIn": user.IsLoggedIn,
                        "Message": "Change Sucessfully!",
                    }
                else:
                    return "Invalid or missing BirthTime field in JSON data", 400
            else:
                return "User not found", 404
    except Exception as e:
        print(e)
        return "An error occurred", 500


# Change Birth Date
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError


def changeBirthDate(id):
    try:
        if request.method == "PATCH":
            json_data = request.json
            # birth_date = (json_data.get("BirthDate"), ("%Y-%m-%d"),)
            birth_date = datetime.strptime(json_data.get("BirthDate"), "%Y-%m-%d")
            user = Users.query.filter(Users.UserID == id).first()

            if user:
                if birth_date:
                    user.BirthDate = birth_date
                    db.session.commit()
                    return jsonify(
                        {
                            "UserID": user.UserID,
                            "Username": user.Username,
                            "FullName": user.FullName,
                            "Email": user.Email,
                            "Phone": user.Phone,
                            "Password": user.Password,
                            "Gender": user.Gender,
                            "BirthDate": user.BirthDate.strftime("%Y-%m-%d") if user.BirthDate else None,
                            "BirthTime": user.BirthTime.strftime("%H:%M:%S") if user.BirthTime else None,
                            "RegistrationIP": user.RegistrationIP,
                            "LastLoginIP": user.LastLoginIP,
                            "LastActivityTime": user.LastActivityTime,
                            "IsLoggedIn": user.IsLoggedIn,
                            "Message": "Change Sucessfully!",
                        }
                    )
                else:
                    return (
                        jsonify(
                            {"error": "Invalid or missing BirthDate field in JSON data"}
                        ),
                        400,
                    )
            else:
                return jsonify({"error": "User not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An error occurred: " + str(e)}), 500


# Change Birth Time
def changeBirthTime(id):
    try:
        if request.method == "PATCH":
            # birth_date = datetime.strptime(json_data.get("BirthDate"), "%Y-%m-%d")
            # user = Users.query.filter(Users.UserID == id).first()
            json_data = request.json
            birth_time = datetime.strptime(json_data.get("BirthTime"), ("%H:%M:%S"))
            user = Users.query.filter(Users.UserID == id).first()

            if user:
                if birth_time:
                    user.BirthTime = birth_time
                    db.session.commit()
                    return {
                        "UserID": user.UserID,
                        "Username": user.Username,
                        "FullName": user.FullName,
                        "Email": user.Email,
                        "Phone": user.Phone,
                        "Password": user.Password,
                        "Gender": user.Gender,
                        "BirthDate": user.BirthDate.strftime("%Y-%m-%d") if user.BirthDate else None,
                        "BirthTime": user.BirthTime.strftime("%H:%M:%S") if user.BirthTime else None,
                        # "BirthDate": user.BirthDate.strftime("%Y-%m-%d"),
                        # "BirthTime": birth_time,
                        "RegistrationIP": user.RegistrationIP,
                        "LastLoginIP": user.LastLoginIP,
                        "LastActivityTime": user.LastActivityTime,
                        "IsLoggedIn": user.IsLoggedIn,
                        "Message": "Change Sucessfully!",
                    }
                else:
                    return "Invalid or missing BirthTime field in JSON data", 400
            else:
                return "User not found", 404
    except Exception as e:
        print(e)
        return "An error occurred", 500


def checkStatus(id):
    try:
        if request.method == "GET":
            user = Users.query.filter(Users.UserID == id).first()
            if user:
                return {"UserID": user.UserID, "IsLoggedIn": user.IsLoggedIn}
            else:
                return "User does not exits!"
    except Exception as e:
        print(e)
        return "An error occured", 500


from datetime import datetime

# ... (import các module cần thiết)


def updateUser(id):
    ProvinceID = ""
    if request.method == "PUT":
        try:
            data_json = request.json
            user = Users.query.get(id)
            print(str(user))
            if user:
                if "FullName" in data_json:
                    user.FullName = data_json["FullName"]
                    print("__FullName___" + user.FullName)
                if "Email" in data_json:
                    print("__Email___" + user.Email)
                    user.Email = data_json["Email"]
                if "Phone" in data_json:
                    print("__Phone___" + user.Email)
                    user.Phone = data_json["Phone"]
                if "Gender" in data_json:
                    user.Gender = data_json["Gender"]
                if "BirthDate" in data_json:
                    user.BirthDate = datetime.strptime(
                        data_json["BirthDate"], "%Y-%m-%d"
                    )
                if "BirthTime" in data_json:
                    user.BirthTime = datetime.strptime(
                        data_json["BirthTime"], "%H:%M:%S"
                    )
                if "Bio" in data_json:
                    user.Bio = data_json["Bio"]
                if "CurrentAdd" in data_json:
                    user.CurrentAdd = data_json["CurrentAdd"]
                if "BirthPlace" in data_json:
                    user.BirthPlace = data_json["BirthPlace"]
                if "ProvinceID" in data_json:
                    ProvinceID_int = int(data_json["ProvinceID"])
                    user.ProvinceID = ProvinceID_int
                    ProvinceID = data_json["ProvinceID"]
                    print("__ProvinceID___" + str(user.ProvinceID))
                print("USERID____CHUAN_BI_UPDATE " + str(user.UserID))
                db.session.commit()
                new_user = {
                    "UserID": user.UserID,
                    "Username": user.Username,
                    "FullName": user.FullName,
                    "Email": user.Email,
                    "Phone": user.Phone,
                    "Password": user.Password,
                    "Gender": user.Gender,
                    "BirthDate": user.BirthDate.strftime("%Y-%m-%d"),
                    "BirthTime": user.BirthTime.strftime("%H:%M:%S"),
                    "RegistrationIP": user.RegistrationIP,
                    "LastLoginIP": user.LastLoginIP,
                    "LastActivityTime": user.LastActivityTime,
                    "IsLoggedIn": user.IsLoggedIn,
                    "Bio":user.Bio,
                    "BirthPlace":user.BirthPlace,
                    "CurrentAdd":user.CurrentAdd,
                    "avatarLink":byteToString(user.avatarLink)
                }
                return make_response(
                    jsonify({"status": 200, "Message": "User updated successfully", "data":new_user},)
                )
            else:
                return make_response(
                    jsonify({"status": 404, "message": "User not found"}), 404
                )
        except Exception as e:
            print(e)
            error = "Bad request " + str(e) + "__ProvinceID___" + str(ProvinceID)
            return make_response(jsonify({"status": 400, "message": error}), 400)
