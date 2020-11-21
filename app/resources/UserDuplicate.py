import bcrypt
from datetime import timedelta
from flask_restful import Resource, reqparse, request
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_claims,
    create_refresh_token, jwt_refresh_token_required
)
from flask_cors import cross_origin
from app.models.response import error_response, ok_response
from flask import current_app as app
from sqlalchemy import text

# GET /user/duplicate
class GETDuplicate(Resource):
    @cross_origin()
    def post(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        # Handle body parameters
        try:
            email = request.json.get('email', None)
            if (not email):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))

        # Querying
        try:
            result = app.database.execute(text('''
                SELECT count(user_email) AS count
                FROM user WHERE user_email= :email
            '''),{
                'email' : email
            })
        except Exception as exc:
            return error_response(500, str(exc))
        
        if result['count'] == 0:
            return ok_response({'available': True})
        else:
            return ok_response({'available': False})
