from Parser import Parser, get_event, write_json
import tkinter as tk 
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter import messagebox as mb
import json

class ParserGUI:
	def __init__(self):
		self.log_path = "Logs/example_log_data.log"
		self.command_path = "CommandTables/example_command_table.txt"
		self.parser = Parser(self.log_path, self.command_path, False)
		default_regex = open("CommandTables/example_command_table.txt")
		self.event_index = 1
		self.COMMANDS = [
		    "Delimiter",
		    "RegEx"
		]
		#list to store StringVar objects for OptionMenu Widget of tkinter
		self.selected_commands = []
		self.cell = list()
		self.height = 1
		self.r = tk.Tk() 
		self.r.title('Log Data Parser')

		self.frame_left = tk.Frame(self.r)
		self.frame_left.grid(column=0, sticky="ns")

		self.regex_grid = tk.LabelFrame(self.frame_left, text="Field Extractions")
		self.regex_grid.grid(row=0)

		
		self.set_table(default_regex)

		btn_add_regex_row = tk.Button(self.frame_left, text="Add Field", command=self.add_row)
		btn_add_regex_row.grid(row=1)

		frame_regex_buttons = tk.Frame(self.frame_left)
		frame_regex_buttons.grid(row=2, sticky="s")

		btn_load_regex = tk.Button(frame_regex_buttons, text="Load", command=self.open_table)
		btn_load_regex.pack(side=tk.LEFT)

		btn_save_regex = tk.Button(frame_regex_buttons, text="Save", command=self.save_table)
		btn_save_regex.pack(side=tk.LEFT)

		frame_right = tk.Frame(self.r)
		frame_right.grid(row=0, column=1)

		btn_open = tk.Button(frame_right, text='Open Log', command=self.open_log) 
		btn_open.grid(row=0, column=0, sticky="w") 

		btn_parse = tk.Button(frame_right, text="Parse", command=self.save_log)
		btn_parse.grid(row=0, column=1)

		frame_example = tk.LabelFrame(frame_right, text="Example Event Log")
		frame_example.grid(row=1, column=0)

		self.txt_example_event = tk.Label(frame_example, wraplength=500, justify=tk.LEFT)
		self.txt_example_event.grid(row=0)

		frame_example_buttons = tk.Frame(frame_example)
		frame_example_buttons.grid(row=1, sticky="w")

		btn_next_event = tk.Button(frame_example_buttons, text= "Prev Event", command=self.prev_event)
		btn_next_event.pack(side=tk.LEFT)
		btn_next_event = tk.Button(frame_example_buttons, text= "Next Event", command=self.next_event)
		btn_next_event.pack(side=tk.LEFT)

		frame_example_fields = tk.LabelFrame(frame_right, text="Field Values")
		frame_example_fields.grid(row=2, column=0, sticky="we")

		self.txt_example_fields = tk.Label(frame_example_fields, justify=tk.LEFT)
		self.txt_example_fields.grid(row=0, sticky="we")

		btn_parse = tk.Button(frame_example_fields, text="Update", command=self.parse_example)
		btn_parse.grid(row=1)
		self.main()

	#checks if any log file has been selected
	def check_file_path(self):
		if self.log_path is not None and self.log_path != "":
			return True
		else:
			mb.showerror("No log file", "Please select a log file to parse!")
			return False

	# Reads the log file and parse the first line
	def open_log(self):
	    self.log_path = askopenfilename()
	    if self.log_path == "":
	    	self.txt_example_event.config(text="")
	    	self.txt_example_fields.config(text="")
	    	return
	    self.parse_example()

	# Saves the extracted fields to json file
	def save_log(self):
		if self.check_file_path():
		    f = asksaveasfile(mode='w', defaultextension=".json")
		    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
		        return
		    fields = self.parser.parse(self.log_path, self.get_table())
		    write_json(fields, f)

	# Loads regex expressions and delimeters from a file
	def open_table(self):
	    regex_path = askopenfilename()
	    if regex_path == "":
	        return
	    with open(regex_path) as f:
	        self.set_table(f)
	
	# Saves the regex expressions and delimeters to a file     
	def save_table(self):
	    table = self.get_table()
	    
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

	# Returns a list of list of the regex expressions and delimeters to extract fields
	def get_table(self):
	    # table = [[0 for i in range(self.height-1)] for j in range(4)]
	    table = list()
	    # table_row = 0
	    for i in range(1, self.height): #Rows
	        command = self.selected_commands[i-1].get()
	        index = self.cell[i][1].get()
	        field_name = self.cell[i][2].get()
	        expression = self.cell[i][3].get()
	        if field_name is not None and expression is not None and (field_name != "" and field_name != 0) and (expression != "" and expression != 0):
		        row = [command, index, field_name, expression]
		        # table[table_row]= row
		        # table_row += 1
		        table.append(row)
	    return table

	# Sets the values for regex expressions and delimeters to extract fields
	def set_table(self, f):
	    entries = self.regex_grid.grid_slaves()
	    for l in entries:
	        l.destroy()

	    self.cell = list()

	    self.height = 1
	    new_row = [tk.Label(self.regex_grid, text="Command"), tk.Label(self.regex_grid, text="Index"), tk.Label(self.regex_grid, text="Field Name"),tk.Label(self.regex_grid, text="Expression")]
	    self.cell.append(new_row)
	    self.cell[0][0].grid(row=0, column=0)
	    self.cell[0][1].grid(row=0, column=1)
	    self.cell[0][2].grid(row=0, column=2)
	    self.cell[0][3].grid(row=0, column=3)
	    
	    i = 0
	    for line in f:
	        values = line.split(" ")
	        field = self.add_row()
	        self.selected_commands[i].set(values[0])
	        # deleting previous garbage values
	        field[1].delete(0, tk.END)
	        field[2].delete(0, tk.END)
	        field[3].delete(0, tk.END)

	        # inserting new values
	        field[1].insert(0, values[1])
	        field[2].insert(0, values[2])
	        field[3].insert(0, values[3])
	        i += 1

	# Callback action for "Next Event" button
	def next_event(self):
	    self.event_index +=1
	    self.parse_example()

	# Callback action for "Prev Event" button
	def prev_event(self):
	    if(self.event_index>1):
	        self.event_index -=1
	    self.parse_example()

	# Parse the specified event   
	def parse_example(self):
		if self.check_file_path():
		    event = get_event(self.log_path, self.event_index)
		    self.txt_example_event.config(text=event)

		    example_fields = str(self.parser.parse_event(event, self.get_table()))
		    example_fields = example_fields.replace("{","{\n\t")
		    example_fields = example_fields.replace(",",",\n\t")
		    example_fields = example_fields.replace("}","\n}")
		    self.txt_example_fields.config(text=example_fields)

	# Callback action for "Add Field" button to add new row for adding regex or delimeter for parsing
	def add_row(self):
	    new_command = tk.StringVar(self.r)
	    new_command.set(self.COMMANDS[0]) # default valueS
	    self.selected_commands.append(new_command)

	    new_row = [tk.OptionMenu(self.regex_grid, new_command, *self.COMMANDS), tk.Entry(self.regex_grid, text="", width="3"), tk.Entry(self.regex_grid, text=""),tk.Entry(self.regex_grid, text="")]
	    self.cell.append(new_row)
	    self.cell[self.height][0].grid(row=self.height, column=0)
	    self.cell[self.height][1].grid(row=self.height, column=1)
	    new_row[1].insert(0, "0")
	    self.cell[self.height][2].grid(row=self.height, column=2)
	    self.cell[self.height][3].grid(row=self.height, column=3)
	    self.height += 1
	    return new_row

	# The main function
	def main(self):
		self.parse_example()
		self.r.mainloop() 

ParserGUI()
