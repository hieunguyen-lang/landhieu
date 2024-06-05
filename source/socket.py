import base64
from flask_socketio import SocketIO
from flask_socketio import emit, join_room, leave_room
from flask import request
from source.main.extend import *
from source import socketIo, db, connected_clients
from source.main.model.messages import Messages
from source.main.model.relationships import Relationships
from source.main.model.users import Users
from datetime import datetime, timedelta,timezone
from sqlalchemy import and_, text
import smtplib
import eventlet


connected_user = {}

@socketIo.on("online")
def online(data):
    onlineUser = []
    for obj in connected_user.keys():
        onlineUser.append(int(obj))
    emit("online", {"user": onlineUser}, room = request.sid)

    


@socketIo.on("offline")
def offline(data):
    for userId, sid in connected_user.items():
        if request.sid == sid:
            item = connected_user.pop(userId)
            emit("offline", {"userOffline": userId}, broadcast=True)
            break
    print("User disconnected")



@socketIo.on('connect')
def connected(data):
    try:
        # userID = data['userId']
        # user = Users.query.filter_by(UserID=userID).first()
        # if user:
        #     connected_user[userID] = request.sid
            emit("connected", {"message": "Connected Sucessfully"})
        # else:
        #     emit("connected", {"message": "User doesn't exit"})
    except Exception as e:
        emit("connected", {"message": "Error"})


@socketIo.on("userId")
def connected(data):
    try:
        userID = data['userId']
        user = Users.query.filter_by(UserID=userID).first()
        onlineUser = []
        if user:
            connected_user[userID] = request.sid
            emit("userId", {"message": "Connected Sucessfully"})
            for obj in connected_user.keys():
                onlineUser.append(int(obj))
            emit("online", {"user": onlineUser}, room = request.sid)
        else:
            emit("userId", {"message": "User doesn't exit"})
            
    except Exception as e:
        print(e)
    
    


@socketIo.on("disconnect")
def disconnected():
    for userId, sid in connected_user.items():
        if request.sid == sid:
            item = connected_user.pop(userId)
            emit("offline", {"userOffline": userId}, broadcast=True)
            break
    print("User disconnected")


@socketIo.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)
    print("join")


@socketIo.on("leave")
def on_leave(data):
    room = data["room"]
    leave_room(room)
    print("leave")


@socketIo.on("chat_group")
def chat_group(data):
    room = data["room"]
    message = data["data"]
    print(message, data)
    newChat = Chats(
        idGroup=room,
        sendAt=datetime.strptime(message["sendAt"], "%d/%m/%Y %H:%M %p %z"),
        idSend=message["idSend"],
        type=message["type"],
    )
    if (
        newChat.type == "image"
        or newChat.type == "icon-image"
        or newChat.type == "muti-image"
    ):
        newChat.image = message["metaData"]
    else:
        newChat.text = message["content"]
    db.session.add(newChat)
    db.session.commit()
    message["sendAt"] = str(newChat.sendAt)
    # Lấy thời gian hiện tại
    emit("chat_group", message, room=room)


# chat 1vs1


@socketIo.on("join_room")
def handle_join_room(data):
    room = data["room"]
    join_room(room)
    print(" ")
    # Truy vấn tin nhắn từ cơ sở dữ liệu và gửi chúng đến người dùng
    messages = Messages.query.filter(
        (Messages.idSend == room) | (Messages.idReceive == room)
    ).all()
    for message in messages:
        emit("message", {"sender": message.sender, "content": message.content})


# @socketIo.on("private message", ({ content, to }) => {
#   socket.to(to).emit("private message", {
#     content,
#     from: socket.id,
#   });
# });


@socketIo.on("check_message")
def handle_check_message(data: Messages):
    if data.ReceiverID in connected_user:
        emit("check_message", {"senderID": data.SenderID, "content": data.Content}, room = connected_user[data.ReceiverID])


# @socketIo.on("send_message")
# def handle_send_message(data):
#     print("SON____send_message")
#     try:
#         room = data["room"]
#         message = data["data"]
#         print("PHANROOM____" + room)
#         print("PHAN_MESSAGE____" + message)
#         print(message, data)
#         user1 = Relationships.query.filter(
#             (Relationships.idSend == message["idSend"])
#             & (Relationships.idReceive == message["idReceive"])
#         ).first()
#         user2 = Relationships.query.filter(
#             (Relationships.idReceive == message["idSend"])
#             & (Relationships.idSend == message["idReceive"])
#         ).first()
#         if user1.relation == True and user2.relation == True:
#             newChat = Messages(
#                 sendAt=datetime.now().strftime("%Y-%m-%d %H:%M:%S %z"),
#                 idSend=message["idSend"],
#                 idReceive=message["idReceive"],
#                 room=room,
#                 type=message["type"],
#             )
#             if (
#                 newChat.type == "image"
#                 or newChat.type == "icon-image"
#                 or newChat.type == "muti-image"
#             ):
#                 newChat.img = message["data"]
#             else:
#                 newChat.text = message["content"]

#             db.session.add(newChat)
#             db.session.commit()

#             emit("send_message", message, room=room)
#             eventlet.sleep(900)
#             pushemail(newChat.id)
#             # scheduler.add_job(pushemail, 'interval', minutes=1, newChat.id)

#         else:
#             print("you are banned from chatting")
#             emit("send_message", f"you are banned from chatting", room=room)
#         # ,state=message["state"]
#     except Exception as e:
#         # Log the error message
#         print("SQL Error:", str(e))

@socketIo.on("send_message")
def handle_send_message(data):
    try:
        user1 = Relationships.query.filter(and_
            (Relationships.UserID == data["idSend"], Relationships.RelatedUserID == data["idReceive"])
        ).with_entities(Relationships.RelationshipType).first()
        user2 = Relationships.query.filter(and_
            (Relationships.RelatedUserID == data["idSend"], Relationships.UserID == data["idReceive"])
        ).with_entities(Relationships.RelationshipType).first()

        if user1 and user1[0] == 'block' or user2 and user2[0] == 'block':
            emit("send_message", {"message": "You have been blocked"})
        else:

            message_time = datetime.now()
            if data.get("Image"):
                image = base64.b64decode(data.get("Image"))
            else: 
                image = None
            newmessage = Messages()
            if data["idReceive"]:
                newmessage = Messages(SenderID=data["idSend"], ReceiverID=data["idReceive"], 
                                    Content=data["content"], MessageTime=message_time)
            if image:
                newmessage.Image = image
            chat_parse = {}
            db.session.add(newmessage)
            db.session.commit()
            chat_parse["MessageID"] = newmessage.MessageID
            chat_parse["SenderID"] = newmessage.SenderID
            chat_parse["ReceiverID"] = newmessage.ReceiverID
            chat_parse["Content"] = newmessage.Content
            chat_parse["MessageTime"] = datetime.strftime(newmessage.MessageTime, "%d/%m/%Y %H:%M %p %z")
            chat_parse["IsSeen"] = newmessage.IsSeen
            chat_parse["Image"] = data.get("Image")
            
            if newmessage.ReceiverID in connected_user:
                emit("check_message", {"data": chat_parse}, room = connected_user[newmessage.ReceiverID])
                emit("send_message", {"message": "Send sucessfully"})
            else:
                emit("send_message", {"message": "User doesn't online"})

    except Exception as e:
        emit("send_message", {"message": "Error"})
        print(e)

@socketIo.on("seen")
def handle_seen(data):
    try:
        messageId = data["MessageID"]
        message = Messages.query.filter_by(
            MessageID = messageId
        ).first()
        if message: 
            message.IsSeen = 1
        db.session.commit()
        
        chat_parse = {}
        chat_parse["MessageID"] = message.MessageID
        chat_parse["SenderID"] = message.SenderID
        chat_parse["ReceiverID"] = message.ReceiverID
        chat_parse["Content"] = message.Content
        chat_parse["MessageTime"] = datetime.strftime(message.MessageTime, "%d/%m/%Y %H:%M %p %z")
        chat_parse["IsSeen"] = message.IsSeen
        chat_parse["Image"] = message.Image
        if message.Image:

            chat_parse["Image"] = byteToString(message.Image)
        else:
            chat_parse["Image"] = None
        if message.SenderID in connected_user:
            emit("seen", {"data": chat_parse}, room = connected_user[message.SenderID])            
        emit("seen", {"message": "Sucessfully", "data": chat_parse}, room = connected_user[message.ReceiverID])
        

    except Exception as e:
        print(e)    