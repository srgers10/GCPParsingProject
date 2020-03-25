parsed_json_path = ""
f = open(parsed_json_path, "r")
json_input = f.read()

try:
    decoded = json.loads(json_input)
 
    # Access data
    for event in decoded['events']:
        desc =  event['description']
        
 
except (ValueError, KeyError, TypeError):
    print "JSON format error"