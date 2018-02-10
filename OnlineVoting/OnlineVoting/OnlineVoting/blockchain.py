import hashlib as hasher
import datetime as date
import json
import time
import os  
from uuid import uuid4
from collections import defaultdict
from transactions import *
from contracts import *
from models import *


class DataBaseSystem:
    def __init__(self, trello):
        self.transactions = []
        for transactionPath in self.get_files_from_directory('transactions'):
            self.transactions.append(readTransaction(transactionPath))
        self.allCards = trello.getAllCards()
        self.allMembers = trello.getMembers()

    def get_files_from_directory(self, path_directory):
        for found_file in os.listdir(path_directory):
            full_path = os.path.join(path_directory, found_file)
            if os.path.isfile(full_path):
                yield full_path

    def free_votes(self, member):
        if member is None:
            return None
        memberHash = GetHashMember(member.id, member.username)
        count = 0
        for i in GetOpenChildContracts(self.transactions, GetHashContract('vote')):
            if i.creator_address == memberHash:
                count += i.parameters_contract[0]
        maxVotes = 2
        return maxVotes - count

    def get_all_free_votes(self):
        maxVotes = 2
        votes = defaultdict()
        for i in GetOpenChildContracts(self.transactions, GetHashContract('vote')):
            votes.setdefault(i.creator_address, []).append(i.parameters_contract[0])
        for i in self.allMembers:
            hashMember = GetHashMember(i.id, i.username)
            votes.setdefault(hashMember, [])
            yield PointModel(i.username, i.full_name, maxVotes - sum(votes[hashMember]))

    def get_themes_by_user(self, member):
        memberHash = GetHashMember(member.id, member.username)
        contracts = GetOpenContracts(self.transactions, GetHashContract('theme'))
        for item in contracts:
            if item.creator_address == memberHash:
                card = self.get_trello_card(item.parameters_contract[0])
                yield VotingModel(item.id, member.full_name, card.name, item.timestamp, card.short_url)

    def get_contract(self, contractId):
        for item in self.transactions:
            if item.id == contractId:
                return item

    def get_lecture_contract(self, trelloCardId):
        hashContract = GetHashContract('theme')
        for item in self.transactions:
            if item.type == 'Contract' and item.parameters_contract[0] == trelloCardId and item.hash_contract == hashContract:
                return item

    def get_publication_contract(self, themeContractId):
        hashContract = GetHashContract('publication')
        for item in self.transactions:
            if item.type == 'ChildContract' and item.parent_contract_id == themeContractId and item.hash_contract == hashContract:
                return item

    def get_feedback(self, publicationContractId, member):
        memberHash = GetHashMember(member.id, member.username)
        hashContract = GetHashContract('feedback')
        for item in self.transactions:
            if item.type == 'ChildContract' and item.hash_contract == hashContract and item.parent_contract_id == publicationContractId and item.creator_address == memberHash:
                return item

    def get_trello_card(self, trelloCardId):
        for item in self.allCards:
            if item.id == trelloCardId:
                return item

    def get_trello_member(self, memberHash):
        for item in self.allMembers:
            if GetHashMember(item.id, item.username) == memberHash:
                return item

    def get_trello_member_by_trello_id(self, trelloMemberId):
        for item in self.allMembers:
            if item.id == trelloMemberId:
                return item

    def get_voting_list(self):
        hashThemeContract = GetHashContract('theme')
        for item in GetOpenContracts(self.transactions, hashThemeContract):
            if self.get_trello_card(item.parameters_contract[0]).list_id == '59f86fde255ded6e9a366b22':
                card = self.get_trello_card(item.parameters_contract[0])
                yield VotingModel(item.id, self.get_trello_member(item.creator_address).full_name, card.name, item.timestamp, card.url)

    def get_new_publication(self, user):
        member = self.get_trello_member_by_trello_id(user.id)
        memberHash = GetHashMember(member.id, member.username)
        hashPublicationContract = GetHashContract('publication')
        hashFeedbackContract = GetHashContract('feedback')
        for item in GetOpenChildContracts(self.transactions, hashPublicationContract):
            found = False
            feedbacks = GetOpenChildContracts(self.transactions, hashFeedbackContract)
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
            contract = Vote(member.id, member.username, lecture.id)
            appendTransaction(contract)
            self.transactions.append(contract)
            card = self.get_trello_card(lecture.parameters_contract[0])
            title = card.name.lstrip('(👍) ')
            cnt = 0
            for item in GetOpenChildContracts(self.transactions, GetHashContract('vote')):
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
            contract = CreatePublicationContract(GetHashMember(member.id, member.username), lecture.id)
            appendTransaction(contract)
            self.transactions.append(contract)

    def feedback(self, contractId, user, themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend):
        lecture = self.get_contract(contractId)
        member = self.get_trello_member_by_trello_id(user.id)
        contract = CreateFeedbackContract(member.id, member.username, lecture.id, themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend)
        appendTransaction(contract)
        self.transactions.append(contract)

    def get_info(self):
        sortedList = sorted(self.transactions, key=sortTransaction)
        hashThemeContract = GetHashContract('theme')
        hashVoteContract = GetHashContract('vote')
        hashPublicationContract = GetHashContract('publication')
        hashFeedbackContract = GetHashContract('feedback')
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
                        contract = CreateThemeContract(member.id, member.username, item.id)
                        contract.timestamp = int(time.mktime(item.card_created_date.timetuple())) 
                        appendTransaction(contract)
                        self.transactions.append(contract)




