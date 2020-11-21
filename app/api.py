# API
from flask_restful import Api
from app.resources.UserSignup import POSTSignup
from app.resources.UserLogin import POSTLogin

def build_api(app):
    api = Api()

    # 유저 관련
    api.add_resource(POSTSignup, '/api/user/signup')
    api.add_resource(POSTLogin, '/api/user/login')

    api.init_app(app)
    return api