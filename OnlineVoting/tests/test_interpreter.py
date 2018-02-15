import unittest
from unittest.mock import patch
from OnlineVoting.interpreter import *
from OnlineVoting.transactions import Contract, ChildContract
from OnlineVoting.contracts import read_blockchain_contract


def create_theme_contract():
    return Contract('owner_theme', 'theme', [2])


def create_speaker_contract(parent_id):
    return ChildContract('owner_speaker', 'speaker', parent_id, ['author'])


def create_publication_contract(parent_id):
    return ChildContract('owner_publication', 'publication', parent_id, [])


def create_feedback_contract(parent_id):
    return ChildContract('owner_feedback', 'feedback', parent_id, [1, 2, 3, 4, 5])


def create_vote_contract(parent_id):
    return ChildContract('owner_vote', 'vote', parent_id, [1])


class CardFake:
    def __init__(self, finished):
        self.list_id = '5a03de5bfc228ec8e0608389' if finished else ''


def patch_get_code_contract(contract_hash):
    return read_blockchain_contract(contract_hash)

speaker_with_feedback_contract_id = 1

def get_child_contracts_fake(contract_id):
    if contract_id == speaker_with_feedback_contract_id:
        return [create_speaker_contract(contract_id), create_feedback_contract(contract_id)]
    return []


class InterpreterTest(unittest.TestCase):
    def test_pay(self):
        pays = []
        pay(pays, 'from', 'to', 1)
        self.assertEqual(1, len(pays))
    '''
    @patch('OnlineVoting.interpreter.get_code_contract', return_value='')
    def test_run_chain_contracts_empty(self, patch_get_code_contract):
        result = run_chain_contracts(create_theme_contract(), CardFake(False), get_child_contracts_fake)
        self.assertIsNone(result)

    @patch('OnlineVoting.interpreter.get_code_contract', new=patch_get_code_contract)
    def test_run_chain_contracts_theme_not_finished(self):
        result = run_chain_contracts(create_theme_contract(), CardFake(False), get_child_contracts_fake)
        self.assertIsNone(result)

    @patch('OnlineVoting.interpreter.get_code_contract', new=patch_get_code_contract)
    def test_run_chain_contracts_theme_finished(self):
        result = run_chain_contracts(create_theme_contract(), CardFake(True), get_child_contracts_fake)
        self.assertEqual(result.transfers, [])
    '''
    @patch('OnlineVoting.interpreter.get_code_contract', new=patch_get_code_contract)
    def test_run_chain_contracts_theme_finished_with_feedback(self):
        contract = create_theme_contract()
        contract.id = speaker_with_feedback_contract_id
        result = run_chain_contracts(contract, CardFake(True), get_child_contracts_fake)
        self.assertEqual(len(result.transfers), 1)

if __name__ == '__main__':
    unittest.main()