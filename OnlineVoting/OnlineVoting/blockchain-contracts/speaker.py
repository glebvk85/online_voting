name_contract = 'speaker'
version_contract = 1

try:
    speakers
except NameError: speakers = []

for item in parameters:
    speakers.append(item)