name_contract = 'vote'
version_contract = 1

investors = get_value(variables, 'investors', [])
votes = get_value(variables, 'votes', [])
votes.append(parameters[0])
investors.append(owner_address)