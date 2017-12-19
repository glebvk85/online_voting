from trello import TrelloClient

class TrelloProvider:

    apiKey = '19f6350892758decb4ede6ae63be78b4'
    apiSecret = 'f7eef63fcf48f860b03e1fa21b08aad977f1b2a3b06c99f73d37d05052dc4737'

    boardId = 'MzDix0uq'
    listIncomingId = '5a1c1baaf6b287cc5d7bf3c0'
    listVotedId = '5a1c1baaf6b287cc5d7bf3c1'
    listLearningId = '5a1c1baaf6b287cc5d7bf3c2'
    listReadyToPublishId = '5a1c1baaf6b287cc5d7bf3c3'
    listPublished = '5a1c1baaf6b287cc5d7bf3c4'
    listIntegrated = '5a1c1baaf6b287cc5d7bf3c5'

    def auth(self, token):
        self.client = TrelloClient(api_key=self.apiKey,
                                  api_secret = self.apiSecret,
                                  token = token)
        self.token = token

    def getBoard(self):
        return self.client.get_board(self.boardId)

    def getIncomingCards(self):
        return self.getBoard().get_list(self.listIncomingId).list_cards()

    def getAccountInfo(self):
        user = self.client.fetch_json('tokens/{0}?token={0}&key={1}'.format(self.token, self.apiKey))
        return self.client.get_member(user['idMember'])

