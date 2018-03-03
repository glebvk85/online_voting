from OnlineVoting.transactions import *
import hashlib


def create_theme_contract(trello_member_id, trello_card_id):
    return Contract(get_hash_member(trello_member_id), get_hash_contract('theme'), [trello_card_id])


def vote(trello_member_id, contract_id):
    return Contract(get_hash_member(trello_member_id), get_hash_contract('vote'), [1], contract_id)


def create_publication_contract(member_hash, contract_id):
    return Contract(member_hash, get_hash_contract('publication'), [], contract_id)


def create_feedback_contract(trello_member_id, contract_id,
                             theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend):
    return Contract(get_hash_member(trello_member_id), get_hash_contract('feedback'),
                    [theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend], contract_id)


def create_speaker_contract(trello_member_id, contract_id, members_hash_list):
    return Contract(get_hash_member(trello_member_id), get_hash_contract('speaker'),
                    members_hash_list, contract_id)


def create_pay(transfers, owner_contract_id):
    return Transfer(transfers, owner_contract_id)


def get_contract(contracts, contract_id):
    for item in contracts:
        if item.id == contract_id:
            return item


def is_closed(contract, all_contracts, closed_contracts):
    if contract.id in closed_contracts:
        return True
    if contract.parent_contract_id is not None:
        return is_closed(get_contract(all_contracts, contract.parent_contract_id), all_contracts, closed_contracts)
    return False


def get_open_contracts(transactions, hash_contract):
    sorted_items = sorted(transactions, key=sort_timestamp_transaction)
    contracts = []
    closed_contracts = set()
    for item in sorted_items:
        if item.type == 'Contract':
            if item.hash_contract == hash_contract:
                contracts.append(item)
        if item.type == 'Transfer':
            closed_contracts.add(item.owner_contract_id)
    for item in contracts:
        if not is_closed(item, transactions, closed_contracts):
            yield item


def get_child_contracts(transactions, contract_id):
    sorted_items = sorted(transactions, key=sort_timestamp_transaction)
    for item in sorted_items:
        if item.type == 'Contract' and item.parent_contract_id == contract_id:
            yield item


def get_speaker_contract(transactions, contract_id):
    hash_contract = get_hash_contract('speaker')
    for item in get_child_contracts(transactions, contract_id):
        if item.hash_contract == hash_contract:
            return item


def get_hash_member(trello_member_id):
    sha = hashlib.sha256()
    sha.update((str(trello_member_id)).encode('utf-8'))
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


def get_lecture_contract(transactions, trello_card_id):
    hash_contract = get_hash_contract('theme')
    for item in transactions:
        if item.type == 'Contract' and item.hash_contract == hash_contract and item.parameters_contract[0] == trello_card_id:
            return item

