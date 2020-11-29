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
import json
from websocket import create_connection

# POST, PUT /user/face
class VIEWFace(Resource):
    @jwt_required
    @cross_origin()
    def post(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        claims = get_jwt_claims()

        # Handle body parameters
        try:
            face = request.json.get('face', None)
            if (not face):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))
        
        # Send to websocket server
        payload = json.dumps({
            'action': 'register',
            'user_id': claims['id'],
            'image': face
        })
        ws_url = 'ws://{}:{}'.format(app.config['WEBSOCKET_SERVER']['server_name'], app.config['WEBSOCKET_SERVER']['port'])
        ws = create_connection(ws_url)
        ws.send(payload)
        resp = ws.recv()
        ws.close()
        
        return ok_response(resp)
    
    @jwt_required
    @cross_origin()
    def put(self):
        if not request.is_json:
            return error_response(400, 'JSON 형식으로 전달해주세요.')

        claims = get_jwt_claims()

        # Handle body parameters
        try:
            face = request.json.get('face', None)
            if (not face):
                return error_response(400, '파라미터가 부족합니다.')
        except Exception as exc:
            return error_response(400, 'JSON 파싱 에러가 발생했습니다 : ' + str(exc))
        
        # Send to websocket server
        payload = json.dumps({
            'action': 'register',
            'user_id': claims['id'],
            'image': face
        })
        ws_url = 'ws://{}:{}'.format(app.config['WEBSOCKET_SERVER']['server_name'], app.config['WEBSOCKET_SERVER']['port'])
        ws = create_connection(ws_url)
        ws.send(payload)
        resp = ws.recv()
        ws.close()
        
        return ok_response(resp)
    