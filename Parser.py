#v0.0.1 for the Google Cloud Platform Parser. This script will parse log data and normailze it so that it will be both CIM Compliant and available to put into BigQuery
#Developers: Stephen Rogers, Patrick Kelly, Utsav Shrestha

import re
import json

delimiter_dict = {
    "<space>": " "
}
#Runs regex on the given event and returns a dictionary of fields and their values.
def regex_to_fields(event, reg_dict):
    to_return = {}
    for field in reg_dict:
        m = re.search(reg_dict[field], event)
        if(m):
            to_return[field] = m.group(0)

    return to_return


def delimiter_to_fields(event, table, delimiter):
    to_return = {}
    fields = event.split(delimiter)
    for i in range(len(table)):
        k = list(table.keys())[i]
        v = fields[int(table[k])]
        to_return[k]=v
    return to_return



def parse_event(path, reg_dict, index, method, delimiter=" "):
    #Could we add a randomizer here to get a random event? Possibly multiple events? 
    event = get_event(path, index)
    field_dict = dict()
    if(method=="RegEx"):
        field_dict = regex_to_fields(event)
    elif(method=="Delimiter"):
        field_dict = delimiter_to_fields(event, reg_dict, delimiter)
    return field_dict

#Returns a dictionary of fields and values for the given event
def parse_event(event, table): #table is [fields], [index: 0 = command, 1= group/split index, 2 = field_name, 3 = expression] 
    to_return = dict() #key = field_name, value = field_value
    for field in table:
        key = field[2]
        val = ""
        if field[0] == "RegEx":
            val = extract_regex_field(event, int(field[1]), field[3])
        elif field[0] == "Delimiter":
            val = extract_delim_field(event, int(field[1]), field[3])

        to_return[key] = val
    return to_return


def extract_regex_field(event, index, expression):
    m = re.search(expression, event)
    if m:
        return m.group(0)
    return None


def extract_delim_field(event, index, delimiter):
    fields = event.split(delimiter_dict[delimiter.strip()])
    if len(fields) > index:
        return fields[index]



def parse(path, reg_dict):
    f = open(path, "r")
    field_dict = dict()
    events = []

    for line in f:
        temp_dict = regex_to_fields(line, reg_dict)
        events.append(temp_dict)

        #for k, v in temp_dict.items():
         #   if k in field_dict:
          #      field_dict[k].append(v)
           # else:
            #    temp = list()
             #   temp.append(v)
              #  field_dict[k] = temp
    field_dict = {'events' : events}
    return field_dict



def get_event(path, index):
    event_index = index
    f = open(path, "r")
    file_data = f.read()
    events = file_data.splitlines()
    return events[index]

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
    
