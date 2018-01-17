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
        return Contract(j = f)


class Contract:
    def __init__(self, version = None, j = None):
        if version is not None:
            self.typeContract =  self.__class__.__name__
            self.timestamp = str(time.mktime(date.datetime.now().timetuple()))
            self.versionContract = version
        elif j is not None:
            self.__dict__ = json.load(j)
        else:
            raise SyntaxError('Incorrect call');
        
    def as_json(self):
        result = self.__dict__
        return result


class MemberContract(Contract):
    def __init__(self, memberId, memberName, memberTitle):
        super(MemberContract, self).__init__(1)
        self.memberId = memberId
        self.memberName = memberName
        self.memberTitle = memberTitle

    def as_json(self):
        return super(MemberContract, self).as_json()


class LectureContract(Contract):
    def __init__(self, ownerCardMemberId, ownerCardMemberName, ownerCardMemberTitle, cardId, title):
        super(LectureContract, self).__init__(version = 1)
        self.cardId = cardId
        self.title = title
        self.ownerCardMemberId = ownerCardMemberId
        self.ownerCardMemberName = ownerCardMemberName
        self.ownerCardMemberTitle = ownerCardMemberTitle

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
        pass





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
        for item in self.contracts:
            if item.typeContract == 'VotingContract' and item.memberId == memberId:
                count += 1
            if item.typeContract == 'PublicationContract' and item.memberId == memberId:
                count -= 1
        maxVotes = 2
        return maxVotes - count

    def sync(self, listPublished):
        for i in listPublished:
            pass

    def get_lecture_contract(self, cardId):
        for item in self.contracts:
            if item.typeContract == 'LectureContract' and item.cardId == cardId:
                return item
        return None

    def get_member(self, memberId):
        for item in self.contracts:
            if item.typeContract == 'MemberContract' and item.memberId == memberId:
                return item
        return None

    def sync_new_members(self, trello):
        listMembers = trello.getMembers()
        for item in listMembers:
            member = self.get_member(item.id)
            if member is None:
                member = MemberContract(item.id, item.username, item.full_name)
                appendContract(member)


    def sync_new_lectures(self, trello):
        listIncoming = trello.getIncomingCards()
        cards = []
        for item in listIncoming:
            card = self.get_lecture_contract(item.id)
            if card is None:
                owner = trello.findMember(item)
                if owner is not None:
                    contract = LectureContract(owner.id, owner.username, owner.full_name, item.id, item.name)
                    appendContract(contract)
                    cards.append(contract)
            else:
                cards.append(card)
        return cards




