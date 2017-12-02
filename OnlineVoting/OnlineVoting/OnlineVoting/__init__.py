
# https://trello.com/app-key

from flask import Flask
app = Flask(__name__)

import OnlineVoting.views
import OnlineVoting.auth
import OnlineVoting.trello
import OnlineVoting.database