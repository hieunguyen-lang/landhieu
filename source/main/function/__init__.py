from source.main.controller.users import *
from source.main.controller.userPhotos import *
from source.main.controller.relationships import *
from source.main.controller.message import *
from source.main.controller.locations import *
from source.main.controller.forum import *
from source.main.controller.groups import *
from source.main.controller.provinces import*
from source.main.controller.postComments import *
from source.main.controller.images import *
from flask_jwt_extended import create_access_token, get_jwt_identity


def reader():
    return '<a href="/docs">/docs</a> to read the documentation'

def refresh_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return {'access_token': access_token}, 200

def refresh_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return {'access_token': access_token}, 200

def make_folder_user(id_user, PATH_IMAGE, image):
    if not os.path.isdir(PATH_IMAGE):
        os.makedirs(PATH_IMAGE)
    else:
        user_path = os.path.join(PATH_IMAGE, str(id_user))
        if not os.path.isdir(user_path):
            os.makedirs(user_path)
        else:
            image.save(os.path.join(user_path, image.filename))

    user_path = os.path.join(PATH_IMAGE, str(id_user))
    return send_from_directory(user_path, image.filename)
