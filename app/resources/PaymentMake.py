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

# POST /payment/make
class POSTMake(Resource):
    @jwt_required
    @cross_origin()
    def post(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        # Handle body parameters
        try:
            price = request.json.get('price', None)
            if (not price):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))

        claims = get_jwt_claims()

        # Querying
        try:
            result = app.database.execute(text('''
                SELECT u.user_credit, c.card_id
                FROM user AS u, card AS c
                WHERE u.user_id= :id
                    AND c.user_id= :id;
            '''), {
                'id': claims['id']
            }).fetchone()
        except Exception as exc:
            return error_response(500, str(exc))
        
        remaining_credit = result['user_credit']
        if price <= 0:
            return error_response(400, '결제할 금액은 0원 이하가 될 수 없습니다.')
        price = abs(price)
        if price > remaining_credit:
            return error_response(500, '크레딧이 부족합니다.')

        # Querying (make transaction)
        try:
            app.database.execute(text('''
                INSERT INTO
                    transaction (card_id, credit_diff, transaction_type)
                    VALUES (:card_id, :credit_diff, :new_type);
            '''),{
                'card_id': result['card_id'],
                'credit_diff': -1 * price,
                'new_type': 'PAYMENT',
            })
        except Exception as exc:
            return error_response(500, str(exc))

        # Querying
        try:
            app.database.execute(text('''
                UPDATE user
                SET user_credit = user_credit - :amount
                WHERE user_id= :id;
            '''), {
                'id': claims['id'],
                'amount': int(price)
            })
        except Exception as exc:
            return error_response(500, str(exc))
        
        return ok_response(None)
