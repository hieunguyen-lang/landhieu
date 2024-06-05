from flask import request
import os.path
from urllib.parse import urlparse
import random

def make_link(localhost, path):
    url = f"{localhost}{path}"
    return url
def split_join(url):
    url = url.split('/')
    url = '/'.join(url[:3])
    return url
def make_url_image(id_user, path, image, typeof):
    local_host = split_join(request.base_url)
    random_name = f"{id_user}_{typeof}_{random.randint(100000, 999999)}.jpg"
    image_link = f"/get_image/{id_user}/{random_name}"
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        user_path = os.path.join(path, str(id_user))
        if not os.path.isdir(user_path):
            os.makedirs(user_path)
            image.save(os.path.join(user_path, random_name))
        else:
            image.save(os.path.join(user_path, random_name))
    print(make_link(local_host, image_link))
    return make_link(local_host, image_link)