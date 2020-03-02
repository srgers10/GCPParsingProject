#v0.0.1 for the Google Cloud Platform Parser. This script will parse log data and normailze it so that it will be both CIM Compliant and available to put into BigQuery
#Developers: Stephen Rogers, Patrick Kelly, Utsav Shrestha

import re

file_path = "example_log_data.log" #Change this to the appropriate log file. Example data grabbed from http://www.almhuette-raith.at/apache-log/access.log
f = open(file_path, "r")
file_data = f.read()
print(file_data)

#Seperates the events by line breaks. \r is carriage return. \n is new line
def seperate_lines(data):
    lines = re.findall("[\r\n]+)", data)
    return lines

#Splits events by white space and any major delimiter. Major Delimiters:   space, newline, tab, [], (), {}, !, ;, ,, "", 
def segment_event(event):
    segments = re.findall(r"[\w`]+", event) #fields seperated by white space





