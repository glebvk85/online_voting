#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from OnlineVoting.auth import make_authorization_url
from flask import render_template, make_response, request, redirect, url_for
from OnlineVoting import app
from OnlineVoting.trello import TrelloProvider
from OnlineVoting.blockchain import DataBaseSystem
from flask import Response
from OnlineVoting.extractors import *
from OnlineVoting.contracts import *
from OnlineVoting.interpreter import preview_run_contracts, run_contracts


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
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
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
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
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
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
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
        year=datetime.datetime.now().year,
        is_auth = is_auth,
        user = user,
        count_vote = count_free_votes(db, user),
        count_points=count_coins(db, user),
        message='Page for feedback created!'
    )


@app.route('/apply_feedback', methods=['POST'])
def apply_feedback():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    contract = db.get_contract(request.form['id'])
    if db.get_feedback(contract.id, user) is not None:
        return error("You already voted", user, True)
    db.feedback(contract.id, user, try_get_value(request.form, 'themeIsActual'), try_get_value(request.form, 'canApply'), try_get_value(request.form, 'qualityInformation'), try_get_value(request.form, 'preparednessAuthor'), try_get_value(request.form, 'canRecommend'))
    return render_template(
        'apply_feedback.html',
        year=datetime.datetime.now().year,
        is_auth = is_auth,
        message='Thanks for feedback!',
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user)
    )


@app.route('/feedback')
def feedback():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    contract = db.get_contract(request.values['id'])
    if db.get_feedback(contract.id, user) is not None:
        return error("You already voted", user, True)
    contract = db.get_contract(contract.parent_contract_id)
    if contract is None:
        return error("Publication not found", user, True)
    card = db.get_trello_card(contract.parameters_contract[0])
    return render_template(
        'feedback.html',
        year=datetime.datetime.now().year,
        is_auth = is_auth,
        user = user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
        header=card.name,
        contract_id = request.values['id'],
        title1 = 'Эта тема актуальна/релевантна для наших задач',
        title2 = 'Я могу применить полученные навыки и знания на практике для решения наших задач',
        title3 = 'Оцените качество изложения и наглядность информации',
        title4 = 'Оцените качество подготовки выступающих и глубину проработки темы',
        title5 = 'Я бы рекомендовал эту публикацию своим коллегам, не участвовавшим в мероприятии',
    )


@app.route('/update-commit', methods=['GET'])
def update_commit():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    if not is_admin(user.username):
        return error("Access denied", user, True)
    return render_template(
        'info.html',
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
        header='Success import Trello',
        items = write_new_lectures(db.transactions, db.allCards, db.allMembers)
    )


@app.route('/update', methods=['GET'])
def update():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    if not is_admin(user.username):
        return error("Access denied", user, True)
    return render_template(
        'info.html',
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
        header='Preview import from Trello',
        items = show_new_lectures(db.transactions, db.allCards, db.allMembers)
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
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
        items=get_info(sorted(db.transactions, key=sort_timestamp_transaction), db.allCards, db.allMembers),
        header='System'
    )


@app.route('/history_balance', methods=['GET'])
def history_balance():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    return render_template(
        'history_balance.html',
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
        list=db.history_balance(user),
        header='History balance'
    )


@app.route('/dashboard', methods=['GET'])
def dashboard():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    return render_template(
        'dashboard.html',
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
        list=db.get_all_free_votes(),
        publications=db.get_all_publications(),
        header='System'
    )


@app.route('/feedback_export.csv')
def feedback_export():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    if not is_admin(user.username):
        return error("Access denied", user, True)

    def generate(contracts):
        for row in contracts:
            author = db.get_trello_member(row.creator_address).full_name
            points = ','.join([str(x) for x in row.parameters_contract])
            yield author + ',' + points + '\n'

    return Response(generate(db.get_child_contracts(request.values['id'])), mimetype='text/csv')


@app.route('/run', methods=['GET'])
def run():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    if not is_admin(user.username):
        return error("Access denied", user, True)
    return render_template(
        'info.html',
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
        header='Contracts complete',
        items=preview_run_contracts(db.transactions, db.allCards, db.allMembers))


@app.route('/run-commit', methods=['GET'])
def run_commit():
    is_auth, trello, user, db = initialize()
    if not is_auth:
        return error("Unauthorized", None, False)
    if not is_admin(user.username):
        return error("Access denied", user, True)
    return render_template(
        'info.html',
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        count_vote=count_free_votes(db, user),
        count_points=count_coins(db, user),
        header='Contracts closed',
        items=run_contracts(db.transactions, db.allCards, db.allMembers))


def error(message, user, is_auth):
    return render_template(
        'error.html',
        year=datetime.datetime.now().year,
        is_auth=is_auth,
        user=user,
        message=message
    )


def is_admin(username):
    admins = set()
    admins.add('gleb_kucherenko')
    admins.add('evanchurov')
    return username in admins


def try_get_value(form, value_name):
    return int(form[value_name]) if value_name in form else 0


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

def count_coins(db, user):
    return None if db is None or user is None else db.count_coins(user)