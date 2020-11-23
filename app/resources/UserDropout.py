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

# POST /user/dropout
class POSTDropout(Resource):
    @jwt_required
    @cross_origin()
    def post(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        claims = get_jwt_claims()

        # Handle body parameters
        try:
            pw = request.json.get('pw', None)
            if (not pw):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))

        # Querying
        try:
            result = app.database.execute(text('''
                SELECT count(user_email) AS counts, user_email, user_pw
                FROM user WHERE user_id= :id
            '''),{
                'id': claims['id']
            }).fetchone()
            if int(result['counts']) == 0:
                return error_response(500, '존재하지 않는 ID입니다.')
        except Exception as exc:
            return error_response(500, str(exc))

        # Compare the password
        try:
            if not bcrypt.checkpw(pw.encode('utf-8'), result['user_pw'].encode('utf-8')):
                return error_response(401, '비밀번호가 잘못되었습니다.')
        except Exception as exc:
            return error_response(401, '비밀번호가 잘못되었습니다 : ' + str(exc))

        # Dropout the account
        result = app.database.execute(text('''
            DELETE FROM user WHERE user_email= :email
        '''), {
            'email': claims['email']
        })
        print(result)
            
        return ok_response(None)