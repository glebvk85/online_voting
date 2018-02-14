name_contract = 'vote'
version_contract = 1

try:
    investors
except NameError: investors = []
try:
    votes
except NameError: votes = []

votes.append(parameters[0])
investors.append(owner_address)