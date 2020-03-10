import pandas as pd
from collections import defaultdict
import openpyxl
#-----------------------------------------------------------------------------------------
# Initialization of the Column
#-----------------------------------------------------------------------------------------
data_file = "McAfee_Raw_Events.txt"

data_file_delim = ', '
column_names = set()

with open(data_file, 'r') as temp_f:
    lines = temp_f.readlines()

    for l in lines:
        temp = l.split(data_file_delim)
        for item in temp:
            temp_split = item.split("=")
            if len(temp_split) >= 2:
                column_names.add(temp_split[0])

temp_f.close()
column_names = list(column_names)
#-----------------------------------------------------------------------------------------
print(column_names)
events = defaultdict(list)

with open(data_file, 'r') as temp_f:
    lines = temp_f.readlines()

    for l in lines:
        temp = l.split(data_file_delim)
        for item in temp:
            temp_split = item.split("=")
            if len(temp_split) >= 2:
                if temp_split[0] in column_names:
                    events[temp_split[0]].append(temp_split[1])
                else:
                    events[temp_split[0]].append("")

print(events)
df = pd.DataFrame.from_dict(events, orient='index')
df = df.transpose()
df.to_excel("McAfeeTestNew.xlsx", index=False)
