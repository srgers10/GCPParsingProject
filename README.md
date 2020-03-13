# GCP Parsing Project
Tool for parsing and normalizing log data to ease injestion into Google Cloud Platform (Big Query) & Splunk

**The GUI should only be used for the creation of the command table**

### Developers: Stephen Rogers, Patrick Kelly, Utsav Shrestha


## Using the GUI
The GUI tool is to help in the creation of the command table file. It allows user to view and test their RegEx and extractions in real time and cycle through multiple events to make sure it works in all scenarios. 

[gui]: https://github.com/srgers10/GCPParsingProject/blob/master/Other/pics/Capture.PNG
[gui]

1. Run the ParserGUI.py file
1. Click the **Open Log** button and selected log file you would like to parse.

1. Field Extraction
   1. Click the **Add Row** for the amount of fields you would like to extract from the data.
      1. Select the **Command**: the method of extraction(RegEx, Delimiter)
      1. Select the **Index**: the nth element that gets extracted from the expression (The group # for RegEx, the index # for delimiter)
      1. Write the **Field Name** you would like to call the value.
      1. Write the expression. 
         * **Regex**: write the regular expression here.
         * **Delimiter**: write the delimiter here. (ex: if values are seperated by spaces, type \<space\>
   1. If you have already created a command table, you can load it by clicking the **Load** button
   
1. You can press the **Update** button to update the example output with the new field expressions
1. When you are happy with the result, press the **Parse** button and it will run the field extraction over all events in the log file and save it in JSON format to the desired location

## Using the Parser

via a command line or a script run the following command
`python Parser.py log_file command_table_file output_file`
ex:
`python Parser.py example_log_file.log example_command_table.txt my_fields.json`

When you run the command it will parse the log file by the given commands and store the values in JSON format.
