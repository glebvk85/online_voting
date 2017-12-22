from trello import TrelloClient

class TrelloProvider:

    apiKey = '19f6350892758decb4ede6ae63be78b4'
    apiSecret = 'f7eef63fcf48f860b03e1fa21b08aad977f1b2a3b06c99f73d37d05052dc4737'

    boardId = 'eisJ9agE'
    listIncomingId = '59f86fde255ded6e9a366b22'
    listVotedId = '5a1c1baaf6b287cc5d7bf3c1'
    listLearningId = '5a1c1baaf6b287cc5d7bf3c2'
    listReadyToPublishId = '5a1c1baaf6b287cc5d7bf3c3'
    listPublished = '5a1c1baaf6b287cc5d7bf3c4'
    listIntegrated = '5a1c1baaf6b287cc5d7bf3c5'

    isAuth = False

    members = None

    def auth(self, token):
        self.client = TrelloClient(api_key=self.apiKey,
                                  api_secret = self.apiSecret,
                                  token = token)
        self.token = token
        self.isAuth = True

    def getBoard(self):
        if not self.isAuth:
            return None
        return self.client.get_board(self.boardId)

    def __findMember(self, memberId):
        for i in self.members:
            if i.id == memberId:
                return i

    def findMember(self, card):
        if len(card.member_id) > 0:
            if self.members is None:
                self.members = self.getMembers()
            owner = self.__findMember(card.member_id[0])
            if owner is None:
                return self.getMember(str(card.member_id[0]))
            else:
                return owner
        else:
            return

    def getIncomingCards(self):
        if not self.isAuth:
            return None
        result = self.getBoard().get_list(self.listIncomingId).list_cards()
        for i in result:
            i.member_username = self.findMember(i).full_name
        return result

    def getAccountInfo(self):
        if not self.isAuth:
            return None
        user = self.client.fetch_json('tokens/{0}?token={0}&key={1}'.format(self.token, self.apiKey))
        return self.client.get_member(user['idMember'])

    def getCard(self, cardId):
        if not self.isAuth:
            return None
        return self.client.get_card(cardId)

    def getMember(self, memberId):
        if not self.isAuth:
            return None
        return self.client.get_member(memberId)

    def getMembers(self):
        if not self.isAuth:
            return None
        board = self.getBoard()
        return board.get_members()


