from source import app
from source.main.function.relationships import *


#Check relationship
app.add_url_rule('/api/profile/relationship/<id>', methods=['GET'], view_func=relationship)

#Set Relationship
app.add_url_rule('/api/profile/setRelationship/<id>', methods=['POST'], view_func=setRelationship)
