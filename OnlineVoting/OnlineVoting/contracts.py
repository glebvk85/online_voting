from OnlineVoting.transactions import *

def CreateThemeContract(trelloMemberId, trelloMemberName, trelloCardId):
    return Contract(GetHashMember(trelloMemberId, trelloMemberName), GetHashContract('theme'), [trelloCardId])


def Vote(trelloMemberId, trelloMemberName, contractId):
    return ChildContract(GetHashMember(trelloMemberId, trelloMemberName), GetHashContract('vote'), contractId, [1])


def CreatePublicationContract(memberHash, contractId):
    return ChildContract(memberHash, GetHashContract('publication'), contractId, [])


def CreateFeedbackContract(trelloMemberId, trelloMemberName, contractId, themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend):
    return ChildContract(GetHashMember(trelloMemberId, trelloMemberName), GetHashContract('feedback'), contractId, [themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend])


def CloseThemeContract(trelloMemberId, trelloMemberName, trelloCardId):
    return ClosingContract(GetHashMember(trelloMemberId, trelloMemberName), contractId, [])


def GetOpenChildContracts(list, hashContract):
    sortedList = sorted(list, key=sortTransaction)
    contracts = []
    closedContracts = set()
    for item in sortedList:
        if item.type == 'ChildContract':
            if item.hash_contract == hashContract:
                contracts.append(item)
        if item.type == 'ClosingContract':
            closedContracts.add(item.parent_contract_id)
    for item in contracts:
        if item.parent_contract_id not in closedContracts:
            yield item


def GetOpenContracts(list, hashContract):
    sortedList = sorted(list, key=sortTransaction)
    contracts = []
    closedContracts = set()
    for item in sortedList:
        if item.type == 'Contract':
            if item.hash_contract == hashContract:
                contracts.append(item)
        if item.type == 'ClosingContract':
            closedContracts.add(item.parent_contract_id)
    for item in contracts:
        if item.id not in closedContracts:
            yield item


def GetHashMember(trelloMemberId, trelloMemberName):
    sha = hasher.sha256()
    sha.update((str(trelloMemberId) + str(trelloMemberName)).encode('utf-8'))
    return sha.hexdigest()


def RunContract(text):
    complete = False
    exec(text)
    i = name_contract


def GetHashContract(nameContract):
    text_contract = None
    with open(os.path.join('OnlineVoting', 'contracts', '{0}.py'.format(nameContract)), 'r') as f:
        text_contract = f.read()
    sha = hasher.sha256()
    sha.update((str(text_contract)).encode('utf-8'))
    return sha.hexdigest()

