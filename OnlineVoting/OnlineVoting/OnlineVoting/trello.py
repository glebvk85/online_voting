from trello import TrelloClient

class TrelloProvider:

    apiKey = '19f6350892758decb4ede6ae63be78b4'
    apiSecret = 'f7eef63fcf48f860b03e1fa21b08aad977f1b2a3b06c99f73d37d05052dc4737'

    boardId = 'eisJ9agE'
    listIncomingId = '59f86fde255ded6e9a366b22'
    listVotedId = '5a028c8e14a7f0baebaf95b3'
    listLearningId = '59f871297f5a2f912f33c506'
    listReadyToPublishId = '59f87147fd63ab917ebfb139'
    listPublishingId = '5a3374a74d2abc862d23a39d'
    listPublishedId = '5a03de5bfc228ec8e0608389'
    listIntegratedId = '59f871749dbbcc90cb18a0c4'

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
        return self._getListCards(self.listIncomingId)

    def getPublishedCards(self):
        return self._getListCards(self.listPublishedId)

    def _getListCards(self, listId):
        if not self.isAuth:
            return None
        result = self.getBoard().get_list(listId).list_cards()
        for i in result:
            member = self.findMember(i)
            if member is None:
                i.member_username = ""
            else:
                i.member_username = member.full_name
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


