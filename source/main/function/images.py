from flask import jsonify, request, make_response
from source import db
from source.main.model.images import *
from source.main.function.users import *
from flask_mail import *
from source.main.function.middleware import *
PATH_IMAGE = r"/home/thinkdiff/Documents/Image"

def uploadImage(id_user):
    try:

        data = request.form
        image_upload = request.files.get("uploaded_image")
        url = make_url_image(id_user, PATH_IMAGE, image_upload, "img")
        if url:
            new_data = Images(
                id_user = id_user,
                image_url= url
            )
            db.session.add(new_data)
            db.session.commit()
            return jsonify({"status": 200, "message": "Success", "Info": new_data.image_url}), 200
        else :
            print('xxx')
    except Exception as e:
        print("____Error from server:______ " + str(e))
        return make_response(jsonify("____Error from server:______ ", str(e)), 500)

def view_image(id_user, file_name):
    try:
        user_path = os.path.join(PATH_IMAGE, str(id_user))
        return send_from_directory(user_path, file_name)
    except Exception as e:
        return make_response(jsonify("Something went wrong: ", str(e)), 500)
