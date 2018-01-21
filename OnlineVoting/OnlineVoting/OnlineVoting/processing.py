
from OnlineVoting.trello import TrelloProvider

def findMember(members, memberId):
    for i in members:
        if i.id == memberId:
            return i

def processVoting(voting, token):
    client = TrelloProvider()
    client.auth(token)
    user = client.getAccountInfo()

    members = client.getMembers()
    for vote in voting:
        card = client.getCard(vote)
        owner = client.findMember(card)
        #extractContract(user.id, user.username, owner.id, owner.username, card.id, card.name)

