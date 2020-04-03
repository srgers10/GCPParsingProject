import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import javax.xml.parsers.*;
import org.w3c.dom.*;


/**
 * parses out fields within any given file, based on a given command file. Fields can be extracted by either RegEx, a Delimitter, or via an XML field
 * <hr>
 *  <div><b>Command Format: </b> 'Command' 'Index' 'FieldName' 'Expression'</div>
 *  <div>ex: Delimitter 0 destIP |</div>
 *  <div>ex: RegEx 2 timestamp (\[.*\])</div>
 *  <br>
 *  <ul>
 *      <li><b>Command</b> - the type of extraction
 *        <ul> 
 *            <li>RegEx - extract field with a regular expression</li>
 *            <li>Delimitter - grabs the nth element split by a character</li>
 *            <li>XML - extracts field by given XML tag name</li>
 *          </ul>
 *      </li>
 *      <li><b>Index</b> - the nth element that was extracted from the expression
 *      </li>
 *      <li><b>FieldName</b> - the alias (JSON key) for the extracted data
 *      </li>
 *      <li><b>Expression</b> - the expression used to extract the value
 * *        <ul> 
 *            <li>RegEx - RegEx expression</li>
 *            <li>Delimitter - The character to split by</li>
 *            <li>XML - the XML tag name</li>
 *          </ul>
 *      </li>
 *  </ul>
 * <hr>

 * @author Stephen Rogers
 * @author Patrick Kelly
 * @author Utsav Shrestha
 */
public class ParserCreator{
    Dictionary<String, String>  delimDict;
    HashMap<String, Integer> xmlExprDict;
    HashMap<String, Pattern> regexPatterns = new HashMap<String, Pattern>();
    HashMap<String, String[]> delimitedEvents = new HashMap<String, String[]>();

    String[] events;
    Dictionary<String, String> fields;
    ArrayList<String[]> commandTable;
    NodeList xml_nodes = null;

    String logPath;
    String commandPath;
    String eventSplitter;

    /**
     * 
     * @param logPath the path to the file you want to parse
     * @param commandPath the path to the command table
     * @param eventSplitter the RegEx to split the log file by
     */
    public ParserCreator(String logPath, String commandPath, String eventSplitter){
        delimDict = new Hashtable<String, String>(){{
            put("<space>", " ");
            put("<hyphen>", "-");
        }};
        xmlExprDict = new HashMap<String, Integer>(){{
            put("<text>", 1);
        }};

        this.logPath = logPath;
        this.commandPath = commandPath;

        commandTable = getCommandTable(commandPath);
        this.eventSplitter = eventSplitter;
        try{
            events = splitEvents(logPath, eventSplitter);
        } catch (Exception e){
            e.printStackTrace();
        }
    }

    /**
     * Splits a given file path into a String[] of events
     * @param path the path to the file you want to spilt
     * @param splitter the regex to split the events by
     * @return an array of events (represented by strings)
     */
    public String[] splitEvents(String path, String splitter){
        String fileData = "";
        try {
            fileData = new String(Files.readAllBytes(Paths.get(path)));
        } catch (Exception e){
            System.out.println("File not found" + e);
            return null;
        }
        String[] toReturn = null;
        if(splitter != "XML"){
            toReturn = fileData.split(splitter);
        }

        return toReturn;
    }

    /**
     * 
     * Extracts the given commands in a command table and saves each command into a String[] where {
     * 
     * <ul>

     * <li>XML: [0] = command, [1]= Node Name, [2] = field_name, [3] = Attribute Name/expression], [4] = group/split index, [5] = Regex Expression, [6] = Delimiter </li>
     * </ul>
     * <div><i>Command table is the list of commands and field names needed to extract event's fields</i></div>
     * @param commandPath the path to the command table
     * @return an ArrayList of all commands in the command table
     */
    public ArrayList<String[]> getCommandTable(String commandPath){
        ArrayList<String[]> toReturn = new ArrayList<String[]>();
        File file = new File(commandPath);

        try{
            BufferedReader br = new BufferedReader(new FileReader(file));
            String line = "";

            boolean temp = false;
            while ((line = br.readLine()) != null) {
                String[] field = line.split(" ");
                if(temp){
                    eventSplitter = field[1];
                    temp = false;
                } else{
                    toReturn.add(field);

                }
            }
            br.close();

        } catch (Exception e){
            e.printStackTrace();
            return null;
        }
        return toReturn;
    }
    /**
     * Extracts value based on given regular expression
     * @param event  the input you want to extract the value from
     * @param index the regex group to return
     * @param expression the regular expression
     * @return the value extracted by the given expression
     */

    public String extractRegexField(String event, int index, String expression) {
        String toReturn = "";
        try{
            Pattern r;
            if(regexPatterns.containsKey(expression)){
                r = regexPatterns.get(expression);
            }else{
                r = Pattern.compile(expression);
                regexPatterns.put(expression, r);
            }

            Matcher m = r.matcher(event);

            while (m.find()){
                toReturn += " " + m.group(1);
            }

            return toReturn;
        }catch (Exception e){
            e.printStackTrace();
            return toReturn;
        }
        //return val;
    }
    /**
     * Extracts value based on the provided delimeter and index
     * @param event  the input you want to extract the value from
     * @param index the nth element form the split values
     * @param delimiter the character to split by
     * @return the value extracted by the given delimiter
     */
    public String extractDelimField(String event, int index, String delimiter) {
        String[] fields = null;
        if(delimitedEvents.containsKey(delimiter)){
            fields = delimitedEvents.get(delimiter.trim());
        }
        else{
            String delim = delimDict.get(delimiter.trim());
            if (delim != null)
                fields = event.split(delim);
            else{
                System.out.println("Invalid Delimiter");
                return "";
            }
        }
        if (fields != null && fields.length > index)
            return fields[index];

        return "";
    }

    /**
     * Splits an XML File by the "Events" tag
     * @return list of event nodes. 
     */
    public NodeList splitXML(){
        try
        {
            File inputFile = new File(this.logPath);
            DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
            DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
            Document doc = dBuilder.parse(inputFile);
            doc.getDocumentElement().normalize();
            Element root = doc.getDocumentElement();
            NodeList all_child = root.getChildNodes();
            String tagName = "";

            // get the name of firstchildnode
            // This is required becuase java considers white-space as a [#text node but we are looking for element node
            for (int i=0; i<all_child.getLength();i++) {
                Node curNode = all_child.item(i);
                if (curNode.getNodeType() == Node.ELEMENT_NODE) {
                    tagName = curNode.getNodeName();
                }
            }

            NodeList childrens = root.getElementsByTagName(tagName);
            return childrens;
        } catch (Exception e) {
           e.printStackTrace();
        }
        return null;
    }
    /**
     * Extracts value based on XML attributes or text along with other options such as regex and delimeter
     * 
     * @param xPath the path to the given xml tag. can also be the name of the tag
     * @param expression text = extract value from text of the node, else = extract value from attribute of the node
     * @param index index
     * @param regex regex
     * @param delimiter delimiter
     * @param eventIndex event index
     * @return the field value
     */

    public String extractXMLField(String xPath, String expression, int index, String regex, String delimiter, int eventIndex) {
        try {
            if(this.xml_nodes == null){
                this.xml_nodes = splitXML();
            }
            Element desiredChild = (Element) this.xml_nodes.item(eventIndex);
            NodeList xPathNode = desiredChild.getElementsByTagName(xPath);
            for (int i=0; i<xPathNode.getLength();i++) {
                String value = "";
                Node curNode = xPathNode.item(i);
                if (curNode.getNodeType() == Node.ELEMENT_NODE) {
                    Element curElement = (Element) curNode;
                    // extract value from text of the node
                    if(xmlExprDict.containsKey(expression.trim())) {
                        if(xmlExprDict.get(expression)==1) {
                            value = curElement.getTextContent();
                        }
                    }
                    // extract value from attribute of the node
                    else {
                        value = curElement.getAttribute(expression);
                    }

                    // additionally extract the required value by using regex or delimiter to the xml extracted above value
                    if (regex != null && regex != "") {
                        return extractRegexField(value, index, regex);
                    }
                    else if(delimiter != null && delimiter != "") {
                        return extractDelimField(value, index, delimiter);
                    }

                    return value;
                }
            }

        } catch (Exception e) {
           e.printStackTrace();
        }
        return null;
    }

    /**
     * parses the log file with the command table
     * @return json with field and value pairs, based on the given log file and command table
     */
    
    public String parse(){
        Dictionary<String, String> toReturn = new Hashtable<String, String>();
        StringBuilder json =new StringBuilder("{ \"events\": [ {");
        int noOfEvents = 0;
        boolean xml = this.eventSplitter.equals("XML");

        if (xml){
            if (this.xml_nodes == null){
                this.xml_nodes = splitXML();
            }
            noOfEvents = this.xml_nodes.getLength();
        }
        else{
            noOfEvents = events.length;
        }
        for(int i = 1; i < noOfEvents; i++){
            String[][] parsedEvent = parseEvent(xml ? "" : events[i], i);
            if(i!=1) json.append(", {");
            for(int j = 0; j< parsedEvent.length; j++){
                if(j!=0) json.append(",");
                String fieldName = parsedEvent[j][0];
                String val = parsedEvent[j][1];
                toReturn.put(fieldName, val);

                json.append("\""+fieldName + "\": \"" + val + "\"");
            }
            json.append("}");
        }
        json.append("]\n}");
        fields = toReturn;
        return json.toString();
    }

    /**
     * Parses out the fields of a given event by the command table
     * @param event event
     * @param eventIndex event index
     * @return a 2D array of [field][0 == field name, 1 == value]
     */
    /* Returns a dictionary of fields and values for the given event
       key = field_name, value = field_value
       table = [fields],
       For Regex and Delimiter: [index: 0 = command, 1= group/split index, 2 = field_name, 3 = expression]
       For XML: [index: 0 = command, 1= Node Name, 2 = field_name, 3 = Attribute Name/<expression>], 4 = group/split index, 5 = Regex Expression, 6 = Delimiter 
    */
    public String[][] parseEvent(String event, int eventIndex) {
        String[][] toReturn = new String[commandTable.size()][2]; //0 == field name, 1 == value
        this.delimitedEvents = new HashMap<String, String[]>();
        for(int i = 0; i < commandTable.size(); i++){
            String[] field = commandTable.get(i);
            String key = field[2];
            String val = "";
            if(key != "" && key != null){
                String command = field[0];
                int index = 0;
                String expression = field[3];
                switch(command){
                    case "RegEx":
                        index = Integer.parseInt(field[1]);
                        val = extractRegexField(event, index, expression);
                        break;
                    case "Delimiter":
                        index = Integer.parseInt(field[1]);
                        val = extractDelimField(event, index, expression);
                        break;
                    case "XML":
                        String xPath = field[1];
                        index = field.length > 4 ? Integer.parseInt(field[4]): 0;
                        String regex = field.length >5 ? field[5]: "";
                        String delim = field.length >6 ? field[6]: "";

                        val = extractXMLField(xPath, expression, index, regex, delim, eventIndex);

                        break;
                }
                toReturn[i][0] = key;
                val = val == null ? "": val;
                toReturn[i][1] = val;
            }
        }
        return toReturn;
    }
}
