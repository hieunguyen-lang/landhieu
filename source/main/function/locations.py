from source import db
from flask import request, make_response, jsonify
from sqlalchemy import or_, and_
from source.main.model.locations import Locations
from source.main.model.relationships import Relationships
from source.main.model.users import Users
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.sql import label, text
from source.main.extend import *
import math

R = 6371


def setCurrentLocation(id):
    if request.method == "PATCH":
        json_data = request.json
        try:
            location = Locations.query.filter(
                and_(Locations.UserID == id, Locations.Type == "current")
            ).first()
            print()
            if location:
                location.Longitude = json_data["Longitude"]
                location.Latitude = json_data["Latitude"]
                location.UpdateTime = datetime.now()
                db.session.commit()

                return {
                    "status": 200,
                    "message": "Set Locations Current Successfully!",
                    "Location": {
                        "UserID": id,
                        "Latitude": json_data["Latitude"],
                        "Longitude": json_data["Longitude"],
                        "UpdateTime": datetime.now(),
                    },
                }, 200
            return make_response(
                jsonify(
                    {
                        "status": 400,
                        "message": "No current location record found for the user ID",
                    }
                ),
                400,
            )
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "An error occurred"}), 400
            )


def calculateDistance(UserID1, UserID2):
    try:
        unit = "km"
        user_data1 = Locations.query.filter(
            and_(Locations.UserID == UserID1, Locations.Type == "current")
        ).first()
        user_data2 = Locations.query.filter(
            and_(Locations.UserID == UserID2, Locations.Type == "current")
        ).first()

        if user_data1 is None or user_data2 is None:
            return make_response(
                jsonify({"status": 404, "Message": "User data not found"}), 404
            )

        dlat = math.radians(user_data2.Latitude - user_data1.Latitude)
        dlon = math.radians(user_data2.Longitude - user_data1.Longitude)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(user_data1.Latitude))
            * math.cos(math.radians(user_data2.Latitude))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        if distance < 1:
            distance *= 1000
            unit = "m"

        result = {"status": 200, "distance": distance, "unit": unit}
        return jsonify(result)

    except Exception as e:
        return make_response(
            jsonify({"status": 500, "Message": "An error occurred"}), 500
        )


def calculateDistanceBetweenTwoPoint(lat1, lon1, lat2, lon2):
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def countUserInRadius(UserID, radius):
    try:
        user_data = Locations.query.filter(
            and_(Locations.UserID == UserID, Locations.Type == "current")
        ).first()

        if user_data is None:
            return make_response(
                jsonify({"status": 404, "message": "User data not found"}), 404
            )

        user_lat = float(user_data.Latitude)
        user_lon = float(user_data.Longitude)

        users_in_radius = [
            user
            for user in Locations.query.filter(Locations.Type == "current").all()
            if calculateDistanceBetweenTwoPoint(
                user_lat, user_lon, float(user.Latitude), float(user.Latitude)
            )
            <= radius
        ]

        count = len(users_in_radius)

        return make_response(jsonify({"status": 200, "count": count}), 200)
    except Exception as e:
        print(e)
        return make_response(
            jsonify({"status": 500, "message": "An error occurred!"}), 500
        )


def calculateDistanceInRadius(UserID, radius):
    try:
        user_data = Locations.query.filter(
            and_(Locations.UserID == UserID, Locations.Type == "current")
        ).first()

        # Handle case where user data is not found
        if user_data is None:
            return make_response(
                jsonify({"status": 404, "message": "User data not found"}), 404
            )

        user_lat = float(user_data.Latitude)
        user_lon = float(user_data.Longitude)

        # Assuming Locations is a list of dictionaries
        users_in_radius = Locations.query.filter(Locations.Type == "current").all()

        distances_in_radius = []

        for user in users_in_radius:
            if (
                user.UserID != UserID
                and calculateDistanceBetweenTwoPoint(
                    user_lat, user_lon, float(user.Latitude), float(user.Latitude)
                )
                <= radius
            ):
                
                check = Relationships.query.filter(or_(
                    and_(Relationships.UserID == user.UserID, Relationships.RelatedUserID == UserID)
                    ,and_(Relationships.UserID == UserID, Relationships.RelatedUserID == user.UserID)
                )
                ).first()
                if check:
               
                    pass
                else:
                    users_data_detail = Users.query.filter(
                        Users.UserID == user.UserID
                    ).first()
                    distances_in_radius.append(
                        {
                            "UserID": user.UserID,
                            "IsLoggedIn": users_data_detail.IsLoggedIn,
                            "Distance": calculateDistanceBetweenTwoPoint(
                                user_lat,
                                user_lon,
                                float(user.Latitude),
                                float(user.Latitude),
                            ),
                            "FullName": users_data_detail.FullName,
                            "Email": users_data_detail.Email,
                            "Gender": users_data_detail.Gender,
                            "ProvinceID": users_data_detail.ProvinceID,
                            "LastActivityTime": users_data_detail.LastActivityTime,
                            "avatarLink": byteToString(users_data_detail.avatarLink),
                            "Bio": users_data_detail.Bio,
                            "CurrentAdd": users_data_detail.CurrentAdd,
                            "BirthPlace": users_data_detail.BirthPlace,
                            "BirthDate": (
                                users_data_detail.BirthDate.strftime("%Y-%m-%d")
                                if users_data_detail.BirthDate
                                else None
                            ),
                            "BirthTime": (
                                users_data_detail.BirthTime.strftime("%H:%M:%S")
                                if users_data_detail.BirthTime
                                else None
                            ),
                        }
                    )
        return jsonify(
            {"status": 200, "UserID": UserID, "Distances": distances_in_radius}
        )
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": 500, "message": str(e)}), 500)
