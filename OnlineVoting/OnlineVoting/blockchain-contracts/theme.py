name_contract = 'theme'
version_contract = 1

need_close = True
complete = theme_finished

if complete:
    try:
        investors
    except NameError: investors = []
    try:
        speakers
    except NameError: speakers = []
    try:
        votes
    except NameError: votes = []
    try:
        feedbacks
    except NameError:
        feedbacks = []

    columns = []
    for item in feedbacks:
        if len(columns) == 0:
            for i in range(len(item)):
                columns.append([])
        for i in range(len(item)):
            columns[i].append(item[i])
    sum_of_feedbacks = 0
    for item in columns:
        sum_of_feedbacks += median(item)
    sum_of_votes = sum(votes)
    count_of_speakers = len(speakers)
    count_of_investors = len(investors)
    total_bonus = sum_of_votes + sum_of_feedbacks
    if count_of_speakers <= count_of_investors:
        bonus_speaker = total_bonus / (count_of_speakers + count_of_investors)
        bonus_investor = bonus_speaker
    else:
        bonus_speaker = (total_bonus / 2) / count_of_speakers
        bonus_investor = (total_bonus / 2) / count_of_investors
    for item in investors:
        pay(pays, None, item, bonus_investor)
    for item in speakers:
        pay(pays, None, item, bonus_speaker)