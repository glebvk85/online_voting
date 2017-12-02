
from datetime import datetime
from OnlineVoting.auth import make_authorization_url
from flask import render_template, make_response, request
from OnlineVoting import app

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        year=datetime.now().year,
        auth_url = make_authorization_url()
    )

@app.route('/voting')
def voting():
    return render_template(
        'voting.html',
        year=datetime.now().year,
        message='Your contact page.'
    )
