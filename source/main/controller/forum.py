from source import app
from source.main.function.forum import *


#Add new post
app.add_url_rule('/api/forum/add_post/<int:id>', methods=['POST'], view_func=addNewPost)

#View Post
app.add_url_rule('/api/forum/view_post/<int:id>', methods=['GET'], view_func=viewPost)

#Get list post
app.add_url_rule('/api/forum/group/<int:GroupID>/<int:PostFrom>/<int:PostTo>/<int:UserID>', methods=['GET'], view_func=getListPost)

#Update Post
app.add_url_rule('/api/forum/update_post/<int:PostID>', methods=['PATCH'], view_func=updatePost)

#Remove Post
app.add_url_rule('/api/forum/delete_post/<int:PostID>', methods=['DELETE'], view_func=deletePost)

#search post
app.add_url_rule('/api/forum/search/<string:key>', methods=['GET'], view_func=searchPost)

#favorite post
app.add_url_rule('/api/forum/favorite/<int:UserID>/<int:PostID>', methods=['POST'], view_func=favoritePost)