from OnlineVoting.contracts import read_blockchain_contract, create_pay
from OnlineVoting.transactions import TransferInfo
import statistics


def pay(pays, from_address, to_address, count):
    pays.append(TransferInfo(from_address=from_address, to_address=to_address, count=count*100))


def get_value(variables, name, default_value):
    try:
        return variables[name]
    except KeyError:
        variables[name] = default_value
        return get_value(variables, name, default_value)


def median(items):
    return statistics.median(items)


def get_code_contract(contract_hash):
    return ''


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


def run_chain_contracts(contract, card, get_child_contracts):
    # set variables
    theme_finished = False if card is None else card.list_id == '5a03de5bfc228ec8e0608389'
    variables = { 'pays' : [], 'theme_finished' : theme_finished }

    need_close, complete = run_contract(contract, variables, get_child_contracts)
    if need_close and complete:
        return create_pay(variables['pays'])


def exec_contract(text, _locals):
    # run contract and extract results
    exec(text, globals(), _locals)
    need_close = _locals['need_close']
    complete = _locals['complete']

    return need_close, complete


