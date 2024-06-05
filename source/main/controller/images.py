from source import app
from source.main.function.images import *

#Upload anh
app.add_url_rule('/api/upload_image/<id_user>', methods=['POST'], view_func=uploadImage)
#Xem anh
app.add_url_rule('/get_image/<string:id_user>/<string:file_name>', methods=["GET"], view_func=view_image)