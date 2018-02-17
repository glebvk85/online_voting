name_contract = 'theme'
version_contract = 1

need_close = True
theme_is_finished = get_value(variables, 'theme_is_finished', None)
complete = theme_is_finished is not None and theme_is_finished(parameters[0])

if complete:
    investors = get_value(variables, 'investors', [])
    speakers = get_value(variables, 'speakers', [])
    votes = get_value(variables, 'votes', [])
    feedbacks = get_value(variables, 'feedbacks', [])

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
    if len(columns) != 0:
        sum_of_feedbacks = sum_of_feedbacks / (len(columns) * 10)
    sum_of_votes = sum(votes)
    count_of_speakers = len(speakers)
    count_of_investors = len(investors)
    total_bonus = sum_of_votes + sum_of_feedbacks
    if count_of_speakers + count_of_investors != 0:
        if count_of_speakers <= count_of_investors:
            bonus_speaker = total_bonus / (count_of_speakers + count_of_investors)
            bonus_investor = bonus_speaker
        else:
            bonus_speaker = 0 if count_of_speakers == 0 else (total_bonus / 2) / count_of_speakers
            bonus_investor = 0 if count_of_investors == 0 else (total_bonus / 2) / count_of_investors
        for item in investors:
            variables['pays'].append(pay(None, item, bonus_investor))
        for item in speakers:
            variables['pays'].append(pay(None, item, bonus_speaker))