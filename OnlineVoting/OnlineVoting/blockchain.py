import datetime as date
import json
import time
import os  
from uuid import uuid4
from collections import defaultdict
from OnlineVoting.blockchain import *
from OnlineVoting.contracts import *
from OnlineVoting.models import *
from OnlineVoting.transactions import *
from OnlineVoting.trello import TrelloProvider


class DataBaseSystem:
    def __init__(self, trello):
        self.transactions = []
        for transactionPath in get_files_from_directory('transactions'):
            self.transactions.append(read_transaction(transactionPath))
        self.allCards = trello.get_all_cards()
        self.allMembers = trello.get_all_members()

    def free_votes(self, member):
        if member is None:
            return None
        member_hash = get_hash_member(member.id, member.username)
        count = 0
        for i in get_open_contracts(self.transactions, get_hash_contract('vote')):
            if i.creator_address == member_hash:
                count += i.parameters_contract[0]
        max_votes = 2
        return max_votes - count

    def get_all_free_votes(self):
        max_votes = 2
        votes = defaultdict()
        for i in get_open_contracts(self.transactions, get_hash_contract('vote')):
            votes.setdefault(i.creator_address, []).append(i.parameters_contract[0])
        for i in self.allMembers:
            member_hash = get_hash_member(i.id, i.username)
            votes.setdefault(member_hash, [])
            yield PointModel(i.username, i.full_name, max_votes - sum(votes[member_hash]))

    def get_themes_by_user(self, member):
        member_hash = get_hash_member(member.id, member.username)
        contracts = get_open_contracts(self.transactions, get_hash_contract('theme'))
        for item in contracts:
            if item.creator_address == member_hash:
                card = self.get_trello_card(item.parameters_contract[0])
                yield VotingModel(item.id, member.full_name, card.name, item.timestamp, card.short_url)

    def get_contract(self, contract_id):
        for item in self.transactions:
            if item.id == contract_id:
                return item

    def get_lecture_contract(self, trello_card_id):
        hash_contract = get_hash_contract('theme')
        for item in self.transactions:
            if item.type == 'Contract' and item.parameters_contract[0] == trello_card_id and item.hash_contract == hash_contract:
                return item

    def get_feedback(self, publication_contract_id, member):
        member_hash = get_hash_member(member.id, member.username)
        hash_contract = get_hash_contract('feedback')
        for item in self.transactions:
            if item.type == 'Contract' and item.hash_contract == hash_contract and item.parent_contract_id == publication_contract_id and item.creator_address == member_hash:
                return item

    def get_trello_card(self, trello_card_id):
        for item in self.allCards:
            if item.id == trello_card_id:
                return item

    def get_trello_member(self, member_hash):
        for item in self.allMembers:
            if get_hash_member(item.id, item.username) == member_hash:
                return item

    def get_trello_member_by_trello_id(self, trello_member_id):
        for item in self.allMembers:
            if item.id == trello_member_id:
                return item

    def get_voting_list(self):
        hash_theme_contract = get_hash_contract('theme')
        for item in get_open_contracts(self.transactions, hash_theme_contract):
            if self.get_trello_card(item.parameters_contract[0]).list_id == TrelloProvider.listIncomingId:
                card = self.get_trello_card(item.parameters_contract[0])
                yield VotingModel(item.id, self.get_trello_member(item.creator_address).full_name, card.name, item.timestamp, card.url)

    def get_new_publication(self, user):
        member = self.get_trello_member_by_trello_id(user.id)
        member_hash = get_hash_member(member.id, member.username)
        hash_publication_contract = get_hash_contract('publication')
        hash_feedback_contract = get_hash_contract('feedback')
        for item in get_open_contracts(self.transactions, hash_publication_contract):
            found = False
            feedbacks = get_open_contracts(self.transactions, hash_feedback_contract)
            for j in feedbacks:
                if j.parent_contract_id == item.id and member_hash == j.creator_address:
                    found = True
                    break
            if not found:
                parent = self.get_contract(item.parent_contract_id)
                card = self.get_trello_card(parent.parameters_contract[0])
                yield VotingModel(item.id, self.get_trello_member(item.creator_address).full_name, card.name, item.timestamp, card.url)

    def vote(self, form, user):
        for item in form:
            lecture = self.get_contract(item)
            member = self.get_trello_member_by_trello_id(user.id)
            contract = vote(member.id, member.username, lecture.id)
            write_transaction(contract)
            self.transactions.append(contract)
            card = self.get_trello_card(lecture.parameters_contract[0])
            title = card.name.lstrip('(👍) ')
            cnt = 0
            for item in get_open_contracts(self.transactions, get_hash_contract('vote')):
                if item.parent_contract_id == lecture.id:
                    cnt += item.parameters_contract[0]
            tmp = ''
            for i in range(cnt):
                tmp += '👍'
            title = '({0}) {1}'.format(tmp, title)
            card.set_name(title)
            card.comment('👍')

    def publication(self, form, user):
        for item in form:
            lecture = self.get_contract(item)
            member = self.get_trello_member_by_trello_id(user.id)
            contract = create_publication_contract(get_hash_member(member.id, member.username), lecture.id)
            write_transaction(contract)
            self.transactions.append(contract)

    def feedback(self, contractId, user, theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend):
        lecture = self.get_contract(contractId)
        member = self.get_trello_member_by_trello_id(user.id)
        contract = create_feedback_contract(member.id, member.username, lecture.id, theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend)
        write_transaction(contract)
        self.transactions.append(contract)

    def get_info(self):
        sorted_list = sorted(self.transactions, key=sort_transaction)
        hash_theme_contract = get_hash_contract('theme')
        hash_vote_contract = get_hash_contract('vote')
        hash_publication_contract = get_hash_contract('publication')
        hash_feedback_contract = get_hash_contract('feedback')
        for item in sorted_list:
            if item.hash_contract == hash_theme_contract:
                yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, 'create theme', self.get_trello_card(item.parameters_contract[0]).name)
            if item.hash_contract == hash_vote_contract:
                parent = self.get_contract(item.parent_contract_id)
                yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, 'vote', self.get_trello_card(parent.parameters_contract[0]).name)
            if item.hash_contract == hash_publication_contract:
                parent = self.get_contract(item.parent_contract_id)
                yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, 'publication', self.get_trello_card(parent.parameters_contract[0]).name)
            if item.hash_contract == hash_feedback_contract:
                parent = self.get_contract(item.parent_contract_id)
                parent = self.get_contract(parent.parent_contract_id)
                points = " ".join(str(x) for x in item.parameters_contract)
                data = "feedback - [{0}]".format(points)
                yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, data, self.get_trello_card(parent.parameters_contract[0]).name)

    def sync_lectures(self):
        # sync new lectures
        for item in self.allCards:
            contract = self.get_lecture_contract(item.id)
            if contract is None:
                if len(item.member_id) > 0:
                    member = self.get_trello_member_by_trello_id(item.member_id[0])
                    if member is not None:
                        item.fetch_actions()
                        print(item.actions)
                        contract = create_theme_contract(member.id, member.username, item.id)
                        contract.timestamp = int(time.mktime(item.card_created_date.timetuple())) 
                        write_transaction(contract)
                        self.transactions.append(contract)
        # update contracts
        for item in self.transactions:
            old_hashes = {'86b1e91ae158671c784422216426ac7e50cd14412049322609cee2448c865c15' : 'feedback',
                          '90e8255cf28c2979b69f2a91439ebd1b765f46884de2ef7d4653e71af6c6b060' : 'publication',
                          'a96a59ffd294d425a433b14657d5b6ea1a6215f809f8a849e045dc06e0b11d09' : 'theme',
                          'eec62090053d8bd962da5993d600a0b2a0f9836e194f315903a5f9a0ed6dab7c' : 'vote',
                          }
            item.hash_contract = get_hash_contract(old_hashes[item.hash_contract])
            write_transaction(item)




