name_contract = 'publication'
version_contract = 1

feedbacks = get_value(variables, 'feedbacks', [])
publication_points = get_value(variables, 'publication_points', [])

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
publication_points.append(sum_of_feedbacks)
set_value(variables, 'feedbacks', [])