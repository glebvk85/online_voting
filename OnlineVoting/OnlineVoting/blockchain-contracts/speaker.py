name_contract = 'speaker'
version_contract = 1

speakers = get_value(variables, 'speakers', [])
for item in parameters:
    speakers.append(item)