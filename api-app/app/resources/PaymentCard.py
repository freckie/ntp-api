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

# GET, POST /payment/card
class VIEWCard(Resource):
    @jwt_required
    @cross_origin()
    def get(self):
        claims = get_jwt_claims()

        # Querying
        try:
            result = app.database.execute(text('''
                SELECT card_id, card_number, card_network, card_issuer, registered_at
                FROM card WHERE user_id= :id;
            '''),{
                'id': claims['id']
            }).fetchall()
        except Exception as exc:
            return error_response(500, str(exc))
        
        cards = []
        for row in result:
            cards.append({
                'card_id': row['card_id'],
                'card_number': row['card_number'],
                'card_network': row['card_network'],
                'card_issuer': row['card_issuer'],
                'registered_at': str(row['registered_at'])
            })
        return ok_response({
            'cards_count': len(cards),
            'cards': cards
        })

    @jwt_required
    @cross_origin()
    def post(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        # Handle body parameters
        try:
            card_number = request.json.get('card_number', None)
            card_network = request.json.get('card_network', None)
            card_issuer = request.json.get('card_issuer', None)
            if (not card_number) or (not card_network) or (not card_issuer):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))

        claims = get_jwt_claims()

        # Check permission of the card
        try:
            result = app.database.execute(text('''
                SELECT count(card_id) AS counts
                FROM card
                WHERE card_number= :card_number
                    AND card_network= :card_network
                    AND card_issuer= :card_issuer
            '''), {
                'card_number': card_number,
                'card_issuer': card_issuer,
                'card_network': card_network
            }).fetchone()
            if int(result['counts']) == 1:
                return error_response(500, '이미 등록된 카드 정보입니다.')
        except Exception as exc:
            return error_response(500, str(exc))

        # Querying
        try:
            app.database.execute(text('''
                INSERT INTO card
                    (card_number, card_network, card_issuer, user_id)
                    VALUES (:card_number, :card_network, :card_issuer, :user_id)
            '''), {
                'card_number': card_number,
                'card_issuer': card_issuer,
                'card_network': card_network,
                'user_id': claims['id']
            })
        except Exception as exc:
            return error_response(500, str(exc))

        return ok_response(None)

# PUT /payment/card/<card_id>
class PUTCard(Resource):
    @jwt_required
    @cross_origin()
    def put(self, card_id):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        # Handle body parameters
        try:
            card_number = request.json.get('card_number', None)
            card_network = request.json.get('card_network', None)
            card_issuer = request.json.get('card_issuer', None)
            if (not card_number) or (not card_network) or (not card_issuer):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))

        claims = get_jwt_claims()

        # Check permission of the card
        try:
            result = app.database.execute(text('''
                SELECT count(card_id) AS counts, user_id
                FROM card
                WHERE card_id= :card_id;
            '''), {
                'card_id': card_id
            }).fetchone()
            if int(result['counts']) == 0:
                return error_response(404, '존재하지 않는 결제 수단입니다.')
            if str(result['user_id']) != str(claims['id']):
                return error_response(403, '해당 결제 수단에 접근할 권한이 없습니다.')
        except Exception as exc:
            return error_response(500, str(exc))

        # Querying
        try:
            app.database.execute(text('''
                UPDATE card SET
                    card_number= :card_number, card_issuer= :card_issuer, card_network= :card_network
                    WHERE card_id= :card_id
            '''), {
                'card_number': card_number,
                'card_issuer': card_issuer,
                'card_network': card_network,
                'card_id': card_id
            })
        except Exception as exc:
            return error_response(500, str(exc))

        return ok_response(None)
    
    def delete(self, card_id):
        claims = get_jwt_claims()

        # Check permission of the card
        try:
            result = app.database.execute(text('''
                SELECT count(card_id) AS counts, user_id
                FROM card
                WHERE card_id= :card_id;
            '''), {
                'card_id': card_id
            }).fetchone()
            if int(result['counts']) == 0:
                return error_response(404, '존재하지 않는 결제 수단입니다.')
            if str(result['user_id']) != str(claims['id']):
                return error_response(403, '해당 결제 수단에 접근할 권한이 없습니다.')
        except Exception as exc:
            return error_response(500, str(exc))

        # Querying
        try:
            app.database.execute(text('''
                DELETE FROM card WHERE card_id= :card_id;
            '''), {
                'card_id': card_id
            })
        except Exception as exc:
            return error_response(500, str(exc))

        return ok_response(None)
