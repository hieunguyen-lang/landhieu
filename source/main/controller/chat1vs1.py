from source import app

from source.main.function.chat1vs1 import *

app.add_url_rule('/chat/<string:id>',
                 methods=['GET', 'POST', "PATCH", "DELETE"], view_func=chat1vs1)
# relationship  chat
#id User
app.add_url_rule('/chatblock/<string:id>',
                 methods=['GET', 'POST', 'PATCH'], view_func=blockchat)
#change state message
#id message
app.add_url_rule('/message/<string:id>',
                 methods=['GET', 'POST', 'PATCH'], view_func=statemessage)
