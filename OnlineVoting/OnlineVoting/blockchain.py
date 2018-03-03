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

    def count_coins(self, member):
        if member is None:
            return None
        member_hash = get_hash_member(member.id)
        balance = 0
        for item in self.transactions:
            if item.type == 'Transfer':
                for pay in item.transfers:
                    if pay[0] == member_hash:
                        balance -= pay[2]
                    if pay[1] == member_hash:
                        balance += pay[2]
        return balance / 1000

    def history_balance(self, member):
        if member is None:
            return None
        member_hash = get_hash_member(member.id)
        for item in self.transactions:
            if item.type == 'Transfer':
                for pay in item.transfers:
                    if pay[1] == member_hash:
                        contract = self.get_contract(item.owner_contract_id)
                        card = self.get_trello_card(contract.parameters_contract[0])
                        speakers = self.get_speakers(item.owner_contract_id)
                        yield PointModel(speakers, card.name, pay[2]/1000)

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
        return False if card is None else card.list_id == '5a03de5bfc228ec8e0608389'

    def run_contracts(self):
        for item in get_open_contracts(self.transactions, get_hash_contract('theme')):
            if item.type == 'Contract':
                result = run_chain_contracts(item, self.theme_is_finished, self.get_child_contracts)
                if result is not None:
                    write_transaction(result)
                    self.transactions.append(result)

    def get_themes_by_user(self, member):
        member_hash = get_hash_member(member.id)
        contracts = get_open_contracts(self.transactions, get_hash_contract('theme'))
        for item in contracts:
            speaker_contract = get_speaker_contract(self.transactions, item.id)
            if speaker_contract is not None and member_hash in speaker_contract.parameters_contract:
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

    def get_speakers(self, theme_contract_id):
        speakers = '(no speaker)'
        speaker_contract = get_speaker_contract(self.transactions, theme_contract_id)
        if speaker_contract is not None:
            speakers_info = []
            for sp in speaker_contract.parameters_contract:
                speakers_info.append(self.get_trello_member(sp).full_name)
                speakers = ', '.join(speakers_info)
        return speakers

    def get_voting_list(self):
        hash_theme_contract = get_hash_contract('theme')
        for item in get_open_contracts(self.transactions, hash_theme_contract):
            if self.get_trello_card(item.parameters_contract[0]).list_id == TrelloProvider.listIncomingId:
                card = self.get_trello_card(item.parameters_contract[0])
                speakers = self.get_speakers(item.id)
                yield VotingModel(item.id, speakers, card.name, item.timestamp, card.url)

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
                speakers = self.get_speakers(item.parent_contract_id)
                yield VotingModel(item.id, speakers, card.name, item.timestamp, card.url)

    def get_all_publications(self):
        sorted_items = sorted(self.transactions, key=sort_transaction)
        for item in sorted_items:
            if item.type == 'Contract' and item.hash_contract == get_hash_contract('publication'):
                parent = self.get_contract(item.parent_contract_id)
                card = self.get_trello_card(parent.parameters_contract[0])
                speakers = self.get_speakers(item.parent_contract_id)
                yield VotingModel(item.id, speakers, card.name,
                                  item.timestamp, card.url)

    def vote(self, form, user):
        for item in form:
            lecture = self.get_contract(item)
            contract = vote(user.id, lecture.id)
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
        publication = self.get_contract(contractId)
        contract = create_feedback_contract(user.id, publication.id, theme_is_actual, can_apply, quality_information, preparedness_author, can_recommend)
        write_transaction(contract)
        self.transactions.append(contract)
        lecture = self.get_contract(publication.parent_contract_id)
        card = self.get_trello_card(lecture.parameters_contract[0])
        card.comment('Feedback: | {} |'.format(' | '.join([str(theme_is_actual), str(can_apply), str(quality_information), str(preparedness_author), str(can_recommend)])))

    def get_info(self):
        sorted_list = sorted(self.transactions, key=sort_transaction)
        hash_theme_contract = get_hash_contract('theme')
        hash_vote_contract = get_hash_contract('vote')
        hash_publication_contract = get_hash_contract('publication')
        hash_feedback_contract = get_hash_contract('feedback')
        hash_speaker_contract = get_hash_contract('speaker')
        for item in sorted_list:
            if item.type == 'Contract':
                # yield  InfoModel(item.timestamp, item.id, 'has parent', item.parent_contract_id)
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
                yield InfoModel(item.timestamp, self.get_trello_member(owner.creator_address).full_name, 'closed',
                                self.get_trello_card(owner.parameters_contract[0]).name)
                for pay in item.transfers:
                    member_from = 'Get' if pay[0] is None else self.get_trello_member(pay[0]).full_name
                    member_to = self.get_trello_member(pay[1]).full_name
                    count = pay[2]
                    yield InfoModel(item.timestamp, member_to, 'gets {} by'.format(count/1000), self.get_trello_card(owner.parameters_contract[0]).name)

    def get_creator_card(self, actions):
        for item in actions:
            if item['type'] == 'createCard':
                return item['idMemberCreator']

    def import_speakers(self, comments):
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



