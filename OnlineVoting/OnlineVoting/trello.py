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

    def __init__(self):
        self.token = None
        self.isAuth = False
        self.client = None

    def auth(self, token):
        self.client = TrelloClient(api_key=self.apiKey,
                                  api_secret=self.apiSecret,
                                  token=token)
        self.token = token
        self.isAuth = True

    def get_board(self):
        if not self.isAuth:
            return None
        return self.client.get_board(self.boardId)

    def get_account_info(self):
        if not self.isAuth:
            return None
        user = self.client.fetch_json('tokens/{0}?token={0}&key={1}'.format(self.token, self.apiKey))
        return self.client.get_member(user['idMember'])

    def get_card(self, cardId):
        if not self.isAuth:
            return None
        return self.client.get_card(cardId)

    def get_all_cards(self):
        if not self.isAuth:
            return None
        return self.get_board().all_cards()

    def get_member(self, memberId):
        if not self.isAuth:
            return None
        return self.client.get_member(memberId)

    def get_all_members(self):
        if not self.isAuth:
            return None
        return self.get_board().get_members()

