from source import app
from source.main.function.postComments import *

#get all comment
app.add_url_rule('/api/forum/comment/<int:PostID>/<int:UserID>', methods=['GET'], view_func=getAllComment)

#add comment
app.add_url_rule('/api/forum/add_comment/<int:UserID>/<int:PostID>', methods=['POST'], view_func=addComment)

#favorite or unfavorite comment
app.add_url_rule('/api/forum/comment/favorite/<int:UserID>/<int:CommentID>', methods=['POST'], view_func=favoriteComment)

#remove comment
app.add_url_rule('/api/forum/comment/remove_imgcomment/<int:CommentID>', methods=['DELETE'], view_func=removeImageComment)

#remove favorite comment
app.add_url_rule('/api/forum/comment/remove_favorite/<int:CommentID>', methods=['DELETE'], view_func=removeFavoriteComment)

#remove comment
app.add_url_rule('/api/forum/comment/remove/<int:CommentID>', methods=['DELETE'], view_func=removeComment)

#remove all comment in a Post
app.add_url_rule('/api/forum/comment/remove_all_comment/<int:PostID>', methods=['DELETE'], view_func=removeAllComment)