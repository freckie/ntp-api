# API
from flask_restful import Api
from app.resources.UserSignup import POSTSignup
from app.resources.UserLogin import POSTLogin
from app.resources.UserDropout import POSTDropout
from app.resources.UserDuplicate import GETDuplicate

def build_api(app):
    api = Api()

    # 유저 관련
    api.add_resource(POSTSignup, '/api/user/signup')
    api.add_resource(POSTLogin, '/api/user/login')
    api.add_resource(POSTDropout, '/api/user/dropout')
    api.add_resource(GETDuplicate, '/api/user/duplicate')

    api.init_app(app)
    return api