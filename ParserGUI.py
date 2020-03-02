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
    print(fields)

    grid_values = tk.LabelFrame(r, text="Field Values")
    grid_values.pack(fill="both", expand="yes")

    values = [[tk.Entry(grid_reg_ex, text="") for i in range(width)] for j in range(height)]
    for i in range(height): #Rows
        for j in range(width): #Columns 
            values[i][j].grid(row=i, column=j)


file_path = ""
r = tk.Tk() 
r.title('Log Data Parser') 

button = tk.Button(r, text='Choose Log File', width=25, command=choose_file) 
button.pack() 
frame_example = tk.LabelFrame(r, text="Example Event Log")
frame_example.pack(fill="both", expand="yes")

txt_example_event = tk.Text(frame_example)
txt_example_event.pack()

grid_reg_ex = tk.LabelFrame(r, text="Field Extractions")
grid_reg_ex.pack(fill="both", expand="yes")

height = 5
width = 2
cell = [[tk.Entry(grid_reg_ex, text="") for i in range(width)] for j in range(height)]
for i in range(height): #Rows
    for j in range(width): #Columns 
        cell[i][j].grid(row=i, column=j)

btn_parse = tk.Button(r, text="Parse", command=start_parse)
btn_parse.pack()

r.mainloop() 