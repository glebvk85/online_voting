from OnlineVoting.contracts import read_blockchain_contract, create_pay, get_hash_contract, get_open_contracts, write_transaction, get_child_contracts
from OnlineVoting.transactions import TransferInfo
from OnlineVoting.extractors import theme_is_finished, get_info
import statistics


def pay(from_address, to_address, count):
    return TransferInfo(from_address=from_address, to_address=to_address, count=int(count*1000))


def get_value(variables, name, default_value):
    try:
        return variables[name]
    except KeyError:
        variables[name] = default_value
        return get_value(variables, name, default_value)

def set_value(variables, name, value):
    variables[name] = value

def median(items):
    return statistics.median(items)


def get_code_contract(contract_hash):
    hashes = {}
    hashes[get_hash_contract('feedback')] = 'feedback'
    hashes[get_hash_contract('publication')] = 'publication'
    hashes[get_hash_contract('speaker')] = 'speaker'
    hashes[get_hash_contract('theme')] = 'theme'
    hashes[get_hash_contract('vote')] = 'vote'

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


def run_contracts(transactions, cards, members):
    response = []
    for item in get_open_contracts(transactions, get_hash_contract('theme')):
        if item.type == 'Contract':
            contract = run_chain_contracts(item, lambda x: theme_is_finished(cards, x), lambda x: get_child_contracts(transactions, x))
            if contract is not None:
                write_transaction(contract)
                transactions.insert(0, contract)
                response.append(get_info(transactions, cards, members).__next__())
    return response


def preview_run_contracts(transactions, cards, members):
    for item in get_open_contracts(transactions, get_hash_contract('theme')):
        if item.type == 'Contract':
            contract = run_chain_contracts(item, lambda x: theme_is_finished(cards, x), lambda x: get_child_contracts(transactions, x))
            if contract is not None:
                transactions.insert(0, contract)
                yield get_info(transactions, cards, members).__next__()


