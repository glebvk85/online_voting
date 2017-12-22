
from datetime import datetime
from OnlineVoting.auth import make_authorization_url
from flask import render_template, make_response, request, redirect, url_for
from OnlineVoting import app
from OnlineVoting.trello import TrelloProvider
from OnlineVoting.blockchain import extractContract, VotingContract
from OnlineVoting.processing import processVoting

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
        header = 'Голосуем за темы на обучение с учетом их актуальности для решения тактических и стратегических вопросов в команде.',
        year=datetime.now().year,
        auth_url = make_authorization_url(returnUrl),
        is_auth = token is not None,
        cards = trello.getIncomingCards(),
        user = trello.getAccountInfo()
    )

@app.route('/voting', methods=['POST'])
def voting():
    token = request.cookies.get('token')
    processVoting(request.form, token)
    return render_template(
        'voting.html',
        year=datetime.now().year,
        message='Your vote is accepted!'
    )
