import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Dictionary;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.regex.*;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import java.util.TreeSet;

class CliParser{
    private String[] args = null;
    private HashMap<String, Integer> switchIndexes = new HashMap<String, Integer>();
    private TreeSet<Integer> takenIndexes  = new TreeSet<Integer>();

    public CliParser(String[] args) {
        parse(args);
    }

    public void parse(String[] arguments){
        this.args = arguments;
        //locate switches.
        switchIndexes.clear();
        takenIndexes.clear();
        for(int i=0; i < args.length; i++) {
            if(args[i].startsWith("-") ){
                switchIndexes.put(args[i], i);
                takenIndexes.add(i);
            }
        }
    }

    public String switchValue(String switchName) {
        try{
            int switchIndex = switchIndexes.get(switchName);
            if(switchIndex + 1 < args.length){
                takenIndexes.add(switchIndex +1);
                return args[switchIndex +1];
            }
        }
        catch(Exception ex){
            return "";
        }
        return "";
    }
}

public class MyParser{
    Dictionary<String, String>  delimDict;
    HashMap<String, Integer> xmlExprDict;
    HashMap<String, Pattern> regexPatterns = new HashMap<String, Pattern>();

    String[] events;
    Dictionary<String, String> fields;
    ArrayList<String[]> commandTable;
    NodeList xml_nodes = null;

    String logPath;
    String commandPath;
    String eventSplitter;

    public MyParser(String logPath, String commandPath, String eventSplitter){
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

    //Splits all events by a specified 'Splitter'
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

    //Command table is the list of commands and field names needed to extract event's fields
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

    //Extracts value based on given regular expression
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

            if(m.find()){
                toReturn = (m.group(index));
            }else{
                System.out.println("No Match:" + expression);
            }
            return toReturn;
        } catch (Exception e){
            e.printStackTrace();
            return toReturn;
        }
        //return val;
    }

    //Extracts value based on the provided delimeter and index
    public String extractDelimField(String event, int index, String delimiter) {
        String delim = delimDict.get(delimiter);
        //System.out.println(event);
        String[] temp = event.split(delim);
        //System.out.println(temp.length);
        return temp[index];
    }

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

    //Extracts value based on XML attributes or text along with other options such as regex and delimeter
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
                    if(xmlExprDict.containsKey(expression)) {
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

    //Returns json with field and value pairs, based on the given log file and command table
    public String parse(){
        Dictionary<String, String> toReturn = new Hashtable<String, String>();
        String json = "{ \"events\": [ {";
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
            if(i!=1) json += ", {";
            for(int j = 0; j< parsedEvent.length; j++){
                if(j!=0) json += ",";
                String fieldName = parsedEvent[j][0];
                String val = parsedEvent[j][1];
                toReturn.put(fieldName, val);

                json += "\""+fieldName + "\": \"" + val + "\"";
            }
            json += "}";
        }
        json +="]\n}";
        fields = toReturn;
        return json;
    }

    /* Returns a dictionary of fields and values for the given event
       key = field_name, value = field_value
       table = [fields],
       For Regex and Delimiter: [index: 0 = command, 1= group/split index, 2 = field_name, 3 = expression]
       For XML: [index: 0 = command, 1= Node Name, 2 = field_name, 3 = Attribute Name/<expression>], 4 = group/split index, 5 = Regex Expression, 6 = Delimiter */
    public String[][] parseEvent(String event, int eventIndex){
        String[][] toReturn = new String[commandTable.size()][2]; //0 == field name, 1 == value
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


    public static void main(String args[]){
        // String logPath = "../Logs/example_log_data.log";
        // String commPath = "../CommandTables/example_command_table.txt";
        // String outputPath = "../JSON/java_example_output.json";
        // String split = "[\r\n]+";
        String helpText = "java MyParser -lp <log_path> -cp <command_path> -op <output_path> -s <splitter>";

        CliParser cp = new CliParser(args);

        String logPath = cp.switchValue("-lp");
        String commPath = cp.switchValue("-cp");
        String outputPath = cp.switchValue("-op");
        String split = cp.switchValue("-s");

        if (logPath.equals("") || commPath.equals("") || outputPath.equals("") || split.equals("")){
            System.out.println("Please use correct syntax:");
            System.out.println(helpText);
            return;
        }

        System.out.println("Parsing...");
        MyParser parser = new MyParser(logPath, commPath, split);
        String json = parser.parse();

        Writer writer = null;

        try {
            writer = new BufferedWriter(new OutputStreamWriter(
                new FileOutputStream(outputPath), "utf-8"));
            writer.write(json);
        } catch (IOException ex) {
            // Report
        } finally {
        try {writer.close();} catch (Exception ex) {/*ignore*/}
        }

        System.out.println(json);
        System.out.println("\nDone! Saved to "+ outputPath);
    }
}
