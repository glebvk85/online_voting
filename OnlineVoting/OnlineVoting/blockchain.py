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
from OnlineVoting.interpreter import *


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
        member_hash = get_hash_member(member.id)
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
            member_hash = get_hash_member(i.id)
            votes.setdefault(member_hash, [])
            yield PointModel(i.username, i.full_name, max_votes - sum(votes[member_hash]))

    def get_child_contracts(self, contract_id):
        return get_child_contracts(self.transactions, contract_id)

    def theme_is_finished(self, trello_card_id):
        card = self.get_trello_card(trello_card_id)
        print('card {0}'.format(card))
        return False if card is None else card.list_id == '5a03de5bfc228ec8e0608389'

    def run_contracts(self):
        for item in self.transactions:
            if item.type == 'Contract':
                result = run_chain_contracts(item, self.theme_is_finished, self.get_child_contracts)
                if result is not None:
                    write_transaction(result)
                    self.transactions.append(result)

    def get_themes_by_user(self, member):
        member_hash = get_hash_member(member.id)
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
            if item.type == 'Contract' and item.hash_contract == hash_contract and item.parameters_contract[0] == trello_card_id:
                return item

    def get_feedback(self, publication_contract_id, member):
        member_hash = get_hash_member(member.id)
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
            if get_hash_member(item.id) == member_hash:
                return item

    def get_trello_member_by_username(self, trello_username):
        for item in self.allMembers:
            if item.username == trello_username:
                return item

    def get_voting_list(self):
        hash_theme_contract = get_hash_contract('theme')
        for item in get_open_contracts(self.transactions, hash_theme_contract):
            if self.get_trello_card(item.parameters_contract[0]).list_id == TrelloProvider.listIncomingId:
                card = self.get_trello_card(item.parameters_contract[0])
                yield VotingModel(item.id, self.get_trello_member(item.creator_address).full_name, card.name, item.timestamp, card.url)

    def get_new_publication(self, user):
        member_hash = get_hash_member(user.id)
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
            contract = create_publication_contract(get_hash_member(user.id), lecture.id)
            write_transaction(contract)
            self.transactions.append(contract)

    def feedback(self, contractId, user, theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend):
        lecture = self.get_contract(contractId)
        contract = create_feedback_contract(user.id, lecture.id, theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend)
        write_transaction(contract)
        self.transactions.append(contract)

    def get_info(self):
        sorted_list = sorted(self.transactions, key=sort_transaction)
        hash_theme_contract = get_hash_contract('theme')
        hash_vote_contract = get_hash_contract('vote')
        hash_publication_contract = get_hash_contract('publication')
        hash_feedback_contract = get_hash_contract('feedback')
        hash_speaker_contract = get_hash_contract('speaker')
        for item in sorted_list:
            if item.type == 'Contract':
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
                    points = ' '.join(str(x) for x in item.parameters_contract)
                    data = 'feedback - [{0}]'.format(points)
                    yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, data, self.get_trello_card(parent.parameters_contract[0]).name)
                if item.hash_contract == hash_speaker_contract:
                    parent = self.get_contract(item.parent_contract_id)
                    data = 'set speaker(s) {0}'.format([self.get_trello_member(x).full_name for x in item.parameters_contract])
                    yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, data, self.get_trello_card(parent.parameters_contract[0]).name)
            if item.type == 'Transfer':
                owner = self.get_contract(item.owner_contract_id)
                for pay in item.transfers:
                    member_from = 'Get' if pay[0] is None else self.get_trello_member(pay[0]).full_name
                    member_to = self.get_trello_member(pay[1]).full_name
                    count = pay[2]
                    yield InfoModel(item.timestamp, member_to, 'gets {} by'.format(count/100), self.get_trello_card(owner.parameters_contract[0]).name)

    def get_creator_card(self, actions):
        for item in actions:
            if item['type'] == 'createCard':
                return item['idMemberCreator']

    def get_speakers(self, comments):
        if comments is not None:
            for item in comments:
                if item['type'] == 'commentCard':
                    text_comment = item['data']['text']
                    authors = text_comment.strip().split(' ')
                    if len(authors) > 0:
                        is_authors_comment = sum([len(x) > 0 and x[0] == '@' for x in authors]) == len(authors)
                        if is_authors_comment:
                            authors = [x[1:] for x in authors]
                            speakers = [self.get_trello_member_by_username(x) for x in authors]
                            if None not in speakers:
                                return (item['idMemberCreator'], speakers)

    def sync_lectures(self):
        # update contracts
        mem = {}
        for x in self.allMembers:
            mem[get_old_hash_member(x.id, x.username)] = get_hash_member(x.id)
        for item in self.transactions:
            old_hashes = {'86b1e91ae158671c784422216426ac7e50cd14412049322609cee2448c865c15' : 'feedback',
                          '90e8255cf28c2979b69f2a91439ebd1b765f46884de2ef7d4653e71af6c6b060' : 'publication',
                          'a96a59ffd294d425a433b14657d5b6ea1a6215f809f8a849e045dc06e0b11d09' : 'theme',
                          'eec62090053d8bd962da5993d600a0b2a0f9836e194f315903a5f9a0ed6dab7c' : 'vote',
                          }
            item.hash_contract = get_hash_contract(old_hashes[item.hash_contract])
            if item.type == 'Contract':
                item.parent_contract_id = None
            if item.type == 'ChildContract':
                item.type = 'Contract'
            item.creator_address = mem[item.creator_address]
            write_transaction(item)
        # sync new lectures
        for item in self.allCards:
            contract = self.get_lecture_contract(item.id)
            if contract is None:
                if len(item.member_id) > 0:
                    item.fetch_actions()
                    member_id = self.get_creator_card(item.actions)
                    contract = create_theme_contract(member_id, item.id)
                    contract.timestamp = int(time.mktime(item.card_created_date.timetuple()))
                    write_transaction(contract)
                    self.transactions.append(contract)
            else:
                item.fetch_actions()
                member_id = self.get_creator_card(item.actions)
                contract.creator_address = get_hash_member(member_id)
                write_transaction(contract)
            # add speakers
            if contract is not None:
                speaker_contract = get_speaker_contract(self.transactions, contract.id)
                if speaker_contract is None:
                    item.fetch_comments(True)
                    speakers_info = self.get_speakers(item.fetch_comments(True))
                    if speakers_info is not None:
                        speaker_contract = create_speaker_contract(speakers_info[0], contract.id, [get_hash_member(x.id) for x in speakers_info[1]])
                        write_transaction(speaker_contract)
                        self.transactions.append(speaker_contract)



