from os import environ
from OnlineVoting import app
import argparse
import logging


def configure_log(log_filename):
    logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')


if __name__ == '__main__':
    configure_log('errors.log')
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')

    args = parser.parse_args()
    PORT = 11234
    try:
        app.run(host=args.host, port=PORT)
    except Exception as x:
        logging.exception(x)
