from OnlineVoting.transactions import *
import hashlib


def create_theme_contract(trello_member_id, trello_member_name, trello_card_id):
    return Contract(get_hash_member(trello_member_id, trello_member_name), get_hash_contract('theme'), [trello_card_id])


def vote(trello_member_id, trello_member_name, contract_id):
    return Contract(get_hash_member(trello_member_id, trello_member_name), get_hash_contract('vote'), [1], contract_id)


def create_publication_contract(member_hash, contract_id):
    return Contract(member_hash, get_hash_contract('publication'), [], contract_id)


def create_feedback_contract(trello_member_id, trello_member_name, contract_id,
                             theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend):
    return Contract(get_hash_member(trello_member_id, trello_member_name), get_hash_contract('feedback'),
                    [theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend], contract_id)


def create_pay(transfers):
    return Transfer(transfers)


def get_open_contracts(items, hash_cContract):
    sorted_items = sorted(items, key=sort_transaction)
    contracts = []
    closed_contracts = set()
    for item in sorted_items:
        if item.type == 'Contract':
            if item.hash_contract == hash_cContract:
                contracts.append(item)
        if item.type == 'Transfer':
            closed_contracts.add(item.owner_contract_id)
    for item in contracts:
        if item.id not in closed_contracts:
            yield item


def get_hash_member(trello_member_id, trello_member_name):
    sha = hashlib.sha256()
    sha.update((str(trello_member_id) + str(trello_member_name)).encode('utf-8'))
    return sha.hexdigest()


def read_blockchain_contract(name_contract):
    with open(os.path.join('OnlineVoting', 'blockchain-contracts', '{0}.py'.format(name_contract)), 'r') as f:
        text_contract = f.read()
    return text_contract


def get_hash_contract(name_contract):
    text_contract = read_blockchain_contract(name_contract)
    sha = hashlib.sha256()
    sha.update((str(text_contract)).encode('utf-8'))
    return sha.hexdigest()

