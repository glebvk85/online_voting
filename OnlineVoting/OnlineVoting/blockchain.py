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
        memberHash = get_hash_member(member.id, member.username)
        count = 0
        for i in get_open_child_contracts(self.transactions, get_hash_contract('vote')):
            if i.creator_address == memberHash:
                count += i.parameters_contract[0]
        maxVotes = 2
        return maxVotes - count

    def get_all_free_votes(self):
        maxVotes = 2
        votes = defaultdict()
        for i in get_open_child_contracts(self.transactions, get_hash_contract('vote')):
            votes.setdefault(i.creator_address, []).append(i.parameters_contract[0])
        for i in self.allMembers:
            hashMember = get_hash_member(i.id, i.username)
            votes.setdefault(hashMember, [])
            yield PointModel(i.username, i.full_name, maxVotes - sum(votes[hashMember]))

    def get_themes_by_user(self, member):
        memberHash = get_hash_member(member.id, member.username)
        contracts = get_open_contracts(self.transactions, get_hash_contract('theme'))
        for item in contracts:
            if item.creator_address == memberHash:
                card = self.get_trello_card(item.parameters_contract[0])
                yield VotingModel(item.id, member.full_name, card.name, item.timestamp, card.short_url)

    def get_contract(self, contractId):
        for item in self.transactions:
            if item.id == contractId:
                return item

    def get_lecture_contract(self, trelloCardId):
        hashContract = get_hash_contract('theme')
        for item in self.transactions:
            if item.type == 'Contract' and item.parameters_contract[0] == trelloCardId and item.hash_contract == hashContract:
                return item

    def get_publication_contract(self, themeContractId):
        hashContract = get_hash_contract('publication')
        for item in self.transactions:
            if item.type == 'ChildContract' and item.parent_contract_id == themeContractId and item.hash_contract == hashContract:
                return item

    def get_feedback(self, publicationContractId, member):
        memberHash = get_hash_member(member.id, member.username)
        hashContract = get_hash_contract('feedback')
        for item in self.transactions:
            if item.type == 'ChildContract' and item.hash_contract == hashContract and item.parent_contract_id == publicationContractId and item.creator_address == memberHash:
                return item

    def get_trello_card(self, trelloCardId):
        for item in self.allCards:
            if item.id == trelloCardId:
                return item

    def get_trello_member(self, memberHash):
        for item in self.allMembers:
            if get_hash_member(item.id, item.username) == memberHash:
                return item

    def get_trello_member_by_trello_id(self, trelloMemberId):
        for item in self.allMembers:
            if item.id == trelloMemberId:
                return item

    def get_voting_list(self):
        hashThemeContract = get_hash_contract('theme')
        for item in get_open_contracts(self.transactions, hashThemeContract):
            if self.get_trello_card(item.parameters_contract[0]).list_id == '59f86fde255ded6e9a366b22':
                card = self.get_trello_card(item.parameters_contract[0])
                yield VotingModel(item.id, self.get_trello_member(item.creator_address).full_name, card.name, item.timestamp, card.url)

    def get_new_publication(self, user):
        member = self.get_trello_member_by_trello_id(user.id)
        memberHash = get_hash_member(member.id, member.username)
        hashPublicationContract = get_hash_contract('publication')
        hashFeedbackContract = get_hash_contract('feedback')
        for item in get_open_child_contracts(self.transactions, hashPublicationContract):
            found = False
            feedbacks = get_open_child_contracts(self.transactions, hashFeedbackContract)
            for j in feedbacks:
                if j.parent_contract_id == item.id and memberHash == j.creator_address:
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
            for item in get_open_child_contracts(self.transactions, get_hash_contract('vote')):
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

    def feedback(self, contractId, user, themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend):
        lecture = self.get_contract(contractId)
        member = self.get_trello_member_by_trello_id(user.id)
        contract = create_feedback_contract(member.id, member.username, lecture.id, themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend)
        write_transaction(contract)
        self.transactions.append(contract)

    def get_info(self):
        sortedList = sorted(self.transactions, key=sort_transaction)
        hashThemeContract = get_hash_contract('theme')
        hashVoteContract = get_hash_contract('vote')
        hashPublicationContract = get_hash_contract('publication')
        hashFeedbackContract = get_hash_contract('feedback')
        for item in sortedList:
            if item.hash_contract == hashThemeContract:
                yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, 'create theme', self.get_trello_card(item.parameters_contract[0]).name)
            if item.hash_contract == hashVoteContract:
                parent = self.get_contract(item.parent_contract_id)
                yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, 'vote', self.get_trello_card(parent.parameters_contract[0]).name)
            if item.hash_contract == hashPublicationContract:
                parent = self.get_contract(item.parent_contract_id)
                yield InfoModel(item.timestamp, self.get_trello_member(item.creator_address).full_name, 'publication', self.get_trello_card(parent.parameters_contract[0]).name)
            if item.hash_contract == hashFeedbackContract:
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




