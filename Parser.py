#iss3 for the Google Cloud Platform Parser. This script will parse log data and normailze it so that it will be both CIM Compliant and available to put into BigQuery
#Developers: Stephen Rogers, Patrick Kelly, Utsav Shrestha

import re
import json
import sys, getopt
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Dictionary for delimiter command
delimiter_dict = {
    "<space>": " "
}

xml_expr_dict = {
    "<text>": 1
}

class Parser:
    events = list()
    fields = dict()
    command_table = list()

    log_path = ""
    command_path = ""
    

    def __init__(self, log_path, command_path, event_splitter, parse_at_start = False):
        
        self.log_path = log_path
        self.command_path = command_path
        
        self.open_command_table()
        self.event_splitter = event_splitter
        self.events = self.split_events(log_path, self.event_splitter)
        
        if parse_at_start:
            self.parse()

    def format_xml(self):
        tree = ET.parse(self.log_path)
        root = tree.getroot()
        for child in root:
            print(ET.tostring(child, encoding='unicode'))

    def split_events(self, path, splitter):
        f = open(path, "r")
        file_data = f.read()
        to_return = list()
        if splitter == "XML":
            tree = minidom.parse(self.log_path)
            itemgroup = tree.getElementsByTagName('Event')
            to_return = [x.toxml() for x in itemgroup]
        else:
            to_return = re.split(splitter, file_data)
        return to_return

    # Command table is the list of commands and field names needed to extract the event's fields.
    def open_command_table(self, command_path = None):
        to_return = list()

        if command_path is None:
            command_path = self.command_path

        f = open(command_path, "r")

        temp = True
        for line in f:
            field = line.split()
            if temp:
                self.event_splitter = field[1]
                temp = False
            else:
                to_return.append(field)

        self.command_table = to_return
        
        return to_return

    # Returns json with field and value pairs, based on the given log file and command table
    def parse(self, path = None, table= None):
        if path is None:
            path = self.log_path
        if table is None:
            table = self.command_table

        field_dict = dict()
        parsed_events = []
        for event in self.events:
            # temp_dict = regex_to_fields(line, table)
            if event is not None and event.strip() != "":
                temp_dict = self.parse_event(event, table, None)
                parsed_events.append(temp_dict)

        field_dict = {'events' : parsed_events}
        self.fields = field_dict
        return field_dict

    # Returns a dictionary of fields and values for the given event
    # key = field_name, value = field_value
    # table = [fields], [index: 0 = command, 1= group/split index, 2 = field_name, 3 = expression]
    def parse_event(self, event, table, event_index):
        to_return = dict()
        delimited_event_dict = dict()
        for field in table:
            key = field[2]
            val = ""
            if key is not None and key != "":
                if field[0] == "RegEx":
                    val = self.extract_regex_field(event, int(field[1]), field[3])
                elif field[0] == "Delimiter":
                    val, delimited_event_dict = self.extract_delim_field(event, int(field[1]), field[3], delimited_event_dict)
                elif field[0] == "XML":
                    val = self.extract_xml_field(field[1], field[3], event_index)
                to_return[key] = val

        return to_return

    # Extracts value based on the given regex expression
    def extract_regex_field(self, event, index, expression):
        m = re.search(expression, event)
        if m:
            return m.group(0)
        return None

    # Extracts value based on the provided delimeter and index
    def extract_delim_field(self, event, index, delimiter, delimited_event_dict):
        fields = list()
        if delimiter in delimited_event_dict:
            fields = delimited_event_dict[delimiter]
        else:
            try:
                fields = event.split(delimiter_dict[delimiter.strip()])
                delimited_event_dict[delimiter] = fields
            except:
                print("Invalid Delimiter")
        if len(fields) > index:
            return fields[index], delimited_event_dict
        return None, delimited_event_dict
    
    def extract_xml_field(self, x_path, expression, event_index):
        tree = ET.parse(self.log_path)
        root = tree.getroot()
        xmlns = root[event_index].tag.split('}')[0]
        if xmlns != root:
            x_path = xmlns + "}" + str(x_path)

        expression = expression.strip()
        for child in root[event_index].iter(x_path):
            if expression in xml_expr_dict:
                if xml_expr_dict[expression] == 1:
                    return child.text
            return child.attrib[expression]

        # fields = root.findall(x_path)
        # for child in root:
        #     print(child.tag, child.attrib)
        # if len(fields) > index:
        #     return fields[index]
        # else:
        #     print(x_path + " is not in event" + str(root))
        #     return None
    

# Saves to json
def write_json(data, f_json):
    json.dump(data, f_json)

def get_cmd_parameters(argv):
    log_path = ""
    command_path = ""
    output_path = ""
    try:
        opts, args = getopt.getopt(argv,"hl:c:o:",["lfile=","cfile=","ofile="])
    except getopt.GetoptError:
        print("Parser.py -l <log_file> -c <command_table_file> -o <output_file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Parser.py -l <log_file> -c <command_table_file> -o <output_file>")
            sys.exit()
        elif opt in ("-l", "--lfile"):
            log_path = arg
        elif opt in ("-c", "--cfile"):
            command_path = arg
        elif opt in ("-o", "--ofile"):
            output_path = arg

    return log_path, command_path, output_path

# arg1 = path of the log file
# arg2 = path of the command table file
# arg3 = output path (JSON format)
if __name__ == "__main__":

    if len(sys.argv) == 1 : # default: Example data grabbed from http://www.almhuette-raith.at/apache-log/access.log
        log_path = "Logs/example_log_data.log"
        command_path = "CommandTables/example_command_table_v2.cmdt"
        output_path = "JSON/example_output.json"
    else:
        log_path, command_path, output_path = get_cmd_parameters(sys.argv[1:])
        # log_path = sys.argv[1]
        # command_path = sys.argv[2]
        # output_path = sys.argv[3]

    parser = Parser(log_path, command_path, True)

    with open(output_path, 'w') as f:
        json.dump(parser.fields, f)

    """
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
    """
