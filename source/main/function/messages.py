from source import db
from flask import request, make_response, jsonify
import base64
# from source.main.model.relationship import Relationship
from source.main.extend import *
from source.main.model.messages import Messages
from source.main.model.relationships import Relationships
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.sql import label, text
from flask_socketio import SocketIO
from source.socket import *

def messages(id):
    if request.method == "GET":
        try:
            chat = db.session.execute(
                text(
                    f"""
                    SELECT *
                    FROM Users
                    INNER JOIN Messages ON Messages.SenderID = {id} OR Messages.ReceiverID = {id}
                    WHERE Users.UserID = {id}
                    ORDER BY Messages.MessageTime DESC;
                    """
                )
            )
            data = []
            checked = []
            for row in chat:
                view_chat = {}
                other_userId = row.SenderID
                if int(row.SenderID) == int(id):
                    other_userId = row.ReceiverID

                user = db.session.execute(
                    text(
                        f"""
                        SELECT *
                        From Users Where Users.UserID = {other_userId}
                        LIMIT 1
                        """
                    )
                )
                item = Users
                for row2 in user:
                    item = row2
                if other_userId not in checked:
                    view_chat["UserID"] = row.UserID
                    view_chat["OtherUserID"] = other_userId

                    view_chat["Username"] = row.Username
                    view_chat["OtherUsername"] = item.Username

                    view_chat["OtherFullname"] = item.FullName

                    view_chat["Email"] = row.Email
                    view_chat["OtherEmail"] = item.Email
                   
                    view_chat["Avatar"] = byteToString(row.avatarLink)
                    view_chat["OtherAvatar"] = byteToString(item.avatarLink)
                
                    view_chat["OtherLastActivityTime"] = item.LastActivityTime
                  
                    view_chat["MessageID"] = row.MessageID

                    view_chat["SenderID"] = row.SenderID
                    view_chat["ReceiverID"] = row.ReceiverID

                    view_chat["Content"] = row.Content

                    view_chat["MessageTime"] = row.MessageTime
                    view_chat["IsSeen"] = row.IsSeen
                    if row.Image:
                        # binary_string = row.Image

                        # binary_bytes = int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, byteorder='big')

                   
                        view_chat["Image"] = byteToString(row.Image)
                    else:
                        view_chat["Image"] = None
                    checked.append(other_userId)
                    data.append(view_chat)
                else:
                    pass
            print(checked)
            print(data)
            return make_response(
                jsonify({"status": 200, "data": data}),
                200,
            )
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )
    if request.method == "POST":
        json = request.json
        try:
            message_time = datetime.strptime(
                json["MessageTime"], "%d/%m/%Y %H:%M %p %z"
            )
            newmessage = Messages()
            if json["idReceive"]:
                newmessage = Messages(SenderID=id, ReceiverID=json["idReceive"], 
                                       Content=json["content"], MessageTime=message_time)
            db.session.add(newmessage)
            db.session.commit()
            chat_parse = {}
            chat_parse["MessageID"] = newmessage.MessageID
            chat_parse["SenderID"] = newmessage.SenderID
            chat_parse["ReceiverID"] = newmessage.ReceiverID
            chat_parse["Content"] = newmessage.Content
            chat_parse["MessageTime"] = newmessage.MessageTime
            chat_parse["IsSeen"] = newmessage.IsSeen

            return make_response(
                jsonify({"status": 200, "message": chat_parse}),
                200,
            )
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 300, "message": "Request fail. Please try again"}),
                300,
            )
    if request.method == "DELETE":
        try:
            messageId = request.json["messageId"]
            messages = Messages.query.filter_by(MessageID=messageId).first()
            
            if messages:

                db.session.delete(messages)
                db.session.commit()

                return make_response(
                    jsonify(
                        {"status": 200, "message": "Delete success"}
                    ),
                    200,
                )
            else:
                return make_response(
                    jsonify(
                        {"status": 404, "message": "No messageID found"}
                    ),
                    404,
                )
        except Exception as e:
            print(e)
            return make_response(
                jsonify(
                    {"Error": str(e)}
                ), 400
            )



def blockchat(id):
    if request.method == "GET":
        try:
            chat = db.session.execute(
                text(
                    # 'Select * from Users inner join Relationships on users.id= relationship.idReceive'))
                    f"SELECT * FROM Users INNER JOIN Relationships ON Users.UserID = {id}"
                )
            )
            print(chat)
            data = []
            for row in chat:
                # view_chat = {}
                # view_chat["Relationships"] = row.idSend
                # view_chat["idReceive"] = row.idReceive
                # view_chat["relationship"] = row.relation
                # data.append(view_chat)
                view_chat = {}
                view_chat["Relationships"] = row.RelationshipID
                view_chat["RelatedUserID"] = row.RelatedUserID
                view_chat["RelationshipType"] = row.relation
                data.append(view_chat)
            return {"state": 200, "data": data}
        except Exception as e:
            print("-----" + str(e))
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )
    if request.method == "POST":
        json_data = request.json  # Get JSON data from the request
        try:
            # Try to find an existing relationship in the database based on certain conditions
            user1 = Relationships.query.filter(
                (Relationships.RelationshipID == id)
                & (Relationships.RelatedUserID == json_data["RelatedUserID"])
            ).first()
            user2 = Relationships.query.filter(
                (Relationships.RelatedUserID == id)
                & (Relationships.RelationshipID == json_data["RelatedUserID"])
            ).first()
            print("-----" + str(json_data))

            if user1 or user2:
                # If a relationship exists, return its status
                return {"status": 200, "relation is": user1.relation}
            else:
                # If no relationship exists, create a new one with relation set to True
                new_relation1 = Relationships(
                    RelationshipID=id,
                    RelatedUserID=json_data["RelatedUserID"],
                    relation=True,
                )
                new_relation2 = Relationships(
                    RelatedUserID=id,
                    RelationshipID=json_data["RelatedUserID"],
                    relation=True,
                )
                db.session.add(new_relation1)
                db.session.add(new_relation2)
                db.session.commit()

                # Prepare a response message
                chat_parse = {
                    "id": new_relation1.id,
                    "RelationshipID": new_relation1.RelationshipID,
                    "RelatedUserID": new_relation1.RelatedUserID,
                    "relation": new_relation1.relation,
                }

                # Return a JSON response with the newly created relationship data
                return {"status": 200, "message": chat_parse}

        except Exception as e:
            # Handle exceptions, e.g., database errors
            print(e)
            return make_response(
                jsonify(
                    {"status": 300, "message": "Sonpipi Request fail. Please try again"}
                ),
                300,
            )

    if request.method == "PATCH":
        json_data = request.json  # Get JSON data from the request
        try:
            # Try to find an existing relationship in the database based on certain conditions
            user = Relationships.query.filter(
                (Relationships.RelationshipID == id)
                & (Relationships.RelatedUserID == json_data["RelatedUserID"])
            ).first()
            if user:
                # If a relationship exists, return its status
                user.relation = json_data["relation"]
                db.session.commit()
                chat_parse = {
                    "id": user.RelationshipID,
                    "RelationshipID": user.RelationshipID,
                    "RelatedUserID": user.RelatedUserID,
                    "relation": user.relation,
                }
                print("-------" + str(json_data))
                return {"status": 200, "message": chat_parse}
            else:
                return {"status": 200, "message": "no relationship"}
        except Exception as e:
            # Handle exceptions, e.g., database errors
            print(e)
            return make_response(
                jsonify(
                    {"status": 300, "message": "Sonpipi Request fail. Please try again"}
                ),
                300,
            )

def pairmessage(id): 
    
    if request.method == "GET":
        try:
            other_userId = request.args.get('other_userId')
            chat = db.session.execute(
                text(
                    f"""
                    SELECT *
                    FROM Users
                    INNER JOIN Messages ON (Messages.SenderID = {id} AND Messages.ReceiverID = {other_userId}) 
                    OR (Messages.SenderID = {other_userId} AND Messages.ReceiverID = {id})
                    WHERE Users.UserID = {id}
                    ORDER BY Messages.MessageTime DESC;
                    """
                )
            )
            data = []
            for row in chat:
                view_chat = {}
                user = db.session.execute(
                    text(
                        f"""
                        SELECT *
                        From Users Where Users.UserID = {other_userId}
                        LIMIT 1
                        """
                    )
                )
                item = Users
                for row2 in user:
                    item = row2
                    view_chat["UserID"] = row.UserID
                    view_chat["OtherUserID"] = other_userId

                    view_chat["Username"] = row.Username
                    view_chat["OtherUsername"] = item.Username

                    view_chat["OtherFullName"] = item.FullName

                    view_chat["Email"] = row.Email
                    view_chat["OtherEmail"] = item.Email
                   
                    view_chat["Avatar"] = byteToString(row.avatarLink)
                    view_chat["OtherAvatar"] = byteToString(item.avatarLink)
                
                    view_chat["OtherLastActivityTime"] = item.LastActivityTime

                  
                    view_chat["MessageID"] = row.MessageID

                    view_chat["SenderID"] = row.SenderID
                    view_chat["ReceiverID"] = row.ReceiverID

                    view_chat["Content"] = row.Content

                    view_chat["MessageTime"] = row.MessageTime
                    view_chat["IsSeen"] = row.IsSeen
                    if row.Image:
                        # binary_string = row.Image

                        # binary_bytes = int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, byteorder='big')

                        view_chat["Image"] = byteToString(row.Image)
                    else:
                        view_chat["Image"] = None
                data.append(view_chat)
            print(data)
            return make_response(
                jsonify({"status": 200, "data": data}),
                200,
            )
        except UnicodeDecodeError:
            print("Error: Unable to decode data using UTF-8 encoding.")
        except base64.binascii.Error:
            print("Error: Invalid Base64 data.")
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )

def statemessage(id):
    try:
        if request.method == "POST":
            message = Messages.query.filter(Messages.id == id).first()
            message.state = "seen"
            db.session.commit()
            return "state message change 'seen'"
    except Exception as e:
        print(e)
        return make_response(
            jsonify({"status": 300, "message": "Request fail. Please try again"}), 300
        )

