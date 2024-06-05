from flask import jsonify, request, make_response
from source import db
from source.main.model.relationships import Relationships
from source.main.model.users import Users
from flask_mail import *
from datetime import datetime

def relationship(id):
    pass


def setRelationship(id):
    try: 
        data_json = request.json

        relationship = Relationships(
            UserID=id,
            RelatedUserID=data_json['RelatedUserID'],
            RelationshipType=data_json['RelationshipType'],
            CreateTime=datetime.now()
        )

        db.session.add(relationship)
        db.session.commit() 
        
        return {
            'UserID':id,
            'RelatedUserID':data_json['RelatedUserID'],
            'RelationshipType':data_json['RelationshipType'],
            'CreateTime':datetime.now()
        }
                
    except Exception as e:
        print(e)
        return make_response(jsonify({'status': 500, 'message': 'An error occurred'}), 500)