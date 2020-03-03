from Parser import parse, get_example
import tkinter as tk 
from tkinter.filedialog import askopenfilename

def choose_file():
    global file_path
    file_path = askopenfilename()
    example = get_example(file_path, 1)
    txt_example_event.insert(tk.INSERT, example)

def start_parse():
    regex_dict = {}
    for i in range(height): #Rows
        key = cell[i][0].get()
        value = cell[i][1].get()
        if(key != ""):
            regex_dict[key] = value

    fields = parse(file_path,regex_dict)

    grid_values = tk.LabelFrame(r, text="Field Values")
    grid_values.pack(fill="both", expand="yes")

    extracted_fields = ""
    for k, v in fields.items():
    	extracted_fields += "\n" + str(k) + ": " + str(v)

    w= tk.Label(grid_values, text=extracted_fields, justify="left", anchor="w")
    w.pack()

def add_row():
	global height
	
	new_cell = [tk.Entry(grid_reg_ex, text=""), tk.Entry(grid_reg_ex, text="")]
	cell.append(new_cell)
	cell[height][0].grid(row=height, column=0)
	cell[height][1].grid(row=height, column=1)
	height += 1

file_path = ""
r = tk.Tk() 
r.title('Log Data Parser') 

button = tk.Button(r, text='Choose Log File', width=25, command=choose_file) 
button.pack() 
frame_example = tk.LabelFrame(r, text="Example Event Log")
frame_example.pack(fill="both", expand="yes")

txt_example_event = tk.Text(frame_example)
txt_example_event.pack()

btn_add_regex_row = tk.Button(r, text="Add", command=add_row)
btn_add_regex_row.pack()

grid_reg_ex = tk.LabelFrame(r, text="Field Extractions")
grid_reg_ex.pack(fill="both", expand="yes")

cell = list()
height = 0
f = open("regex_cmds.txt", "r")
for line in f:
	k_v = line.split(":", 1)

	e1 = tk.Entry(grid_reg_ex)
	e2 = tk.Entry(grid_reg_ex)
	e1.insert(0, k_v[0].strip())
	e2.insert(0, k_v[1].strip())

	new_cell = [e1, e2]
	cell.append(new_cell)
	cell[height][0].grid(row=height, column=0)
	cell[height][1].grid(row=height, column=1)
	height += 1

btn_parse = tk.Button(r, text="Parse", command=start_parse)
btn_parse.pack()

r.mainloop() 