from source import db
from flask import request, make_response, jsonify
from source.main.model.chat1vs1 import Chat1vs1
from source.main.model.relationship import Relationship
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.sql import label, text


def chat1vs1(id):
    if request.method == "GET":
        try:
            chat = db.session.execute(
                text(
                    "Select * from users inner join chat1vs1 on users.id= chat1vs1.idReceive"
                )
            )
            data = []
            for row in chat:
                view_chat = {}
                view_chat["idSend"] = row.idSend
                view_chat["idReceive"] = row.idReceive
                view_chat["name"] = row.name
                view_chat["text"] = row.text
                view_chat["state"] = row.state
                view_chat["sendAt"] = row.sendAt
                data.append(view_chat)
            return {"state": 200, "data": data}
        except Exception as e:
            print(e)
            return make_response(jsonify({"status": 400, "message": str(e)}), 400)
    if request.method == "POST":
        json = request.json
        print(json)
        print(json["sendAt"])
        try:
            sentAt_time = datetime.strptime(json["sendAt"], "%d/%m/%Y %H:%M %p %z")
            print(json["content"])
            newchat1vs1 = Chat1vs1(
                sendAt=sentAt_time, idReceive=id, text=json["content"]
            )
            print("loi o ghep su kien")
            if json["idSend"]:
                newchat1vs1.idSend = json["idSend"]
            db.session.add(newchat1vs1)
            db.session.commit()
            chat_parse = {}
            chat_parse["id"] = newchat1vs1.id
            chat_parse["idSend"] = newchat1vs1.idSend
            chat_parse["idReceive"] = newchat1vs1.idReceive
            chat_parse["content"] = newchat1vs1.text
            chat_parse["sendAt"] = str(newchat1vs1.sendAt)
            return {"status": 200, "message": chat_parse}
        except:
            return make_response(
                jsonify(
                    {"status": 300, "message": "Sonpipi Request fail. Please try again"}
                ),
                300,
            )
    if request.method == "DELETE":
        pass