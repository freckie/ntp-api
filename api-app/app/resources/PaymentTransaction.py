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

# GET /payment/transaction
class GETTransaction(Resource):
    @jwt_required
    @cross_origin()
    def get(self):
        claims = get_jwt_claims()

        # Querying
        try:
            result = app.database.execute(text('''
                SELECT transaction_id, transaction_type, user_id, price, location_id, timestamp
                FROM transaction 
                WHERE user_id= :id
                ORDER BY transaction_id DESC;
            '''),{
                'id': claims['id']
            }).fetchall()
        except Exception as exc:
            return error_response(500, str(exc))
        
        transactions = []
        for row in result:
            transactions.append({
                'transaction_id': row['transaction_id'],
                'transaction_type': row['transaction_type'],
                'user_id': row['user_id'],
                'price': row['price'],
                'location_id': row['location_id'],
                'timestamp': str(row['timestamp'])
            })

        return ok_response({
            'transactions_count': len(transactions),
            'transactions': transactions
        })

# POST /payment/transaction/<transaction_id>/refund
class POSTRefund(Resource):
    @jwt_required
    @cross_origin()
    def post(self, transaction_id):
        claims = get_jwt_claims()

        # Get transaction
        try:
            result = app.database.execute(text('''
                SELECT count(t.transaction_id) AS counts, t.transaction_type, c.user_id, t.credit_diff, t.card_id
                FROM transaction AS t, card AS c
                WHERE t.card_id=c.card_id
                    AND t.transaction_id= :tid;
            '''), {
                'tid': transaction_id
            }).fetchone()
            if int(result['counts']) == 0:
                return error_response(404, '해당 트랜잭션이 존재하지 않습니다.')
            if result['transaction_type'] != 'PAYMENT':
                return error_response(500, '환불이 불가능한 트랜잭션입니다.')
            if str(result['user_id']) != str(claims['id']):
                return error_response(403, '해당 트랜잭션에 접근할 권한이 부족합니다.')
        except Exception as exc:
            return error_response(500, str(exc))

        credit = abs(int(result['credit_diff']))
        card_id = int(result['card_id'])

        # Querying
        try:
            app.database.execute(text('''
                UPDATE transaction
                SET transaction_type= :type
                WHERE transaction_id= :tid;
            '''),{
                'type': 'COMPLETE',
                'tid': transaction_id
            })
        except Exception as exc:
            return error_response(500, str(exc))

        # Querying
        try:
            app.database.execute(text('''
                INSERT INTO
                    transaction (card_id, credit_diff, transaction_type)
                    VALUES (:card_id, :credit_diff, :new_type);
            '''),{
                'card_id': card_id,
                'credit_diff': credit,
                'new_type': 'REFUND',
            })
        except Exception as exc:
            return error_response(500, str(exc))

        # Querying
        try:
            app.database.execute(text('''
                UPDATE user
                SET user_credit=user_credit+ :credit_diff
                WHERE user_id= :uid;
            '''),{
                'credit_diff': credit,
                'uid': claims['id']
            })
        except Exception as exc:
            return error_response(500, str(exc))

        return ok_response(None)
