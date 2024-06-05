from flask import jsonify, request, make_response
from source.main.model.provinces import Provinces
from source import db

def addProvince():
    try:
        data_json = request.json.get('provinces')
        
        if data_json and isinstance(data_json, list):
            for province_data in data_json:
                province_name = province_data.get('ProvinceName')

                if not province_name:
                    return make_response(jsonify({'Status': 400, 'message': 'ProvinceName is required in each province data!'}), 400)

                new_province = Provinces(ProvinceName=province_name)
                db.session.add(new_province)

            db.session.commit()
            return make_response(jsonify({'Status': 200, 'message': 'Provinces added successfully!'}), 200)
        else:
            return make_response(jsonify({'Status': 400, 'message': 'Invalid or missing data in the request!'}), 400)
    except Exception as e:
        print(e)
        return make_response(jsonify({'status': 500, 'message': 'An error occurred while adding provinces!'}), 500)
