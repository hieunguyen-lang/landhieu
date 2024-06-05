from flask import jsonify, request, make_response
from source import db
from source.main.model.userPhotos import UserPhotos
from source.main.function.users import *
from source.main.extend import *
from source.main.model.users import Users
from flask_mail import *
from datetime import datetime


def addImage(id):
    try:
        photo_url = base64ToByte(request.json.get("PhotoURL"))
        set_as_avatar = request.json.get("SetAsAvatar")
        print(str(id))
        image_data = UserPhotos(
            PhotoURL=photo_url,
            UserID=id,
            UploadTime=datetime.now(),
            SetAsAvatar=set_as_avatar,
        )
        print(str(image_data))
        if set_as_avatar == True:
            UserPhotos.query.filter(UserPhotos.UserID == id).update({"SetAsAvatar": 0})
        print(set_as_avatar)
        print("da qua phan add images")
        # _________________________________add avatar vao link profile
        user = Users.query.filter(Users.UserID == id).update({"avatarLink": photo_url})
        db.session.add(image_data)
        db.session.commit()
        return viewProfileById(id)

    except Exception as e:
        print(e)
        return make_response(jsonify({"status": 500, "message": str(e)}), 500)


def setAvatarFromProfile(id):
    try:
        json_data = request.json
        UserPhotos.query.filter(UserPhotos.UserID == id).update({"SetAsAvatar": 0})
        UserPhotos.query.filter(UserPhotos.PhotoID == json_data["PhotoID"]).update(
            {"SetAsAvatar": 1}
        )
        # url = UserPhotos.query.filter(UserPhotos.PhotoID == json_data["PhotoID"]).first()
        # Users.query.filter(Users.UserID == id).update({"avatarLink": url.PhotoURL})
        # db.session.commit()
        # return {"PhotoID": json_data["PhotoID"], "UserID": id,"NewAvatar":url.PhotoURL, "SetAsAvatar": True}
        url = UserPhotos.query.filter(UserPhotos.PhotoID == json_data["PhotoID"]).first()

        if url:
            Users.query.filter(Users.UserID == id).update({"avatarLink": url.PhotoURL})
            db.session.commit()
            return {"PhotoID": json_data["PhotoID"], "UserID": id, "NewAvatar": byteToString(url.PhotoURL), "SetAsAvatar": True}
        else:
        #  return make_response(jsonify({"status": 404, "message": "Photo not found"}), 404)
            return make_response(jsonify({"status": 404, "message": f"Photo with ID {json_data['PhotoID']} not found"}), 404)


    except Exception as e:
        print(e)
        return make_response(jsonify({"status": 500, "message": "An error occurred" + str(e)}), 500)


def viewAllImage(id):
    try:
        data = []
        # user_images = UserPhotos.query.filter(UserID=id).all()
        user_images = UserPhotos.query.filter(UserPhotos.UserID == id).all()
        print(str(user_images))
        if user_images:
            for image_data in user_images:
                image_info = {
                    "PhotoID": image_data.PhotoID,
                    "PhotoURL": byteToString(image_data.PhotoURL),
                    "UploadTime": image_data.UploadTime,
                    "SetAsAvatar": image_data.SetAsAvatar,
                }
                data.append(image_info)
            return {"status": 200, "UserID": id, "Photos": data}
        else:
            return make_response(
                jsonify({"status": 404, "message": "User not found"}), 404
            )
    except Exception as e:
        print(e)
        error = "Ma Loi: " + str(e)
        return make_response(jsonify({"status": 500, "message": error}), 500)


def viewSingleImage(id):
    try:
        image_to_view = UserPhotos.query.get(id)

        if image_to_view:
            return {
                "PhotoID": image_to_view.PhotoID,
                "PhotoURL": byteToString(image_to_view.PhotoURL),
                "UploadTime": image_to_view.UploadTime,
                "SetAsAvatar": image_to_view.SetAsAvatar,
            }
        else:
            return make_response(
                jsonify({"status": 404, "message": "Image not found"}), 404
            )
    except Exception as e:
        print(e)
        return make_response(jsonify({"status": 500, "message": str(e)}), 500)


def deleteImageUser(id):
    try:
        image_to_delete = UserPhotos.query.get(id)

        if image_to_delete:
            db.session.delete(image_to_delete)
            db.session.commit()
            return make_response(
                jsonify({"status": 200, "message": "Image deleted successfully"}), 200
            )
        else:
            return make_response(
                jsonify({"status": 404, "message": "Image not found"}), 404
            )
    except Exception as e:
        return make_response(
        jsonify({"status": 500, "message": f"An error occurred: {str(e)}"}), 500
    )

