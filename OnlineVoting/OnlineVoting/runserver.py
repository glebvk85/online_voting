from os import environ
from OnlineVoting import app
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')

    args = parser.parse_args()
    PORT = 11234
    app.run(host=args.host, port=PORT, threaded=True)
