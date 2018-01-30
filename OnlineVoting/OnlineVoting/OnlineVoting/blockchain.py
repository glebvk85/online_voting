import hashlib as hasher
import datetime as date
import json
import time
import os  
from uuid import uuid4
from collections import defaultdict


def appendTransaction(transaction):
    with open(os.path.join('transactions', transaction.id), 'w', encoding='utf8') as f:
        json.dump(transaction.as_json(), f, ensure_ascii=False)

def readTransaction(path_file):
    with open(path_file, 'r', encoding='utf8') as f:
        return Transaction(j = f)

def sortTransaction(contract):
    return contract.timestamp

class Transaction:
    def __init__(self, version = None, j = None):
        if version is not None:
            self.id = str(uuid4())
            self.type =  self.__class__.__name__
            self.timestamp = int(time.mktime(date.datetime.now().timetuple()))
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


def GetHashMember(trelloMemberId, trelloMemberName):
    sha = hasher.sha256()
    sha.update((str(trelloMemberId) + str(trelloMemberName)).encode('utf-8'))
    return sha.hexdigest()

def RunContract(text):
    complete = False
    exec(text)
    i = name_contract

def GetHashContract(nameContract):
    text_contract = None
    with open(os.path.join('OnlineVoting', 'contracts', '{0}.py'.format(nameContract)), 'r') as f:
        text_contract = f.read()
    sha = hasher.sha256()
    sha.update((str(text_contract)).encode('utf-8'))
    return sha.hexdigest()

def CreateThemeContract(trelloMemberId, trelloMemberName, trelloCardId):
    return Contract(GetHashMember(trelloMemberId, trelloMemberName), GetHashContract('theme'), [trelloCardId])

def Vote(trelloMemberId, trelloMemberName, contractId):
    return ChildContract(GetHashMember(trelloMemberId, trelloMemberName), GetHashContract('vote'), contractId, [1])

def CreatePublicationContract(memberHash, contractId):
    return ChildContract(memberHash, GetHashContract('publication'), contractId, [])

def CreateFeedbackContract(trelloMemberId, trelloMemberName, contractId, themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend):
    return ChildContract(GetHashMember(trelloMemberId, trelloMemberName), GetHashContract('feedback'), contractId, [themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend])

def CloseThemeContract(trelloMemberId, trelloMemberName, trelloCardId):
    return ClosingContract(GetHashMember(trelloMemberId, trelloMemberName), contractId, [])



class VotingModel:
    def __init__(self, id, authorName, themeName, timestamp, url):
        self.id = id
        self.authorName = authorName
        self.themeName = themeName
        self.timestamp = date.datetime.fromtimestamp(int(timestamp)).strftime('%d-%m-%Y %H:%M:%S')
        self.url = url

class InfoModel:
    def __init__(self, timestamp, member, action, data):
        self.timestamp = date.datetime.fromtimestamp(int(timestamp)).strftime('%d-%m-%Y %H:%M:%S')
        self.member = member
        self.action = action
        self.data = data



def GetOpenChildContracts(list, hashContract):
    sortedList = sorted(list, key=sortTransaction)
    contracts = []
    closedContracts = set()
    for item in sortedList:
        if item.type == 'ChildContract':
            if item.hash_contract == hashContract:
                contracts.append(item)
        if item.type == 'ClosingContract':
            closedContracts.add(item.parent_contract_id)
    for item in contracts:
        if item.parent_contract_id not in closedContracts:
            yield item


def GetOpenContracts(list, hashContract):
    sortedList = sorted(list, key=sortTransaction)
    contracts = []
    closedContracts = set()
    for item in sortedList:
        if item.type == 'Contract':
            if item.hash_contract == hashContract:
                contracts.append(item)
        if item.type == 'ClosingContract':
            closedContracts.add(item.parent_contract_id)
    for item in contracts:
        if item.id not in closedContracts:
            yield item


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

    # temporary

    def get_voting_by_member_and_lecture(self, trelloCardId, trelloMemberId):
        member = self.get_trello_member_by_trello_id(trelloMemberId)
        lecture = self.get_lecture_contract(trelloCardId)
        if member is None or lecture is None:
            return None
        hashVoteContract = GetHashContract('vote')
        memberHash = GetHashMember(member.id, member.username)
        for item in self.transactions:
            if item.type == 'ChildContract' and item.hash_contract == hashVoteContract and memberHash == item.creator_address and lecture.id == item.parent_contract_id:
                return item

    def add_voting(self):
        temp = [('59f8cda85fad9eab697155e6','583ebed850e2f6dda2f0740e'),
                ('5a014cd62ef34efb97f3ec63','580ee2cc503dabc477f48b30'),
                ('5a014cd62ef34efb97f3ec63','58e4e28b768539fe28c0db69'),
                ('5a03dc36e173e0f22440c1c4','56166acbe42b8784b493f499'),
                ('59f9aac98e5716aeacbc0402','55e6b1c8de29447a10503b4d'),
                ('59f9517d13a22153205b6c86','58cf6bbdb5ad126ff7c90493'),
                ('59f9517d13a22153205b6c86','5950f9d05e029db06d708dd1'),
                ('5a0153e71a0b80532d24c1ca','58cf6bbdb5ad126ff7c90493'),
                ('5a0153e71a0b80532d24c1ca','580ee2cc503dabc477f48b30'),
                ('5a0153e71a0b80532d24c1ca','58eb69cd4705fa27d8688752'),
                ('5a0153e71a0b80532d24c1ca','5791ce343890b24d1d30a654'),
                ('59fb0458b93221eea6cdeb70','5791ce343890b24d1d30a654'),
                ('59f8868815a5f56eb92c5bfd','563dfbf76c439c6464b295a8'),
                ('59fb0bb7a26c0519889a8c4d','56166b31aad8642b07fc4035'),
                ('5a03dc22afc095c59a36d8dd','56166acbe42b8784b493f499'),
                ('59f9539795bf402b0d745ded','5534d4b000faca070c8887d2'),
                ('59f9539795bf402b0d745ded','56d6ba21c234a7edf72880cc'),
                ('59f9539795bf402b0d745ded','5908be1e35ca99d089cf1be1'),
                ('59f9539795bf402b0d745ded','58eb69cd4705fa27d8688752'),
                ('59f8cf2c324c8361d671ed13','59568011a4432b4bd9e96a23'),
                ('59f8cf2c324c8361d671ed13','5534d4b000faca070c8887d2'),
                ('59f9ac62dbb06468a0e29f77','56d6ba21c234a7edf72880cc'),
                ('59f9ac62dbb06468a0e29f77','59568011a4432b4bd9e96a23'),
                ('59f9ac62dbb06468a0e29f77','583ebed850e2f6dda2f0740e'),
                ('59f9ac62dbb06468a0e29f77','563dfbf76c439c6464b295a8'),
                ('59f993a9efe2c178dfecb947','58eb69cd4705fa27d8688752'),
                ('59f993a9efe2c178dfecb947','56166b31aad8642b07fc4035'),
                ('59f9ad8305380dffe0594299','58e4e28b768539fe28c0db69'),
                ('59f9ad8305380dffe0594299','55e6b1c8de29447a10503b4d')]
        for i in temp:
            lecture = self.get_lecture_contract(i[0])
            member = self.get_trello_member_by_trello_id(i[1])
            voting = self.get_voting_by_member_and_lecture(i[0], i[1])
            if voting is None:
                contract = Vote(member.id, member.username, lecture.id)
                contract.timestamp = int(time.mktime(date.datetime.strptime('09-10-2017 07:42:00', '%d-%m-%Y %H:%M:%S').timetuple()))
                appendTransaction(contract)
                self.transactions.append(contract)

    def add_publication(self):
        temp = [('59f9539795bf402b0d745ded',
        [('58e4e28b768539fe28c0db69',	10	,10	,10	,10	,10),
        ('56166acbe42b8784b493f499',	8	,9	,6	,6	,10),
        ('58eb69cd4705fa27d8688752',	9	,9	,7	,8	,10),
        ('5950f9d05e029db06d708dd1',	8	,8	,9	,8	,9 ),
        ('5926f843cfd6a8a4380b0975',	8	,8	,10	,9	,10),
        ('55e91e3e95a44b9d0645cf31',	9	,8	,6	,7	,9 ),
        ('543b7148b9bb86843b4b9955',	9	,10	,8	,8	,8 ),
        ('595492dc6a00fd4a576b432d',	10	,10	,9	,9	,10),
        ('56166b31aad8642b07fc4035',	7	,7	,10	,9	,9 )]),
        
        ('59f9517d13a22153205b6c86',
        [('5926f843cfd6a8a4380b0975',	8	,9	,9	,8	,10),
        ('543b7148b9bb86843b4b9955',	8	,10	,6	,4	,8 ),
        ('56166b31aad8642b07fc4035',	6	,5	,7	,7	,6 ),
        ('595492dc6a00fd4a576b432d',	7	,6	,8	,7	,8 ),
        ('56166acbe42b8784b493f499',	6	,6	,7	,6	,9 ),
        ('5950f9d05e029db06d708dd1',	9	,9	,7	,9	,9 ),
        ('58eb69cd4705fa27d8688752',	8	,8	,9	,8	,10),
        ('580ee2cc503dabc477f48b30',	7	,8	,9	,8	,10),
        ('5926f843cfd6a8a4380b0975',	10	,10	,10	,10	,10),
        ('563dfbf76c439c6464b295a8',	10	,10	,10	,8	,10),
        ('58eb69cd4705fa27d8688752',	5	,5	,9	,9	,9 )]),

        ('59f993a9efe2c178dfecb947',
        [('5926f843cfd6a8a4380b0975',	8	,9	,9	,8	,10),
        ('543b7148b9bb86843b4b9955',	8	,10	,6	,4	,8 ),
        ('56166b31aad8642b07fc4035',	6	,5	,7	,7	,6 ),
        ('595492dc6a00fd4a576b432d',	7	,6	,8	,7	,8 ),
        ('56166acbe42b8784b493f499',	6	,6	,7	,6	,9 ),
        ('5950f9d05e029db06d708dd1',	9	,9	,7	,9	,9 ),
        ('58eb69cd4705fa27d8688752',	8	,8	,9	,8	,10),
        ('580ee2cc503dabc477f48b30',	7	,8	,9	,8	,10),
        ('5908be1e35ca99d089cf1be1',	7	,7	,9	,8	,8 ),
        ('56d6ba21c234a7edf72880cc',	6	,7	,10	,7	,8 ),
        ('58e4e28b768539fe28c0db69',	7	,7	,9	,9	,9 ),
        ('583ebed850e2f6dda2f0740e',	10	,10	,10	,10	,10),
        ('580ee2cc503dabc477f48b30',	6	,6	,8	,8	,10),
        ('547c4ea5bab38bfebcc6a241',	8	,5	,6	,7	,7 ),
        ('595492dc6a00fd4a576b432d',	7	,7	,8	,8	,8 ),
        ('543b7148b9bb86843b4b9955',	8	,9	,9	,9	,9 ),
        ('56166b31aad8642b07fc4035',	7	,7	,9	,9	,9 )])]
        for i in temp:
            lecture = self.get_lecture_contract(i[0])
            publication = self.get_publication_contract(lecture.id)
            if publication is None:
                publication = CreatePublicationContract(lecture.creator_address, lecture.id)
                appendTransaction(publication)
                self.transactions.append(publication)
            for j in i[1]:
                member = self.get_trello_member_by_trello_id(j[0])
                feedback = self.get_feedback(publication.id, member)
                if feedback is None:
                    feedback = CreateFeedbackContract(member.id, member.username, publication.id, j[1], j[2], j[3], j[4], j[5])
                    appendTransaction(feedback)
                    self.transactions.append(feedback)
    
    # TODO: set dates for feedback, my feedbacks, get author


    def sync_lectures(self):
        # sync new lectures
        for item in self.allCards:
            contract = self.get_lecture_contract(item.id)
            if contract is None:
                if len(item.member_id) > 0:
                    member = self.get_trello_member_by_trello_id(item.member_id[0])
                    if member is not None:
                        contract = CreateThemeContract(member.id, member.username, item.id)
                        contract.timestamp = int(time.mktime(item.card_created_date.timetuple())) 
                        appendTransaction(contract)
                        self.transactions.append(contract)
        # sync votes
        self.add_voting()
        # sync publication
        # self.add_publication()





