def ok_response(data):
    return {
        'status': 200,
        'message': 'success',
        'data': data
    }, 200

def error_response(status, msg):
    return {
        'status': int(status),
        'message': msg,
        'data': None
    }, int(status)
