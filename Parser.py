#v0.0.1 for the Google Cloud Platform Parser. This script will parse log data and normailze it so that it will be both CIM Compliant and available to put into BigQuery
#Developers: Stephen Rogers, Patrick Kelly, Utsav Shrestha

import re
import json

#Runs regex on the given event and returns a dictionary of fields and their values.
def regex_to_fields(event, reg_dict):
    to_return = {}
    for field in reg_dict:
        m = re.search(reg_dict[field], event)
        if(m):
            to_return[field] = m.group(0)

    return to_return


def parse(path, reg_dict, index=1):
    example_event = get_example(path, index)

def parse(path, reg_dict):
    #Could we add a randomizer here to get a random event? Possibly multiple events? 
    example_event = get_example(path, 1)
    field_dict = regex_to_fields(example_event, reg_dict)
    return field_dict
 
def parse(path, reg_dict):
    f = open(path, "r")
    field_dict = dict()
    for line in f:
        temp_dict = regex_to_fields(line, reg_dict)
        for k, v in temp_dict.items():
            if k in field_dict:
                field_dict[k].append(v)
            else:
                temp = list()
                temp.append(v)
                field_dict[k] = temp
    return field_dict

def get_example(path, index):
    event_index = index
    f = open(path, "r")
    file_data = f.read()
    events = file_data.splitlines()
    return events[index]

def write_json(data, filename='fields.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f)

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
    
