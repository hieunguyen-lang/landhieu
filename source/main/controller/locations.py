from source import app
from source.main.function.locations import *

#set current location
app.add_url_rule('/api/location/current_location/<id>', methods=['PATCH'], view_func=setCurrentLocation)

#caculate distance between 2 user
app.add_url_rule('/api/location/distance/<int:UserID1>/<int:UserID2>', methods=['GET'], view_func=calculateDistance)

#Count user in radius
app.add_url_rule('/api/location/count/<int:UserID>/<int:radius>', methods=['GET'], view_func=countUserInRadius)

#caculate distance in radius
app.add_url_rule('/api/location/<int:UserID>/<int:radius>', methods=['GET'], view_func=calculateDistanceInRadius)

