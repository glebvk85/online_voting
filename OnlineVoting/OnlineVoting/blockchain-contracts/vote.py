name_contract = 'vote'
version_contract = 1

try:
    investors
except NameError: investors = []
try:
    sum_of_votes
except NameError: sum_of_votes = 0

sum_of_votes += parameters[1]
investors.append(owner_address)