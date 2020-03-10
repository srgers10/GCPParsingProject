from Parser import parse, parse_event, get_event, write_json
import tkinter as tk 
from tkinter.filedialog import askopenfilename, asksaveasfile
import json

file_path = "example_log_data.log"
event_index = 1
COMMANDS = [
    "Delimiter",
    "RegEx"
]
selected_commands = []

def open_log():
    global file_path
    file_path = askopenfilename()
    if file_path == "":
        return
    parse_example()

def save_log():
    f = asksaveasfile(mode='w', defaultextension=".json")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    fields = parse(file_path, get_table())
    write_json(fields, f)

def open_table():
    regex_path = askopenfilename()
    if regex_path == "":
        return
    with open(regex_path) as f:
        set_table(f)
        

def save_table():
    table = get_table()
    
    content = ""
    for field in table:
        for val in field:
            content+= str(val)+ " " 
        content+="\n"

    f = asksaveasfile(mode='w', defaultextension=".txt")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    f.write(content)
    f.close()

def get_table():
    # table = [[0 for i in range(height-1)] for j in range(4)]
    table = list()
    table_row = 0
    for i in range(1, height): #Rows
        command = selected_commands[i-1].get()
        index = cell[i][1].get()
        field_name = cell[i][2].get()
        expression = cell[i][3].get()
        if field_name is not None and expression is not None and (field_name != "" and field_name != 0) and (expression != "" and expression != 0):
	        row = [command, index, field_name, expression]
	        # table[table_row]= row
	        # table_row += 1
	        table.append(row)
    return table

def set_table(f):
    global cell
    global height

    entries = regex_grid.grid_slaves()
    for l in entries:
        l.destroy()

    cell = list()
    
    new_row = [tk.Label(regex_grid, text="Command"), tk.Label(regex_grid, text="Index"), tk.Label(regex_grid, text="Field Name"),tk.Label(regex_grid, text="Expression")]
    cell.append(new_row)
    cell[0][0].grid(row=0, column=0)
    cell[0][1].grid(row=0, column=1)
    cell[0][2].grid(row=0, column=2)
    cell[0][3].grid(row=0, column=3)
    height = 1

    i = 0
    for line in f:
        values = line.split(" ")
        field = add_row()
        selected_commands[i].set(values[0])
        # deleting previous garbage values
        field[1].delete(0, tk.END)
        field[2].delete(0, tk.END)
        field[3].delete(0, tk.END)

        # inserting new values
        field[1].insert(0, values[1])
        field[2].insert(0, values[2])
        field[3].insert(0, values[3])
        i += 1

def next_event():
    global event_index
    event_index +=1
    parse_example()

def prev_event():
    global event_index
    if(event_index>1):
        event_index -=1
    parse_example()
    
def parse_example():
    event = get_event(file_path, event_index)
    txt_example_event.config(text=event)

    example_fields = str(parse_event(event, get_table()))
    example_fields = example_fields.replace("{","{\n\t")
    example_fields = example_fields.replace(",",",\n\t")
    example_fields = example_fields.replace("}","\n}")
    txt_example_fields.config(text=example_fields)


def add_row():
    global height
    new_command = tk.StringVar(r)
    new_command.set(COMMANDS[0]) # default value
    selected_commands.append(new_command)

    new_row = [tk.OptionMenu(regex_grid, new_command, *COMMANDS), tk.Entry(regex_grid, text="", width="3"), tk.Entry(regex_grid, text=""),tk.Entry(regex_grid, text="")]
    cell.append(new_row)
    cell[height][0].grid(row=height, column=0)
    cell[height][1].grid(row=height, column=1)
    new_row[1].insert(0, "0")
    cell[height][2].grid(row=height, column=2)
    cell[height][3].grid(row=height, column=3)
    height += 1
    return new_row


r = tk.Tk() 
r.title('Log Data Parser') 

frame_left = tk.Frame(r)
frame_left.grid(column=0, sticky="ns")

regex_grid = tk.LabelFrame(frame_left, text="Field Extractions")
regex_grid.grid(row=0)

default_regex =  open("delim_cmds.txt")
set_table(default_regex)

btn_add_regex_row = tk.Button(frame_left, text="Add Field", command=add_row)
btn_add_regex_row.grid(row=1)


frame_regex_buttons = tk.Frame(frame_left)
frame_regex_buttons.grid(row=2, sticky="s")

btn_load_regex = tk.Button(frame_regex_buttons, text="Load RegEx", command=open_table)
btn_load_regex.pack(side=tk.LEFT)

btn_load_regex = tk.Button(frame_regex_buttons, text="Save", command=save_table)
btn_load_regex.pack(side=tk.LEFT)

frame_right = tk.Frame(r)
frame_right.grid(row=0, column=1)

btn_open = tk.Button(frame_right, text='Open Log', command=open_log) 
btn_open.grid(row=0, column=0, sticky="w") 

btn_parse = tk.Button(frame_right, text="Parse", command=save_log)
btn_parse.grid(row=0, column=1)

frame_example = tk.LabelFrame(frame_right, text="Example Event Log")
frame_example.grid(row=1, column=0)

txt_example_event = tk.Label(frame_example, wraplength=500, justify=tk.LEFT)
txt_example_event.grid(row=0)


frame_example_buttons = tk.Frame(frame_example)
frame_example_buttons.grid(row=1, sticky="w")

btn_next_event = tk.Button(frame_example_buttons, text= "Prev Event", command=prev_event)
btn_next_event.pack(side=tk.LEFT)
btn_next_event = tk.Button(frame_example_buttons, text= "Next Event", command=next_event)
btn_next_event.pack(side=tk.LEFT)



frame_example_fields = tk.LabelFrame(frame_right, text="Field Values")
frame_example_fields.grid(row=2, column=0, sticky="we")

txt_example_fields = tk.Label(frame_example_fields, justify=tk.LEFT)
txt_example_fields.grid(row=0, sticky="we")

btn_parse = tk.Button(frame_example_fields, text="Update", command=parse_example)
btn_parse.grid(row=1)

parse_example()
r.mainloop() 
