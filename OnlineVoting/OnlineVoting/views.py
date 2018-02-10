#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from OnlineVoting.auth import make_authorization_url
from flask import render_template, make_response, request, redirect, url_for
from OnlineVoting import app
from OnlineVoting.trello import TrelloProvider
from OnlineVoting.blockchain import DataBaseSystem


@app.route('/')
@app.route('/home')
def home():
    is_auth, trello, user, db = initialize()
    return_url = request.base_url
    incoming_cards = None
    if is_auth:
        incoming_cards = db.get_voting_list()

    return render_template(
        'index.html',
        year=datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        header='Голосуем за темы на обучение с учетом их актуальности для решения тактических и стратегических вопросов в команде.',
        auth_url=make_authorization_url(return_url),
        cards=incoming_cards
    )


@app.route('/voting', methods=['POST'])
def voting():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    if count_free_votes(db, user) < len(request.form):
        return error('Not enough votes', user, True)
    db.vote(request.form, user)
    return render_template(
        'voting.html',
        year=datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=db.free_votes(user),
        message='Your vote is accepted!',
    )


@app.route('/room')
def room():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    themes = None
    if is_auth:
        themes = db.get_themes_by_user(user)

    return render_template(
        'room.html',
        year=datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        themes=themes,
        feedbacks=db.get_new_publication(user),
        header='My themes',
        header2='Open feedbacks'
    )


@app.route('/create_feedback', methods=['POST'])
def create_feedback():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    db.publication(request.form, user)
    return render_template(
        'create_feedback.html',
        year=datetime.now().year,
        is_auth = is_auth,
        user = user,
        count_vote = count_free_votes(db, user),
        message='Page for feedback created!'
    )


@app.route('/apply_feedback', methods=['POST'])
def apply_feedback():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    db.feedback(request.form['id'], user, try_get_value(request.form, 'themeIsActual'), try_get_value(request.form, 'canApply'), try_get_value(request.form, 'qualityInformation'), try_get_value(request.form, 'preparednessAuthor'), try_get_value(request.form, 'canRecommend'))
    return render_template(
        'apply_feedback.html',
        year=datetime.now().year,
        is_auth = is_auth,
        message='Thanks for feedback!',
        user=user,
        count_vote=count_free_votes(db, user)
    )


@app.route('/feedback')
def feedback():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    contract = db.get_contract(request.values['id'])
    contract = db.get_contract(contract.parent_contract_id)
    if contract is None:
        return error("Publication not found", user, True)
    card = db.get_trello_card(contract.parameters_contract[0])
    return render_template(
        'feedback.html',
        year=datetime.now().year,
        is_auth = is_auth,
        user = user,
        count_vote=count_free_votes(db, user),
        header=card.name,
        contract_id = request.values['id'],
        title1 = 'Эта тема актуальна/релевантна для наших задач',
        title2 = 'Я могу применить полученные навыки и знания на практике для решения наших задач',
        title3 = 'Оцените качество изложения и наглядность информации',
        title4 = 'Оцените качество подготовки выступающих и глубину проработки темы',
        title5 = 'Я бы рекомендовал эту публикацию своим коллегам, не участвовавшим в мероприятии',
    )


@app.route('/system', methods=['GET'])
def process():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    if not is_admin(user.username):
        return error("Access denied", user, True)
    db.sync_lectures()
    return render_template(
        'system.html',
        year=datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        debug_print="debug",
        header='System',
    )


@app.route('/info', methods=['GET'])
def info():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    if not is_admin(user.username):
        return error("Access denied", user, True)
    return render_template(
        'info.html',
        year=datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        list=db.get_info(),
        header='System'
    )


@app.route('/dashboard', methods=['GET'])
def dashboard():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    return render_template(
        'dashboard.html',
        year=datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=db.free_votes(user),
        list=db.get_all_free_votes(),
        header='System'
    )


def error(message, user, is_auth):
    return render_template(
        'error.html',
        year=datetime.now().year,
        is_auth=is_auth,
        user=user,
        message=message
    )


def is_admin(username):
    admins = set()
    admins.add('gleb_kucherenko')
    admins.add('evanchurov')
    return username in admins


def try_get_value(form, valueName):
    return form[valueName] if valueName in form else 0


def initialize():
    token = request.cookies.get('token')
    is_auth = token is not None
    if not is_auth:
        return False, None, None, None
    trello = TrelloProvider()
    trello.auth(token)
    user = trello.get_account_info()
    db = DataBaseSystem(trello)
    return is_auth, trello, user, db


def count_free_votes(db, user):
    return None if db is None or user is None else db.free_votes(user)