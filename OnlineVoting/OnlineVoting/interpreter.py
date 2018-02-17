from OnlineVoting.contracts import read_blockchain_contract, create_pay, get_hash_contract
from OnlineVoting.transactions import TransferInfo
import statistics


def pay(from_address, to_address, count):
    return TransferInfo(from_address=from_address, to_address=to_address, count=int(count*100))


def get_value(variables, name, default_value):
    try:
        return variables[name]
    except KeyError:
        variables[name] = default_value
        return get_value(variables, name, default_value)


def median(items):
    return statistics.median(items)


def get_code_contract(contract_hash):
    hashes = {}
    hashes[get_hash_contract('feedback')] = 'feedback'
    hashes[get_hash_contract('publication')] = 'publication'
    hashes[get_hash_contract('speaker')] = 'speaker'
    hashes[get_hash_contract('theme')] = 'theme'
    hashes[get_hash_contract('vote')] = 'vote'

    if contract_hash == '10555f55a860fe2309bd6b009c86f1b1415cae99102bf62fb1d1372214706e6b':
        return read_blockchain_contract('theme')
    if contract_hash == 'bf28c889bbe3b2208e5393d3a27fc93f98b8922930a1e9c8cc2b58c37b960814':
        return read_blockchain_contract('speaker')
    if contract_hash == '1c8a194d0c19145454b58e4b469bec1ea9c813c7debf96c96611d60135fb3536':
        return read_blockchain_contract('feedback')
    if contract_hash == '5e84382ff2b6c1a38e26d56c18346c9fb097ff538135efc91695f64078d24ae4':
        return read_blockchain_contract('vote')

    return read_blockchain_contract(hashes[contract_hash])


def run_contract(contract, variables, get_child_contracts):
    child_contracts = get_child_contracts(contract.id)
    need_close = False
    complete = False
    for child in child_contracts:
        local_need_close, local_complete = run_contract(child, variables, get_child_contracts)
        need_close = need_close and local_need_close
        complete = complete and local_complete
        if need_close and not complete:
            return True, False
    code_contract = get_code_contract(contract.hash_contract)
    parameters = contract.parameters_contract
    owner_address = contract.creator_address
    _locals = locals()
    return exec_contract(code_contract, _locals)


def run_chain_contracts(contract, theme_is_finished, get_child_contracts):
    # set variables
    variables = { 'pays' : [], 'theme_is_finished' : theme_is_finished }

    need_close, complete = run_contract(contract, variables, get_child_contracts)
    if need_close and complete:
        return create_pay(variables['pays'], contract.id)


def exec_contract(text, _locals):
    # run contract and extract results
    exec(text, globals(), _locals)
    need_close = _locals['need_close']
    complete = _locals['complete']

    return need_close, complete


