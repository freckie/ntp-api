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

# POST /user/login
class POSTLogin(Resource):
    @cross_origin()
    def post(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        # Handle body parameters
        try:
            pw = request.json.get('pw', None)
            email = request.json.get('email', None)
            if (not pw) or (not email):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))

        # Querying
        try:
            result = app.database.execute(text('''
                SELECT count(user_email) AS counts, user_name, user_email, user_pw, user_id
                FROM user WHERE user_email= :email
            '''),{
                'email' : email,
            }).fetchone()
            if int(result['counts']) == 0:
                return error_response(401, '이메일이 잘못되었습니다.')
        except Exception as exc:
            return error_response(500, str(exc))

        # Compare the password
        try:
            if not bcrypt.checkpw(pw.encode('utf-8'), result['user_pw'].encode('utf-8')):
                return error_response(401, '비밀번호가 잘못되었습니다.')
        except Exception as exc:
            return error_response(401, '비밀번호가 잘못되었습니다 : ' + str(exc))

        user_claims = {
            'id': result['user_id'],
            'email': result['user_email'],
            'name': result['user_name']
        }
        access_token = create_access_token(
            identity=email,
            expires_delta=timedelta(hours=24),
            user_claims=user_claims
        )
        refresh_token = create_refresh_token(
            identity=email,
            user_claims=user_claims
        )

        return ok_response({
            'access_token': access_token,
            'refresh_token': refresh_token
        })

        return ok_response(None)