#v0.0.1 for the Google Cloud Platform Parser. This script will parse log data and normailze it so that it will be both CIM Compliant and available to put into BigQuery
#Developers: Stephen Rogers, Patrick Kelly, Utsav Shrestha

import re

#Runs regex on the given event and returns a dictionary of fields and their values.
def regex_to_fields(event, reg_dict):
    to_return = {}
    for field in reg_dict:
        m = re.search(reg_dict[field], event)
        if(m):
            to_return[field] = m.group(0)

    return to_return


file_path = "example_log_data.log" #Change this to the appropriate log file. Example data grabbed from http://www.almhuette-raith.at/apache-log/access.log
delimiter = " " #splits the event by the given character.
event_index = 1

f = open(file_path, "r")
file_data = f.read()

events = file_data.splitlines()
example_event = events[event_index]

regex_dict = {
    "ip": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", 
    "timestamp": r"\[.*\]",
    "status-code": r"\"\s\d*"
}

field_dict = regex_to_fields(example_event, regex_dict)



print("\nEvent: " + events[event_index] + "\n")
print(field_dict)