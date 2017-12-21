import hashlib as hasher
import datetime as date
import json
from json import JSONEncoder
import time
import os  
from uuid import uuid4
from OnlineVoting.trello import TrelloProvider

def appendContract(contract):
    with open(os.path.join('contracts', str(uuid4())), 'w', encoding='utf8') as f:
        json.dump(contract.as_json(), f, ensure_ascii=False)

def extractContract(cardId, token):
    client = TrelloProvider()
    client.auth(token)
    user = client.getAccountInfo()
    card = client.getCard(cardId)
    if len(card.member_id) > 0:
        owner = client.getMember(str(card.member_id[0]))
    else:
        return
    contract = VotingContract(user.id, user.username, owner.id, owner.username, cardId, card.name)
    appendContract(contract)

class Contract(JSONEncoder):
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


