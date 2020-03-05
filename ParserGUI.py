from Parser import parse, parse_event, get_example, write_json
import tkinter as tk 
from tkinter.filedialog import askopenfilename, asksaveasfile
import json

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
    fields = parse(file_path, get_regex())
    write_json(fields, f)

def open_regex():
    global file_path
    file_path = askopenfilename()
    if file_path == "":
        return
    with open(file_path) as f:
        set_regex(f)
        

def save_regex():
    regex= get_regex()
    
    content = ""
    for k, v in regex.items():
        content+= k+": "+v + "\n"
    f = asksaveasfile(mode='w', defaultextension=".txt")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    f.write(content)
    f.close()

def get_regex():
    regex_dict = dict()
    for i in range(height): #Rows
        key = cell[i][0].get()
        value = cell[i][1].get()
        if(key != ""):
            regex_dict[key] = value
    return regex_dict

def set_regex(f):
    global cell
    global height

    entries = regex_grid.grid_slaves()
    for l in entries:
        l.destroy()

    cell = list()
    height = 0
    for line in f:
        k_v = line.split(":", 1)

        e1 = tk.Entry(regex_grid)
        e2 = tk.Entry(regex_grid)
        e1.insert(0, k_v[0].strip())
        e2.insert(0, k_v[1].strip())

        new_cell = [e1, e2]
        cell.append(new_cell)
        cell[height][0].grid(row=height, column=0)
        cell[height][1].grid(row=height, column=1)
        height += 1



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
    example = get_example(file_path, event_index)
    txt_example_event.config(text=example)

    example_fields = str(parse_event(file_path, get_regex(), event_index))
    example_fields = example_fields.replace("{","{\n\t")
    example_fields = example_fields.replace(",",",\n\t")
    example_fields = example_fields.replace("}","\n}")
    txt_example_fields.config(text=example_fields)


def add_row():
	global height
	
	new_cell = [tk.Entry(regex_grid, text=""), tk.Entry(regex_grid, text="")]
	cell.append(new_cell)
	cell[height][0].grid(row=height, column=0)
	cell[height][1].grid(row=height, column=1)
	height += 1


file_path = "example_log_data.log"
event_index = 1

r = tk.Tk() 
r.title('Log Data Parser') 

frame_left = tk.Frame(r)
frame_left.grid(column=0, sticky="ns")

regex_grid = tk.LabelFrame(frame_left, text="Field Extractions")
regex_grid.grid(row=0 , columnspan=3 )

default_regex =  open("regex_cmds.txt")
set_regex(default_regex)

btn_add_regex_row = tk.Button(frame_left, text="Add Field", command=add_row)
btn_add_regex_row.grid(row=1, column=2)


frame_regex_buttons = tk.Frame(frame_left)
frame_regex_buttons.grid(row=2, sticky="s")

btn_load_regex = tk.Button(frame_regex_buttons, text="Load RegEx", command=open_regex)
btn_load_regex.pack(side=tk.LEFT)

btn_load_regex = tk.Button(frame_regex_buttons, text="Save", command=save_regex)
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
