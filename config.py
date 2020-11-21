db = {
    'user'     : '',
    'password' : '',
    'host'     : '',
    'port'     : 3306,
    'database' : 'r'
}
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
