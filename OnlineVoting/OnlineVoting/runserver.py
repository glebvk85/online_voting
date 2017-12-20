from os import environ
from OnlineVoting import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    PORT = 11234
    app.run(host='192.168.0.121', port=PORT, threaded=True)
