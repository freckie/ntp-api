# API
from flask_restful import Api
from app.resources.UserSignup import POSTSignup
from app.resources.UserLogin import POSTLogin
from app.resources.UserDropout import POSTDropout
from app.resources.UserDuplicate import GETDuplicate

from app.resources.PaymentCredit import VIEWCredit
from app.resources.PaymentCard import VIEWCard, PUTCard

def build_api(app):
    api = Api()

    # 유저 관련
    api.add_resource(POSTSignup, '/api/user/signup')
    api.add_resource(POSTLogin, '/api/user/login')
    api.add_resource(POSTDropout, '/api/user/dropout')
    api.add_resource(GETDuplicate, '/api/user/duplicate')

    api.add_resource(VIEWCredit, '/api/payment/credit')
    api.add_resource(VIEWCard, '/api/payment/card')
    api.add_resource(PUTCard, '/api/payment/card/<card_id>')

    api.init_app(app)
    return api