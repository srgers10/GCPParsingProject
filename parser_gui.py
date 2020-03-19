import json
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter import messagebox as mb
from parser import Parser, write_json


class ParserGUI:
    def __init__(self):
        self.xml = False
        self.log_path = "Logs/example_log_data.log"
        self.command_path = "CommandTables/example_command_table.txt"
        default_regex = open("CommandTables/example_command_table.txt")
        self.event_index = 1
        self.COMMANDS = [
            "Delimiter",
            "RegEx",
            "XML",
            "JSON"
        ]
        self.COMMANDS_XML = [
            "Delimiter",
            "RegEx"
        ]
        #list to store StringVar objects for OptionMenu Widget of tkinter
        self.selected_commands = []
        self.cell = list()
        self.button_idx = [None]
        self.height = 1
        self.root = tk.Tk()
        self.root.title('Log Data Parser')

        # Creates a "frame" for the left side of the GUI
        self.frame_left = tk.Frame(self.root)
        self.frame_left.grid(column=0, sticky="ns")

        # Splits the Frame in two rows
        frame_splitter = tk.Frame(self.frame_left)
        frame_splitter.grid(row=0)

        # Splits up labels on the Frame
        lbl_splitter = tk.Label(frame_splitter, text='Event Splitter')
        lbl_splitter.grid(row=1, column=0, sticky="w")

        self.ent_splitter = tk.Entry(frame_splitter, text='Event Splitter')
        self.ent_splitter.grid(row=1, column=1, sticky="w")

        event_splitter = "[\\r\\n]+"
        self.ent_splitter.insert(0, event_splitter)

        self.extraction_grid = tk.LabelFrame(self.frame_left, text="Field Extractions")
        self.extraction_grid.grid(row=1)


        self.set_table(default_regex)

        btn_add_extraction_row = tk.Button(self.frame_left, text="Add Field", command=self.add_row)
        btn_add_extraction_row.grid(row=2)

        frame_extraction_buttons = tk.Frame(self.frame_left)
        frame_extraction_buttons.grid(row=3, sticky="s")

        btn_load_extraction = tk.Button(frame_extraction_buttons, text="Load", command=self.open_table)
        btn_load_extraction.pack(side=tk.LEFT)

        btn_save_extraction = tk.Button(frame_extraction_buttons, text="Save", command=self.save_table)
        btn_save_extraction.pack(side=tk.LEFT)

        # Frame for the "right" side of the GUI
        frame_right = tk.Frame(self.root)
        frame_right.grid(row=0, column=1)

        frame_event_buttons = tk.Frame(frame_right)
        frame_event_buttons.grid(row=0, sticky="we")

        btn_open = tk.Button(frame_event_buttons, text='Open Log', command=self.open_log)
        btn_open.grid(row=0, column=0, sticky="w")

        btn_parse = tk.Button(frame_event_buttons, text="Parse", command=self.save_log)
        btn_parse.grid(row=0, column=3, sticky="e")

        frame_example = tk.LabelFrame(frame_right, text="Example Event Log")
        frame_example.grid(row=1, column=0)

        self.txt_example_event = tk.Label(frame_example, wraplength=500, justify=tk.LEFT)
        self.txt_example_event.grid(row=0)

        frame_example_buttons = tk.Frame(frame_example)
        frame_example_buttons.grid(row=1, sticky="w")

        btn_prev_event = tk.Button(frame_example_buttons, text= "Prev Event", command=self.prev_event)
        btn_prev_event.pack(side=tk.LEFT)
        btn_next_event = tk.Button(frame_example_buttons, text= "Next Event", command=self.next_event)
        btn_next_event.pack(side=tk.LEFT)

        frame_example_fields = tk.LabelFrame(frame_right, text="Field Values")
        frame_example_fields.grid(row=2, column=0, sticky="we")

        self.txt_example_fields = tk.Label(frame_example_fields,  wraplength=500, justify=tk.LEFT)
        self.txt_example_fields.grid(row=0, sticky="we")

        btn_parse = tk.Button(frame_example_fields, text="Update", command=self.parse_example)
        btn_parse.grid(row=1)

        self.parser = Parser(self.log_path, self.command_path, event_splitter, False)
        self.main()

    def check_file_path(self):
        """Checks if a log file exists to parse"""
        if self.log_path is not None and self.log_path != "":
            return True
        else:
            mb.showerror("No log file", "Please select a log file to parse!")
            return False

    def open_log(self):
        """Reads the log file and parses the first line"""
        self.ent_splitter.config(state=tk.NORMAL)
        self.ent_splitter.delete(0, tk.END)
        self.log_path = askopenfilename()
        self.xml = False
        self.event_index = 1
        if self.log_path is None or self.log_path.strip() == "":
            self.txt_example_event.config(text="")
            self.txt_example_fields.config(text="")
            return
        elif self.log_path.split('.')[-1].lower() == "xml":
            self.ent_splitter.insert(0, "XML")
            self.ent_splitter.config(state=tk.DISABLED)
            self.xml = True
            self.set_grids_tables()
            self.add_row()
        else:
            self.ent_splitter.insert(0, "[\\r\\n]+")

        event_splitter = self.ent_splitter.get()
        self.parser = Parser(self.log_path, self.command_path, event_splitter, False)
        self.parse_example()

    def save_log(self):
        """Saves the extracted fields to JSON"""
        if self.check_file_path():
            f = asksaveasfile(mode='w', defaultextension=".json")
            if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
                return
            fields = self.parser.parse(self.log_path, self.get_table())
            write_json(fields, f)

    def open_table(self):
        """Loads regular expressions and delimeters from a file"""
        regex_path = askopenfilename()
        if regex_path == "":
            return
        with open(regex_path) as f:
            self.set_table(f)

    def save_table(self):
        """Saves regular expressions and delimeters to a file"""
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

    def get_table(self):
        """Returns a list of lists of the Regex and Delimeters to extract the fields"""
        table = list()
        for i in range(1, self.height): #Rows
            command = self.selected_commands[i-1].get()
            index = self.cell[i][1].get()
            field_name = self.cell[i][2].get()
            expression = self.cell[i][3].get()
            if self.xml:
                xml_1 = self.cell[i][4].get()
                xml_2 = self.cell[i][5].get()
                xml_3 = self.cell[i][6].get()

            if field_name is not None and expression is not None and (field_name != "" and field_name != 0) and (expression != "" and expression != 0):
                if self.xml:
                    row = [command, index, field_name, expression, xml_1, xml_2, xml_3]
                else:
                    row = [command, index, field_name, expression]
                table.append(row)
        return table

    def set_grids_tables(self):
        """Sets the grid table of extraction_grid. This is the grid of Extractions."""
        entries = self.extraction_grid.grid_slaves()
        for l in entries:
            l.destroy()

        self.cell = list()
        self.selected_commands = list()
        self.height = 1
        if self.xml:
            new_row = [tk.Label(self.extraction_grid, text="Command"), tk.Label(self.extraction_grid, text="Node Tag"), tk.Label(self.extraction_grid, text="Field Name"),tk.Label(self.extraction_grid, text="Expression"),tk.Label(self.extraction_grid, text="Index"),tk.Label(self.extraction_grid, text="RegEx"),tk.Label(self.extraction_grid, text="Delimeter")]
        else:
            new_row = [tk.Label(self.extraction_grid, text="Command"), tk.Label(self.extraction_grid, text="Index"), tk.Label(self.extraction_grid, text="Field Name"),tk.Label(self.extraction_grid, text="Expression")]
        self.cell.append(new_row)
        self.cell[0][0].grid(row=0, column=0)
        self.cell[0][1].grid(row=0, column=1)
        self.cell[0][2].grid(row=0, column=2)
        self.cell[0][3].grid(row=0, column=3)
        if self.xml:
            self.cell[0][4].grid(row=0, column=4)
            self.cell[0][5].grid(row=0, column=5)
            self.cell[0][6].grid(row=0, column=6)

    # Sets the values for regex expressions and delimeters to extract fields
    def set_table(self, f):
        """Sets the value for regex and delimeters to extract fields."""
        self.set_grids_tables()

        i = 0
        for line in f:
            values = line.split(" ")
            field = self.add_row(cmd=values[0])

            # deleting previous garbage values
            field[1].delete(0, tk.END)
            field[2].delete(0, tk.END)
            field[3].delete(0, tk.END)
            if self.xml:
                field[4].delete(0, tk.END)
                field[5].delete(0, tk.END)
                field[6].delete(0, tk.END)

            # inserting new values
            field[1].insert(0, values[1])
            field[2].insert(0, values[2])
            field[3].insert(0, values[3])
            if self.xml:
                for j in range(4,len(values)):
                    field[j].insert(0, values[j])
            i += 1

    def next_event(self):
        """Callback action for Next Event button"""
        if self.event_index < len(self.parser.events)-1:
            self.event_index +=1
            self.parse_example()

    def prev_event(self):
        """Callback action for Prev Event button"""
        if(self.event_index>1):
            self.event_index -=1
        self.parse_example()

    def parse_example(self):
        """Parses the specified event"""
        if self.check_file_path():
            event = self.parser.events[self.event_index]
            self.txt_example_event.config(text=event)

            example_fields = str(self.parser.parse_event(event, self.get_table(), self.event_index))
            example_fields = example_fields.replace("{","{\n\t")
            example_fields = example_fields.replace(",",",\n\t")
            example_fields = example_fields.replace("}","\n}")
            self.txt_example_fields.config(text=example_fields)

    # Callback action for "Add Field" button to add new row for adding regex or delimeter for parsing
    def add_row(self, cmd=None):
        """Callback action for the Add Field button. Adds new row for extractions"""
        if self.xml:
            cmd = "XML"
        elif cmd is None:
            cmd = self.COMMANDS[0] #default value
        new_command = tk.StringVar(self.root)
        new_command.set(cmd)
        self.selected_commands.append(new_command)

        temp = self.height + 0
        self.button_idx.append(temp)
        if self.xml:
            new_row = [tk.OptionMenu(self.extraction_grid, new_command, *self.COMMANDS), tk.Entry(self.extraction_grid, text=""), tk.Entry(self.extraction_grid, text=""),tk.Entry(self.extraction_grid, text=""), tk.Entry(self.extraction_grid, text="", width="3"),tk.Entry(self.extraction_grid, text=""),tk.Entry(self.extraction_grid, text=""),tk.Button(self.extraction_grid, text=" X ", command= lambda : self.delete_row(temp))]
            new_row[0].configure(state="disabled")
        else:
            new_row = [tk.OptionMenu(self.extraction_grid, new_command, *self.COMMANDS), tk.Entry(self.extraction_grid, text="", width="3"), tk.Entry(self.extraction_grid, text=""),tk.Entry(self.extraction_grid, text=""),tk.Button(self.extraction_grid, text=" X ", command= lambda : self.delete_row(temp))]
        self.cell.append(new_row)
        self.cell[self.height][0].grid(row=self.height, column=0)
        self.cell[self.height][1].grid(row=self.height, column=1)
        new_row[1].insert(0, "" if self.xml else "0")
        self.cell[self.height][2].grid(row=self.height, column=2)
        self.cell[self.height][3].grid(row=self.height, column=3)
        self.cell[self.height][4].grid(row=self.height, column=4)
        if self.xml:
            self.cell[self.height][4].grid(row=self.height, column=4)
            self.cell[self.height][5].grid(row=self.height, column=5)
            self.cell[self.height][6].grid(row=self.height, column=6)
            self.cell[self.height][7].grid(row=self.height, column=7)

        self.height += 1
        return new_row
    def delete_row(self, row_index):
        """Callback to the 'X' button. Destroys the tkinter objects in a certain row."""
        new_idx = self.button_idx.index(row_index)
        items_to_delete = self.extraction_grid.grid_slaves(row=new_idx)
        del self.cell[new_idx]
        del self.button_idx[new_idx]

        for items in items_to_delete:
            items.destroy()
        self.height -= 1




    # The main function
    def main(self):
        self.parse_example()
        self.root.mainloop()

ParserGUI()
