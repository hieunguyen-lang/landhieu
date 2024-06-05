from source import app
from source.main.function.groups import *

#view a group 
app.add_url_rule('/api/forum/group/<int:GroupID>', methods=['GET'], view_func=singleGroup)

#view all group 
app.add_url_rule('/api/forum/group/all_group', methods=['GET'], view_func=allGroup)

#add group
app.add_url_rule('/api/forum/group/add_group/<int:id>', methods=['POST'], view_func=addGroup)

#change group name
app.add_url_rule('/api/forum/group/update_group/<int:GroupID>', methods=['PATCH'], view_func=updateGroup)

#delete group
app.add_url_rule('/api/forum/group/remove_group/<int:GroupID>', methods=['DELETE'], view_func=removeGroup)

#count post on group
app.add_url_rule('/api/forum/group/count_group', methods=['GET'], view_func=countGroup)

#search post on group
app.add_url_rule('/api/forum/group/search/<int:GroupID>/<string:key>', methods=['GET'], view_func=searchPostInGroup)

#change group image
app.add_url_rule('/api/forum/group/groupImg/<int:GroupID>', methods=['PATCH'], view_func=changeImgGroup)