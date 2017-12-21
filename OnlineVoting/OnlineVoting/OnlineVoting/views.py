
from datetime import datetime
from OnlineVoting.auth import make_authorization_url
from flask import render_template, make_response, request, redirect, url_for
from OnlineVoting import app
from OnlineVoting.trello import TrelloProvider
from OnlineVoting.blockchain import extractContract, VotingContract

@app.route('/')
@app.route('/home')
def home():
    token = request.cookies.get('token')

    trello = TrelloProvider()
    if token is not None:
        trello.auth(token)
    returnUrl = request.base_url
    return render_template(
        'index.html',
        year=datetime.now().year,
        auth_url = make_authorization_url(returnUrl),
        is_auth = token is not None,
        cards = trello.getIncomingCards(),
        user = trello.getAccountInfo()
    )

@app.route('/voting', methods=['POST'])
def voting():
    token = request.cookies.get('token')
    for key in request.form:
        extractContract(key, token)
    return render_template(
        'voting.html',
        year=datetime.now().year,
        message='Your vote is accepted!'
    )
