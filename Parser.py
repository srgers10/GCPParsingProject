"""Google Cloud Platform Parser
This script will parse log data and normailze it
Data will be both CIM Compliant and available for the DataLake/BigQuery
Developers: Stephen Rogers, Patrick Kelly, Utsav Shrestha
"""
import re
import json
import sys
import getopt
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Dictionary for delimiter command
DELIMITER_DICT = {
    "<space>": " ",
    "<hyphen>": "-"
}

XML_EXPR_DICT = {
    "<text>": 1
}

class Parser:
    """Creates a parser object"""
    events = list()
    fields = dict()
    command_table = list()

    log_path = ""
    command_path = ""


    def __init__(self, log_path, command_path, event_splitter, parse_at_start = False):
        """Initializes a Parser Object"""

        self.log_path = log_path
        self.command_path = command_path

        self.open_command_table()
        self.event_splitter = event_splitter
        self.events = self.split_events(log_path, self.event_splitter)

        if parse_at_start:
            self.parse()

    def format_xml(self):
        """Formats XML currently does not return anything"""

        tree = ET.parse(self.log_path)
        root = tree.getroot()
        for child in root:
            print(ET.tostring(child, encoding='unicode'))

    def split_events(self, path, splitter):
        """Splits all events by a specified 'Splitter' """
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
        """Command table is the list of commands and field names needed to extract event's fields"""
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

    def try_parse_int(self, s, base=10, val=0):
        """Testing Integer Parsing"""
        try:
            return int(s, base)
        except ValueError:
            return val
    # Returns json with field and value pairs, based on the given log file and command table
    def parse(self, path = None, table= None):
        """Returns a JSON with field and value pairs based on given log file and command table"""
        if path is None:
            path = self.log_path
        if table is None:
            table = self.command_table

        field_dict = dict()
        parsed_events = []
        for event_index, event in enumerate(self.events):
            # temp_dict = regex_to_fields(line, table)
            if event is not None and event.strip() != "":
                temp_dict = self.parse_event(event, table, event_index)
                parsed_events.append(temp_dict)

        field_dict = {'events' : parsed_events}
        self.fields = field_dict
        return field_dict

    # Returns a dictionary of fields and values for the given event
    # key = field_name, value = field_value
    # table = [fields], [index: 0 = command, 1= group/split index, 2 = field_name, 3 = expression]
    def parse_event(self, event, table, event_index):
        """Returns a dict of fields and values for a given event
        key = field_name, value = field_value
        table = [fields], [index: 0=command, 1=group/split index, 2=field_name, 3=expression]"""
        to_return = dict()
        delimited_event_dict = dict()
        for field in table:
            key = field[2]
            val = ""
            if key is not None and key != "":
                if field[0] == "RegEx":
                    val = self.extract_regex_field(event, int(field[1]), field[3])
                elif field[0] == "Delimiter":
                    val, delimited_event_dict = self.extract_delim_field(event, self.try_parse_int(field[1]), field[3], delimited_event_dict)
                elif field[0] == "XML":
                    index = field[4] if len(field) >= 5 else 0
                    regex = field[5].strip() if len(field) >= 6 else ""
                    delimiter = field[6].strip() if len(field) >= 7 else ""
                    val = self.extract_xml_field(field[1], field[3], self.try_parse_int(index), regex, delimiter, event_index)
                to_return[key] = val

        return to_return

    def extract_regex_field(self, event, index, expression):
        """Extracts value based on given regular expression"""
        m = re.search(expression, event)
        if m:
            return m.group(0)
        return None

    # Extracts value based on the provided delimeter and index
    def extract_delim_field(self, event, index, delimiter, delimited_event_dict):
        """Extracts value based on the provided delimeter and index"""
        fields = list()
        if delimiter in delimited_event_dict:
            fields = delimited_event_dict[delimiter]
        else:
            try:
                fields = event.split(DELIMITER_DICT[delimiter.strip()])
                delimited_event_dict[delimiter] = fields
            except:
                print("Invalid Delimiter")
        if len(fields) > index:
            return fields[index], delimited_event_dict
        return None, delimited_event_dict

    def extract_xml_field(self, x_path, expression, index, regex, delimiter, event_index):
        """Extracts value based on XML as well as other options such as regex and delimeter"""
        tree = ET.parse(self.log_path)
        root = tree.getroot()
        xmlns = root[event_index].tag.split('}')[0]
        if xmlns != root:
            x_path = xmlns + "}" + str(x_path)

        expression = expression.strip()
        for child in root[event_index].iter(x_path):
            value = ""
            if expression in XML_EXPR_DICT:
                if XML_EXPR_DICT[expression] == 1:
                    value = child.text
            else:
                value = child.attrib[expression]

            if (regex is not None and regex != ""):
                return self.extract_regex_field(value, index, regex)
            elif (index is not None and delimiter is not None and index != "" and delimiter != ""):
                val, delimited_event_dict = self.extract_delim_field(value, index, delimiter, dict())
                return val
            else:
                return value



# Saves to json
def write_json(data, f_json):
    """Dumps JSON file using python dictionary"""
    json.dump(data, f_json)

def get_cmd_parameters(argv):
    """Allows for use on Command Line"""
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

    if len(sys.argv) == 1 : #Example data grabbed from http://www.almhuette-raith.at/apache-log/access.log
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
