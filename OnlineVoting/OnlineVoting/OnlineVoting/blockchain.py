import hashlib as hasher
import datetime as date
import json
import time
import os  
from uuid import uuid4


def appendContract(contract):
    with open(os.path.join('contracts', str(uuid4())), 'w', encoding='utf8') as f:
        json.dump(contract.as_json(), f, ensure_ascii=False)

def readContract(path_file):
    with open(path_file, 'r', encoding='utf8') as f:
        return json.load(f)

def extractContract(memberId, memberName, ownerId, ownerName, cardId, cardName):
    contract = VotingContract(memberId, memberName, ownerId, ownerName, cardId, cardName)
    appendContract(contract)


class Contract:
    def __init__(self, version):
        self.typeContract =  self.__class__.__name__
        self.timestamp = str(time.mktime(date.datetime.now().timetuple()))
        self.versionContract = version
        
    def as_json(self):
        result = self.__dict__
        return result


class MemberContract(Contract):
    def __init__(self, version, memberId, memberName):
        super(MemberContract, self).__init__(version)
        self.memberId = memberId
        self.memberName = memberName

    def as_json(self):
        return super(MemberContract, self).as_json()


class LectureContract(Contract):
    def __init__(self, ownerCardMemberId, ownerCardMemberName, cardId, title):
        super(LectureContract, self).__init__(1)
        self.cardId = cardId
        self.title = title
        self.ownerCardMemberId = ownerCardMemberId
        self.ownerCardMemberName = ownerCardMemberName

    def as_json(self):
        return super(LectureContract, self).as_json()


class VotingContract(MemberContract):
    def __init__(self, memberId, memberName, cardId):
        super(VotingContract, self).__init__(1, memberId, memberName)
        self.countOfVotes = 1
        self.cardId = cardId
        
    def as_json(self):
        return super(VotingContract, self).as_json()


class PublicationContract(Contract):
    def __init__(self, cardId):
        super(PublicationContract, self).__init__(1)
        self.cardId = cardId

    def as_json(self):
        return super(PublicationContract, self).as_json()


class FeedbackContract(MemberContract):
    def __init__(self, cardId):






class DataBaseSystem:
    def __init__(self):
        self.contracts = []
        for contract in self.get_files_from_directory('contracts'):
            self.contracts.append(readContract(contract))

    def get_files_from_directory(self, path_directory):
        for found_file in os.listdir(path_directory):
            full_path = os.path.join(path_directory, found_file)
            if os.path.isfile(full_path):
                yield full_path

    def free_votes(self, memberId):
        count = 0
        for i in self.contracts:
            if i['typeContract'] == 'VotingContract' and i['memberId'] == memberId:
                count += 1
            if i['typeContract'] == 'PublicationContract' and i['memberId'] == memberId:
                count -= 1
        maxVotes = 2
        return maxVotes - count

    def sync(self, listPublished):
        for i in listPublished:
            pass



