import hashlib as hasher
import datetime as date
import json
from json import JSONEncoder
import time
import os  
from OnlineVoting.trello import TrelloProvider

def appendContract(contract):
    if (os.path.exists('conracts.data')):
        with open('conracts.data', 'r') as f:
            contracts = json.load(f)
    else:
        contracts = []
    contracts.append(contract.as_json())
    with open('conracts.data', 'w') as f:
        json.dump(contracts, f)

def extractContract(cardId, cardTitle, token):
    client = TrelloProvider()
    client.auth(token)
    user = client.getAccountInfo()
    card = client.getCard(cardId)
    # owner = client.getMember(card.member_id)
    contract = VotingContract(user.id, user.username, card.member_id, 'test', cardId, cardTitle)
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


