from OnlineVoting.contracts import read_blockchain_contract, create_pay
from OnlineVoting.transactions import TransferInfo
import statistics

def pay(pays, from_address, to_address, count):
    pays.append(TransferInfo(from_address=from_address, to_address=to_address, count=count*100))

def median(list):
    print(list)
    return statistics.median(list)

def run_chain_contracts():
    # set variables
    card = None
    complete = False
    need_close = False
    theme_finished = False if card is None else card.list_id == '5a03de5bfc228ec8e0608389'
    pays = []
    '''
    text = read_blockchain_contract('vote')

    parameters = [1]
    owner_address = 'sdsdsd'
    _locals = locals()
    print(run_contract(text, _locals))
    parameters = [2]
    owner_address = 'fgdgdf'
    _locals = locals()
    print(run_contract(text, _locals))
    parameters = [3]
    owner_address = '1111'
    _locals = locals()
    print(run_contract(text, _locals))

    text = read_blockchain_contract('feedback')
    parameters = [1, 2, 2, 3, 4]
    owner_address = 'sdssdsdsdsddsd'
    _locals = locals()
    print(run_contract(text, _locals))

    parameters = [2, 2, 2, 1, 4]
    owner_address = 'sdsdsdsdsddsdsd'
    _locals = locals()
    print(run_contract(text, _locals))

    text = read_blockchain_contract('theme')
    parameters = [1]
    owner_address = 'sdsdsd'
    _locals = locals()
    print(run_contract(text, _locals))
    '''
    return create_pay(pays)

def run_contract(text, _locals):
    # run contract and extract results
    exec(text, globals(), _locals)
    need_close = _locals['need_close']
    complete = _locals['complete']

    # check complete condition
    if need_close:
        if complete:
            return True
    return False


