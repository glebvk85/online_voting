import hashlib as hasher
import datetime as date
import json
import time
import os  
from uuid import uuid4


def appendContract(contract):
    with open(os.path.join('contracts', str(uuid4())), 'w', encoding='utf8') as f:
        json.dump(contract.as_json(), f, ensure_ascii=False)

def extractContract(memberId, memberName, ownerId, ownerName, cardId, cardName):
    contract = VotingContract(memberId, memberName, ownerId, ownerName, cardId, cardName)
    appendContract(contract)

class Contract:
    def __init__(self, version, memberId, memberName):
        self.typeContract =  self.__class__.__name__
        self.memberId = memberId
        self.memberName = memberName
        self.timestamp = str(time.mktime(date.datetime.now().timetuple()))
        self.versionCotract = 1
        
    def as_json(self):
        result = self.__dict__
        return result

class VotingContract(Contract):
    def __init__(self, memberId, memberName, ownerCardMemberId, ownerCardMemberName, cardId, title):
        super(VotingContract, self).__init__(1, memberId, memberName)
        self.countOfVotes = 1
        self.cardId = cardId
        self.title = title
        self.ownerCardMemberId = ownerCardMemberId
        self.ownerCardMemberName = ownerCardMemberName
        
    def as_json(self):
        return super(VotingContract, self).as_json()


