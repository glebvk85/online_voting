from OnlineVoting.transactions import *
import hashlib


def create_theme_contract(trelloMemberId, trelloMemberName, trelloCardId):
    return Contract(get_hash_member(trelloMemberId, trelloMemberName), get_hash_contract('theme'), [trelloCardId])


def vote(trelloMemberId, trelloMemberName, contractId):
    return ChildContract(get_hash_member(trelloMemberId, trelloMemberName), get_hash_contract('vote'), contractId, [1])


def create_publication_contract(memberHash, contractId):
    return ChildContract(memberHash, get_hash_contract('publication'), contractId, [])


def create_feedback_contract(trelloMemberId, trelloMemberName, contractId, themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend):
    return ChildContract(get_hash_member(trelloMemberId, trelloMemberName), get_hash_contract('feedback'), contractId, [themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend])


def close_theme_contract(trelloMemberId, trelloMemberName, trelloCardId):
    return ClosingContract(get_hash_member(trelloMemberId, trelloMemberName), contractId, [])


def get_open_child_contracts(list, hashContract):
    sortedList = sorted(list, key=sort_transaction)
    contracts = []
    closedContracts = set()
    for item in sortedList:
        if item.type == 'ChildContract':
            if item.hash_contract == hashContract:
                contracts.append(item)
        if item.type == 'ClosingContract':
            closedContracts.add(item.parent_contract_id)
    for item in contracts:
        if item.parent_contract_id not in closedContracts:
            yield item


def get_open_contracts(list, hashContract):
    sortedList = sorted(list, key=sort_transaction)
    contracts = []
    closedContracts = set()
    for item in sortedList:
        if item.type == 'Contract':
            if item.hash_contract == hashContract:
                contracts.append(item)
        if item.type == 'ClosingContract':
            closedContracts.add(item.parent_contract_id)
    for item in contracts:
        if item.id not in closedContracts:
            yield item


def get_hash_member(trelloMemberId, trelloMemberName):
    sha = hashlib.sha256()
    sha.update((str(trelloMemberId) + str(trelloMemberName)).encode('utf-8'))
    return sha.hexdigest()


def run_contract(text, parameters_contract, owner_contract_address):
    complete = False
    need_close = False
    parameters = parameters_contract
    owner_address = owner_contract_address
    exec(text)
    if need_close:
        if complete:
            # TODO: create close contract
            pass


def get_hash_contract(nameContract):
    with open(os.path.join('OnlineVoting', 'blockchain-contracts', '{0}.py'.format(nameContract)), 'r') as f:
        text_contract = f.read()
    sha = hashlib.sha256()
    sha.update((str(text_contract)).encode('utf-8'))
    return sha.hexdigest()

