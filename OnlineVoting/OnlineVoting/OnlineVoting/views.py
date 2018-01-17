
from datetime import datetime
from OnlineVoting.auth import make_authorization_url
from flask import render_template, make_response, request, redirect, url_for
from OnlineVoting import app
from OnlineVoting.trello import TrelloProvider
from OnlineVoting.blockchain import extractContract, VotingContract, DataBaseSystem
from OnlineVoting.processing import processVoting

@app.route('/')
@app.route('/home')
def home():
    token = request.cookies.get('token')
    is_auth = token is not None

    trello = TrelloProvider()
    if is_auth:
        trello.auth(token)

    returnUrl = request.base_url
    db = DataBaseSystem()
    incoming_cards = None
    if is_auth:
        incoming_cards = db.sync_new_lectures(trello.getIncomingCards())

    return render_template(
        'index.html',
        header = 'Голосуем за темы на обучение с учетом их актуальности для решения тактических и стратегических вопросов в команде.',
        year=datetime.now().year,
        auth_url = make_authorization_url(returnUrl),
        is_auth = is_auth,
        cards = incoming_cards,
        user = trello.getAccountInfo()
    )

@app.route('/voting', methods=['POST'])
def voting():
    token = request.cookies.get('token')
    trello = TrelloProvider()
    if token is not None:
        trello.auth(token)
    else:
        return error("Unauthorized", None, False)
    user = trello.getAccountInfo()
    db = DataBaseSystem()
    free_votes = db.free_votes(user.id)
    if free_votes < len(request.form):
        return error('Not enough votes', user, True)
    processVoting(request.form, token)
    return render_template(
        'voting.html',
        year=datetime.now().year,
        is_auth = token is not None,
        message='Your vote is accepted!',
        user = user
    )

@app.route('/system', methods=['GET'])
def process():
    token = request.cookies.get('token')
    trello = TrelloProvider()
    if token is not None:
        trello.auth(token)
    else:
        return error("Unauthorized", None, False)
    user = trello.getAccountInfo()

    db = DataBaseSystem()
    db.sync(trello.getPublishedCards())

    return render_template(
        'system.html',
        year=datetime.now().year,
        header='System',
        is_auth = token is not None,
        debug_print = db.free_votes(user.id),
        user = user
    )

def error(message, user, is_auth):
    return render_template(
        'error.html',
        year=datetime.now().year,
        is_auth = is_auth,
        message = message,
        user = user
    )