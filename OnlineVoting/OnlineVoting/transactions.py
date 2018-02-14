import os  
import json
from uuid import uuid4
import datetime
import time


def append_transaction(transaction):
    with open(os.path.join('transactions', transaction.id), 'w', encoding='utf8') as f:
        json.dump(transaction.as_json(), f, ensure_ascii=False)


def read_transaction(path_file):
    with open(path_file, 'r', encoding='utf8') as f:
        return Transaction(j = f)


def sort_transaction(contract):
    return contract.timestamp


def get_files_from_directory(path_directory):
    for found_file in os.listdir(path_directory):
        full_path = os.path.join(path_directory, found_file)
        if os.path.isfile(full_path):
            yield full_path


class Transaction:
    def __init__(self, version = None, j = None):
        if version is not None:
            self.id = str(uuid4())
            self.type =  self.__class__.__name__
            self.timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
            self.version = version
        elif j is not None:
            self.__dict__ = json.load(j)
        else:
            raise SyntaxError('Incorrect call');
        
    def as_json(self):
        return self.__dict__


class Transfer(Transaction):
    def __init__(self, from_address, to_address, count):
        super(Transfer, self).__init__(version = 1)
        self.from_address = from_address
        self.to_address = to_address
        self.count = count

    def as_json(self):
        return super(Transfer, self).as_json()


class Contract(Transaction):
    def __init__(self, creator_address, hash_contract, parameters_contract):
        super(Contract, self).__init__(version = 1)
        self.creator_address = creator_address
        self.hash_contract = hash_contract
        self.parameters_contract = parameters_contract

    def as_json(self):
        return super(Contract, self).as_json()


class ChildContract(Transaction):
    def __init__(self, creator_address, hash_contract, parent_contract_id, parameters_contract):
        super(ChildContract, self).__init__(version = 1)
        self.creator_address = creator_address
        self.parent_contract_id = parent_contract_id
        self.hash_contract = hash_contract
        self.parameters_contract = parameters_contract

    def as_json(self):
        return super(ChildContract, self).as_json()


class ClosingContract(Transaction):
    def __init__(self, creator_address, parent_contract_id, parameters_contract):
        super(ClosingContract, self).__init__(version = 1)
        self.creator_address = creator_address
        self.parent_contract_id = parent_contract_id
        self.parameters_contract = parameters_contract

    def as_json(self):
        return super(ClosingContract, self).as_json()
