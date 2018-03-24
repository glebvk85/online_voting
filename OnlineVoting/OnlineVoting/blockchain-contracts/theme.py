name_contract = 'theme'
version_contract = 1

need_close = True
theme_is_finished = get_value(variables, 'theme_is_finished', None)
complete = theme_is_finished is not None and theme_is_finished(parameters[0])

if complete:
    investors = get_value(variables, 'investors', [])
    speakers = get_value(variables, 'speakers', [])
    votes = get_value(variables, 'votes', [])
    publication_points = get_value(variables, 'publication_points', [])

    sum_of_votes = sum(votes)
    count_of_speakers = len(speakers)
    count_of_investors = len(investors)
    sum_publication_points = sum(publication_points)
    if sum_publication_points == 0:
        sum_publication_points = 10
    total_bonus = (1 + 0.5 * sum_of_votes) * sum_publication_points
    if count_of_speakers + count_of_investors != 0:
        if count_of_investors <= count_of_speakers:
            bonus_speaker = total_bonus / (count_of_speakers + count_of_investors)
            bonus_investor = bonus_speaker
        else:
            bonus_speaker = 0 if count_of_speakers == 0 else (total_bonus / 2) / count_of_speakers
            bonus_investor = 0 if count_of_investors == 0 else (total_bonus / 2) / count_of_investors
        for item in investors:
            variables['pays'].append(pay(None, item, bonus_investor))
        for item in speakers:
            variables['pays'].append(pay(None, item, bonus_speaker))