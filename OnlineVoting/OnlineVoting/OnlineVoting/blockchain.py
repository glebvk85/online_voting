import hashlib as hasher
import datetime as date
import json
import time
import os  
from uuid import uuid4


def appendContract(contract):
    with open(os.path.join('contracts', contract.id), 'w', encoding='utf8') as f:
        json.dump(contract.as_json(), f, ensure_ascii=False)

def readContract(path_file):
    with open(path_file, 'r', encoding='utf8') as f:
        return Contract(j = f)

def sortContract(contract):
    return contract.timestamp

class Contract:
    def __init__(self, version = None, j = None):
        if version is not None:
            self.id = str(uuid4())
            self.typeContract =  self.__class__.__name__
            self.timestamp = str(time.mktime(date.datetime.now().timetuple()))
            self.versionContract = version
        elif j is not None:
            self.__dict__ = json.load(j)
        else:
            raise SyntaxError('Incorrect call');
        
    def as_json(self):
        return self.__dict__


class MemberContract(Contract):
    def __init__(self, trelloMemberId, trelloMemberName, trelloMemberFullName):
        super(MemberContract, self).__init__(version = 1)
        self.trelloMemberId = trelloMemberId
        self.trelloMemberName = trelloMemberName
        self.trelloMemberFullName = trelloMemberFullName

    def as_json(self):
        return super(MemberContract, self).as_json()


class LectureContract(Contract):
    def __init__(self, ownerMemberContractId, trelloCardId, trelloTitle):
        super(LectureContract, self).__init__(version = 1)
        self.ownerMemberContractId = ownerMemberContractId
        self.trelloCardId = trelloCardId
        self.trelloTitle = trelloTitle

    def as_json(self):
        return super(LectureContract, self).as_json()


class VotingContract(Contract):
    def __init__(self, memberContractId, lectureContractId):
        super(VotingContract, self).__init__(version = 1)
        self.countOfVotes = 1
        self.memberContractId = memberContractId
        self.lectureContractId = lectureContractId
        
    def as_json(self):
        return super(VotingContract, self).as_json()


class CloseVotingContract(Contract):
    def __init__(self, lectureContractId):
        super(CloseVotingContract, self).__init__(version = 1)
        self.lectureContractId = lectureContractId
        
    def as_json(self):
        return super(CloseVotingContract, self).as_json()


class PublicationContract(Contract):
    def __init__(self, lectureContractId):
        super(PublicationContract, self).__init__(version = 1)
        self.lectureContractId = lectureContractId

    def as_json(self):
        return super(PublicationContract, self).as_json()


class FeedbackContract(Contract):
    def __init__(self, publicationContractId, memberContractId, themeIsActual, canApply, qualityInformation, preparednessAuthor, canRecommend):
        super(FeedbackContract, self).__init__(version = 1)
        self.publicationContractId = publicationContractId
        self.memberContractId = memberContractId
        self.themeIsActual = themeIsActual
        self.canApply = canApply
        self.qualityInformation = qualityInformation
        self.preparednessAuthor = preparednessAuthor
        self.canRecommend = canRecommend

    def as_json(self):
        return super(FeedbackContract, self).as_json()


class ClosingLectureContract(Contract):
    def __init__(self, lectureContractId):
        super(ClosingLectureContract, self).__init__(version = 1)
        self.lectureContractId = lectureContractId

    def as_json(self):
        return super(ClosingLectureContract, self).as_json()


class VotingModel:
    def __init__(self, id, authorName, themeName):
        self.id = id
        self.authorName = authorName
        self.themeName = themeName


class DataBaseSystem:
    def __init__(self):
        self.contracts = []
        for contract in self.get_files_from_directory('contracts'):
            self.contracts.append(readContract(contract))

    def get_files_from_directory(self, path_directory):
        for found_file in os.listdir(path_directory):
            full_path = os.path.join(path_directory, found_file)
            if os.path.isfile(full_path):
                yield full_path

    def free_votes(self, memberId):
        return 0
        count = 0
        for item in self.contracts:
            if item.memberId == memberId:
                if item.typeContract == 'VotingContract':
                    count += 1
                if item.typeContract == 'ClosingLectureContract':
                    count -= 1
        maxVotes = 2
        return maxVotes - count

    def get_lecture_contract(self, trelloCardId):
        for item in self.contracts:
            if item.typeContract == 'LectureContract' and item.trelloCardId == trelloCardId:
                return item

    def get_member(self, trelloMemberId):
        for item in self.contracts:
            if item.typeContract == 'MemberContract' and item.trelloMemberId == trelloMemberId:
                return item

    def get_voting_by_member_and_lecture(self, trelloCardId, trelloMemberId):
        member = self.get_member(trelloMemberId)
        lecture = self.get_lecture_contract(trelloCardId)
        if member is None or lecture is None:
            return None
        for item in self.contracts:
            if item.typeContract == 'VotingContract' and member.id == item.memberContractId and lecture.id == item.lectureContractId:
                return item

    def get_publication(self, lectureContractId):
        for i in self.contracts:
            if i.typeContract == 'PublicationContract' and i.lectureContractId == lectureContractId:
                return i

    def get_feedback(self, publicationContractId, memberContractId):
        for i in self.contracts:
            if i.typeContract == 'FeedbackContract' and i.publicationContractId == publicationContractId and i.memberContractId == memberContractId:
                return i

    def get_contract(self, typeContract, id):
        for item in self.contracts:
            if item.typeContract == typeContract and item.id == id:
                return item

    def get_contracts(self, typeContract):
        for item in self.contracts:
            if item.typeContract == typeContract:
                yield item

    def get_voting_list(self):
        sortedContracts = sorted(self.contracts, key=sortContract)
        for item in sortedContracts:
            if item.typeContract == 'LectureContract':
                result = False
                for item2 in self.contracts:
                    if item2.typeContract == 'CloseVotingContract' and item.id == item2.lectureContractId:
                        result = True
                        break
                if not result:
                    yield VotingModel(item.id, self.get_contract('MemberContract', item.ownerMemberContractId).trelloMemberFullName, item.trelloTitle)

    def sync_members(self, trello):
        listMembers = trello.getMembers()
        for item in listMembers:
            member = self.get_member(item.id)
            if member is None:
                contract = MemberContract(item.id, item.username, item.full_name)
                appendContract(contract)
                self.contracts.append(contract)


    def add_voting(self):
        temp = [('59f8cda85fad9eab697155e6','583ebed850e2f6dda2f0740e'),
                ('5a014cd62ef34efb97f3ec63','580ee2cc503dabc477f48b30'),
                ('5a014cd62ef34efb97f3ec63','58e4e28b768539fe28c0db69'),
                ('5a03dc36e173e0f22440c1c4','56166acbe42b8784b493f499'),
                ('59f9aac98e5716aeacbc0402','55e6b1c8de29447a10503b4d'),
                ('59f9517d13a22153205b6c86','58cf6bbdb5ad126ff7c90493'),
                ('59f9517d13a22153205b6c86','5950f9d05e029db06d708dd1'),
                ('5a0153e71a0b80532d24c1ca','58cf6bbdb5ad126ff7c90493'),
                ('5a0153e71a0b80532d24c1ca','580ee2cc503dabc477f48b30'),
                ('5a0153e71a0b80532d24c1ca','58eb69cd4705fa27d8688752'),
                ('5a0153e71a0b80532d24c1ca','5791ce343890b24d1d30a654'),
                ('59fb0458b93221eea6cdeb70','5791ce343890b24d1d30a654'),
                ('59f8868815a5f56eb92c5bfd','563dfbf76c439c6464b295a8'),
                ('59fb0bb7a26c0519889a8c4d','56166b31aad8642b07fc4035'),
                ('5a03dc22afc095c59a36d8dd','56166acbe42b8784b493f499'),
                ('59f9539795bf402b0d745ded','5534d4b000faca070c8887d2'),
                ('59f9539795bf402b0d745ded','56d6ba21c234a7edf72880cc'),
                ('59f9539795bf402b0d745ded','5908be1e35ca99d089cf1be1'),
                ('59f9539795bf402b0d745ded','58eb69cd4705fa27d8688752'),
                ('59f8cf2c324c8361d671ed13','59568011a4432b4bd9e96a23'),
                ('59f8cf2c324c8361d671ed13','5534d4b000faca070c8887d2'),
                ('59f9ac62dbb06468a0e29f77','56d6ba21c234a7edf72880cc'),
                ('59f9ac62dbb06468a0e29f77','59568011a4432b4bd9e96a23'),
                ('59f9ac62dbb06468a0e29f77','583ebed850e2f6dda2f0740e'),
                ('59f9ac62dbb06468a0e29f77','563dfbf76c439c6464b295a8'),
                ('59f993a9efe2c178dfecb947','58eb69cd4705fa27d8688752'),
                ('59f993a9efe2c178dfecb947','56166b31aad8642b07fc4035'),
                ('59f9ad8305380dffe0594299','58e4e28b768539fe28c0db69'),
                ('59f9ad8305380dffe0594299','55e6b1c8de29447a10503b4d')]
        for i in temp:
            lecture = self.get_lecture_contract(i[0])
            member = self.get_member(i[1])
            voting = self.get_voting_by_member_and_lecture(i[0], i[1])
            if voting is None:
                contract = VotingContract(member.id, lecture.id)
                appendContract(contract)
                self.contracts.append(contract)

    def add_publication(self):
        temp = [('59f9539795bf402b0d745ded',
        [('58e4e28b768539fe28c0db69',	10	,10	,10	,10	,10),
        ('56166acbe42b8784b493f499',	8	,9	,6	,6	,10),
        ('58eb69cd4705fa27d8688752',	9	,9	,7	,8	,10),
        ('5950f9d05e029db06d708dd1',	8	,8	,9	,8	,9 ),
        ('5926f843cfd6a8a4380b0975',	8	,8	,10	,9	,10),
        ('55e91e3e95a44b9d0645cf31',	9	,8	,6	,7	,9 ),
        ('543b7148b9bb86843b4b9955',	9	,10	,8	,8	,8 ),
        ('595492dc6a00fd4a576b432d',	10	,10	,9	,9	,10),
        ('56166b31aad8642b07fc4035',	7	,7	,10	,9	,9 )]),
        
        ('59f9517d13a22153205b6c86',
        [('5926f843cfd6a8a4380b0975',	8	,9	,9	,8	,10),
        ('543b7148b9bb86843b4b9955',	8	,10	,6	,4	,8 ),
        ('56166b31aad8642b07fc4035',	6	,5	,7	,7	,6 ),
        ('595492dc6a00fd4a576b432d',	7	,6	,8	,7	,8 ),
        ('56166acbe42b8784b493f499',	6	,6	,7	,6	,9 ),
        ('5950f9d05e029db06d708dd1',	9	,9	,7	,9	,9 ),
        ('58eb69cd4705fa27d8688752',	8	,8	,9	,8	,10),
        ('580ee2cc503dabc477f48b30',	7	,8	,9	,8	,10),
        ('5926f843cfd6a8a4380b0975',	10	,10	,10	,10	,10),
        ('563dfbf76c439c6464b295a8',	10	,10	,10	,8	,10),
        ('58eb69cd4705fa27d8688752',	5	,5	,9	,9	,9 )]),

        ('59f993a9efe2c178dfecb947',
        [('5926f843cfd6a8a4380b0975',	8	,9	,9	,8	,10),
        ('543b7148b9bb86843b4b9955',	8	,10	,6	,4	,8 ),
        ('56166b31aad8642b07fc4035',	6	,5	,7	,7	,6 ),
        ('595492dc6a00fd4a576b432d',	7	,6	,8	,7	,8 ),
        ('56166acbe42b8784b493f499',	6	,6	,7	,6	,9 ),
        ('5950f9d05e029db06d708dd1',	9	,9	,7	,9	,9 ),
        ('58eb69cd4705fa27d8688752',	8	,8	,9	,8	,10),
        ('580ee2cc503dabc477f48b30',	7	,8	,9	,8	,10),
        ('5908be1e35ca99d089cf1be1',	7	,7	,9	,8	,8 ),
        ('56d6ba21c234a7edf72880cc',	6	,7	,10	,7	,8 ),
        ('58e4e28b768539fe28c0db69',	7	,7	,9	,9	,9 ),
        ('583ebed850e2f6dda2f0740e',	10	,10	,10	,10	,10),
        ('580ee2cc503dabc477f48b30',	6	,6	,8	,8	,10),
        ('547c4ea5bab38bfebcc6a241',	8	,5	,6	,7	,7 ),
        ('595492dc6a00fd4a576b432d',	7	,7	,8	,8	,8 ),
        ('543b7148b9bb86843b4b9955',	8	,9	,9	,9	,9 ),
        ('56166b31aad8642b07fc4035',	7	,7	,9	,9	,9 )])]
        for i in temp:
            lecture = self.get_lecture_contract(i[0])
            publication = self.get_publication(lecture.id)
            if publication is None:
                publication = PublicationContract(lecture.id)
                appendContract(publication)
                self.contracts.append(publication)
            for j in i[1]:
                member = self.get_member(j[0])
                feedback = self.get_feedback(publication.id, member.id)
                if feedback is None:
                    feedback = FeedbackContract(publication.id, member.id, j[1], j[2], j[3], j[4], j[5])
                    appendContract(feedback)
                    self.contracts.append(feedback)

    def vote(self, form, user):
        for vote in form:
            lecture = self.get_contract('LectureContract', vote)
            member = self.get_member(user.id)
            contract = VotingContract(member.id, lecture.id)
            appendContract(contract)
            self.contracts.append(contract)

    def sync_lectures(self, trello):
        listIncoming = trello.getAllCards()
        # sync new lectures
        for item in listIncoming:
            contract = self.get_lecture_contract(item.id)
            if contract is None:
                if len(item.member_id) > 0:
                    owner = self.get_member(item.member_id[0])
                    if owner is not None:
                        contract = LectureContract(owner.id, item.id, item.name)
                        appendContract(contract)
                        self.contracts.append(contract)
        # sync votes
        self.add_voting()
        # close contracts
        for item in listIncoming:
            contract = self.get_lecture_contract(item.id)
            if contract is not None and item.list_id != trello.listIncomingId:
                result = False
                for item in self.contracts:
                    if item.typeContract == 'CloseVotingContract' and contract.id == item.lectureContractId:
                        result = True
                        break
                if not result:
                    closeContract = CloseVotingContract(contract.id)
                    appendContract(closeContract)
                    self.contracts.append(closeContract)
        # sync publication
        self.add_publication()
        # sync publish
        for item in listIncoming:
            contract = self.get_lecture_contract(item.id)
            if contract is not None and item.list_id == trello.listPublishedId:
                result = False
                for item in self.contracts:
                    if item.typeContract == 'ClosingLectureContract' and contract.id == item.lectureContractId:
                        result = True
                        break
                if not result:
                    closeContract = ClosingLectureContract(contract.id)
                    appendContract(closeContract)
                    self.contracts.append(closeContract)





