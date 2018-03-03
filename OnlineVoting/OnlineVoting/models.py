import datetime


class VotingModel:
    def __init__(self, id, authorName, themeName, timestamp, url):
        self.id = id
        self.authorName = authorName
        self.themeName = themeName
        self.timestamp = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d-%m-%Y %H:%M:%S')
        self.url = url


class InfoModel:
    def __init__(self, timestamp, member, action, data):
        self.timestamp = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d-%m-%Y %H:%M:%S')
        self.member = member
        self.action = action
        self.data = data


class PointModel:
    def __init__(self, username, memberName, count):
        self.username = username
        self.memberName = memberName
        self.count = count


