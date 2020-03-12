#v0.0.1 for the Google Cloud Platform Parser. This script will parse log data and normailze it so that it will be both CIM Compliant and available to put into BigQuery
#Developers: Stephen Rogers, Patrick Kelly, Utsav Shrestha

import re
import json

# Dictionary for delimiter command
delimiter_dict = {
    "<space>": " "
}

## These commented functions are never used. May be it can be deleted
# Runs regex on the given event and returns a dictionary of fields and their values.
# def regex_to_fields(event, reg_dict):
#     to_return = {}
#     for field in reg_dict:
#         m = re.search(reg_dict[field], event)
#         if(m):
#             to_return[field] = m.group(0)

#     return to_return

# # Splits event based on the given delimiter and returns a dictionary of fields and their values.
# def delimiter_to_fields(event, table, delimiter):
#     to_return = {}
#     fields = event.split(delimiter)
#     for i in range(len(table)):
#         k = list(table.keys())[i]
#         v = fields[int(table[k])]
#         to_return[k]=v
#     return to_return

# Returns a dictionary of fields and values for the event selected based on index
# def parse_event(path, reg_dict, index, method, delimiter=" "):
#     #Could we add a randomizer here to get a random event? Possibly multiple events? 
#     event = get_event(path, index)
#     field_dict = dict()
#     if(method=="RegEx"):
#         field_dict = regex_to_fields(event)
#     elif(method=="Delimiter"):
#         field_dict = delimiter_to_fields(event, reg_dict, delimiter)
#     return field_dict

# Extracts value based on the given regex expression
def extract_regex_field(event, index, expression):
    m = re.search(expression, event)
    if m:
        return m.group(0)
    return None

# Extracts value based on the provided delimeter and index
def extract_delim_field(event, index, delimiter):
    fields = event.split(delimiter_dict[delimiter.strip()])
    if len(fields) > index:
        return fields[index]

# Returns a dictionary of fields and values for the given event
def parse_event(event, table): #table is [fields], [index: 0 = command, 1= group/split index, 2 = field_name, 3 = expression] 
    to_return = dict() #key = field_name, value = field_value
    for field in table:
        key = field[2]
        val = ""
        if key is not None and key != "":
            if field[0] == "RegEx":
                val = extract_regex_field(event, int(field[1]), field[3])
            elif field[0] == "Delimiter":
                val = extract_delim_field(event, int(field[1]), field[3])
            to_return[key] = val

    return to_return

# Returns a dictionary with parent key as "events" and value as a list of dictionaries of fields and values for all the events in the given file
def parse(path, table):
    f = open(path, "r")
    field_dict = dict()
    events = []

    for event in f:
        # temp_dict = regex_to_fields(line, table)
        if event is not None and event.strip() != "":
            temp_dict = parse_event(event, table)
            events.append(temp_dict)

    field_dict = {'events' : events}
    return field_dict

# Returns particular event from the log file based on index
def get_event(path, index):
    event_index = index
    f = open(path, "r")
    file_data = f.read()
    events = file_data.splitlines()
    return events[index]

# Saves to json
def write_json(data, f_json): 
    json.dump(data, f_json)

if __name__ == "__main__": 
    file_path = "example_log_data.log" #Change this to the appropriate log file. Example data grabbed from http://www.almhuette-raith.at/apache-log/access.log
    regex_dict = {
        "ip": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", 
        "timestamp": r"\[.*\]",
        "status-code": r"(?<=\"\s)(\d*)"
    }

    fields = parse(file_path, regex_dict)
    print(fields)

    # Creates a json with the dictionary "fields" and saves it as a json. Can be retrieved later using:
    # with open('fields.json', 'r') as f:
    #   fields = json.load(f)
    with open('fields.json', 'w') as f:
        json.dump(fields, f)
    
