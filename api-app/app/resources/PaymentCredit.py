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

# GET, POST /payment/credit
class VIEWCredit(Resource):
    @jwt_required
    @cross_origin()
    def get(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        claims = get_jwt_claims()

        # Querying
        try:
            result = app.database.execute(text('''
                SELECT user_credit
                FROM user WHERE user_id= :=id;
            '''),{
                'id': claims['id']
            }).fetchone()
        except Exception as exc:
            return error_response(500, str(exc))
        
        return ok_response({'remaining_credit': int(result['user_credit'])})

    @jwt_required
    @cross_origin()
    def post(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        claims = get_jwt_claims()

        # Handle body parameters
        try:
            card_id = request.json.get('card_id', None)
            amount = request.json.get('amount', None)
            if (not card_id) or (not amount):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))
        
        if amount < 1000 or amount > 1000000:
            return error_response(400, '1회 충전 한도는 최소 1,000원, 최대 1,000,000원입니다.')

        # Check permission of the card
        try:
            result = app.database.execute(text('''
                SELECT count(card_id) AS counts
                FROM user AS u, card AS c
                WHERE c.user_id=u.user_id
                    AND u.user_id= :id
                    AND c.card_id= :card_id;
            '''), {
                'id': claims['id'],
                'card_id': card_id
            }).fetchone()
            if int(result['counts']) == 0:
                return error_response(403, '해당 결제 수단에 대한 접근 권한이 부족합니다.')
        except Exception as exc:
            return error_response(500, str(exc))

        # Querying
        try:
            app.database.execute(text('''
                UPDATE user SET user_credit=user_credit+ :amount WHERE user_id= :id;
            '''), {
                'id': claims['id'],
                'amount': amount
            })
        except Exception as exc:
            return error_response(500, str(exc))

        # Logging
        app.database.execute(text('''
            INSERT INTO
                transaction (card_id, credit_diff, transaction_type)
                VALUES (:card_id, :amount, :type);
        '''), {
            'card_id': card_id,
            'amount': amount,
            'type': 'CHARGE'
        })

        return ok_response(None)