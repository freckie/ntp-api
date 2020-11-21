# API
from flask_restful import Api

def build_api(app):
    api = Api()

    # api.add_resource(DELETEReservations, '/api/reservations/<reservation_id>')

    api.init_app(app)
    return api