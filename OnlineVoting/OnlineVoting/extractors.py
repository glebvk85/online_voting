import time

from OnlineVoting.contracts import *
from OnlineVoting.models import *


def get_creator_card(actions):
    for item in actions:
        if item['type'] == 'createCard':
            return item['idMemberCreator']


def import_speakers(members, comments):
    if comments is not None:
        for item in comments:
            if item['type'] == 'commentCard':
                text_comment = item['data']['text']
                authors = text_comment.strip().split(' ')
                if len(authors) > 0:
                    is_authors_comment = sum([len(x) > 0 and x[0] == '@' for x in authors]) == len(authors)
                    if is_authors_comment:
                        authors = [x[1:] for x in authors]
                        speakers = [get_trello_member_by_username(members, x) for x in authors]
                        if None not in speakers:
                            return (item['idMemberCreator'], speakers)


def get_trello_member_by_username(members, trello_username):
    for item in members:
        if item.username == trello_username:
            return item


def get_trello_member(members, member_hash):
    for item in members:
        if get_hash_member(item.id) == member_hash:
            return item


def get_new_contracts(transactions, cards, members):
    for card in cards:
        contract = get_lecture_contract(transactions, card.id)
        # sync new lectures
        if contract is None:
            if len(card.member_id) > 0:
                card.fetch_actions()
                member_id = get_creator_card(card.actions)
                contract = create_theme_contract(member_id, card.id)
                yield card, contract
        # sync new speakers
        if contract is not None:
            speaker_contract = get_speaker_contract(transactions, contract.id)
            if speaker_contract is None:
                card.fetch_comments(True)
                speakers_info = import_speakers(members, card.fetch_comments(True))
                if speakers_info is not None:
                    yield card, create_speaker_contract(speakers_info[0], contract.id,
                                                        [get_hash_member(x.id) for x in speakers_info[1]])


def get_trello_card(cards, trello_card_id):
    for card in cards:
        if card.id == trello_card_id:
            return card


def get_contract(transactions, contract_id):
    for item in transactions:
        if item.id == contract_id:
            return item


def show_new_lectures(transactions, cards, members):
    for item in transactions:
        if item.type == 'Contract':
            if item.hash_contract == '26bdb79ec40fcde72a061b5421cc8c26e04f9ce2ac77bf18668d5d35afc0de76':
                item.hash_contract = get_hash_contract('theme')
                write_transaction(item)
    for card, contract in get_new_contracts(transactions, cards, members):
        transactions.insert(0, contract)
        yield get_info(transactions, cards, members).__next__()


def write_new_lectures(transactions, cards, members):
    response = []
    for card, contract in get_new_contracts(transactions, cards, members):
        write_transaction(contract)
        transactions.insert(0, contract)
        response.append(get_info(transactions, cards, members).__next__())
    return response


def theme_is_finished(cards, trello_card_id):
    card = get_trello_card(cards, trello_card_id)
    return False if card is None else card.list_id == '5a03de5bfc228ec8e0608389'


def get_info(transactions, cards, members, where=None):
    hash_theme_contract = get_hash_contract('theme')
    hash_vote_contract = get_hash_contract('vote')
    hash_publication_contract = get_hash_contract('publication')
    hash_feedback_contract = get_hash_contract('feedback')
    hash_speaker_contract = get_hash_contract('speaker')
    for item in transactions:
        if where is not None and not where(item):
            continue
        if item.type == 'Contract':
            if item.hash_contract == hash_theme_contract:
                yield InfoModel(item.timestamp, get_trello_member(members, item.creator_address).full_name, 'create theme', get_trello_card(cards, item.parameters_contract[0]).name)
            elif item.hash_contract == hash_vote_contract:
                parent = get_contract(transactions, item.parent_contract_id)
                yield InfoModel(item.timestamp, get_trello_member(members, item.creator_address).full_name, 'vote', get_trello_card(cards, parent.parameters_contract[0]).name)
            elif item.hash_contract == hash_publication_contract:
                parent = get_contract(transactions, item.parent_contract_id)
                yield InfoModel(item.timestamp, get_trello_member(members, item.creator_address).full_name, 'publication', get_trello_card(cards, parent.parameters_contract[0]).name)
            elif item.hash_contract == hash_feedback_contract:
                parent = get_contract(transactions, item.parent_contract_id)
                parent = get_contract(transactions, parent.parent_contract_id)
                points = ' '.join(str(x) for x in item.parameters_contract)
                data = 'feedback - [{0}]'.format(points)
                yield InfoModel(item.timestamp, get_trello_member(members, item.creator_address).full_name, data, get_trello_card(cards, parent.parameters_contract[0]).name)
            elif item.hash_contract == hash_speaker_contract:
                parent = get_contract(transactions, item.parent_contract_id)
                data = 'set speaker(s) {0}'.format([get_trello_member(members, x).full_name for x in item.parameters_contract])
                yield InfoModel(item.timestamp, get_trello_member(members, item.creator_address).full_name, data, get_trello_card(cards, parent.parameters_contract[0]).name)
            else:
                yield InfoModel(item.timestamp, item.id, item.type, item.version)
        elif item.type == 'Transfer':
            owner = get_contract(transactions, item.owner_contract_id)
            yield InfoModel(item.timestamp, get_trello_member(members, owner.creator_address).full_name, 'closed',
                            get_trello_card(cards, owner.parameters_contract[0]).name)
            for pay in item.transfers:
                member_from = 'Get' if pay[0] is None else get_trello_member(members, pay[0]).full_name
                member_to = get_trello_member(members, pay[1]).full_name
                count = pay[2]
                yield InfoModel(item.timestamp, member_to, 'gets {} by'.format(count/1000), get_trello_card(cards, owner.parameters_contract[0]).name)
        else:
            yield InfoModel(item.timestamp, item.id, item.type, item.version)


def get_speakers(transactions, members, theme_contract_id):
    speakers = '(no speaker)'
    speaker_contract = get_speaker_contract(transactions, theme_contract_id)
    if speaker_contract is not None:
        speakers_info = []
        for sp in speaker_contract.parameters_contract:
            speakers_info.append(get_trello_member(members, sp).full_name)
            speakers = ', '.join(speakers_info)
    return speakers


def show_history_balance(transactions, cards, members, member):
    if member is None:
        return None
    member_hash = get_hash_member(member.id)
    for item in transactions:
        if item.type == 'Transfer':
            for pay in item.transfers:
                if pay[1] == member_hash:
                    contract = get_contract(transactions, item.owner_contract_id)
                    card = get_trello_card(cards, contract.parameters_contract[0])
                    speakers = get_speakers(transactions, members, item.owner_contract_id)
                    yield PointModel(speakers, card.name, pay[2]/1000)