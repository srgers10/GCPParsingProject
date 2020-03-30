import java.nio.file.*;
import java.util.ArrayList;
import java.util.Dictionary;
import java.util.HashMap;
import java.util.Hashtable;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.lang.*;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element;

class MyParser{
    Dictionary<String, String>  delimDict;
    HashMap<String, Integer> xmlExprDict;
    
    String[] events;
    Dictionary<String, String> fields;
    ArrayList<String[]> commandTable;

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
        String[] toReturn;
        if(splitter=="XML"){
            toReturn = splitXMLEvents(fileData);
        } else{
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

            boolean temp = true;
            while ((line = br.readLine()) != null) {
                String[] field = line.split("");
                if(temp){
                    eventSplitter = field[1];
                    temp = false;
                } else{
                    toReturn.add(field);
                }
            }
            br.close();
        } catch (Exception e){
            return null;
        }
        return toReturn;
    }
    
    //TODO: Extracts value based on given regular expression
    public String extractRegexField(String event, int index, String expression) {
        return null;
    }
    
    //TODO: Extracts value based on the provided delimeter and index
    public String extractDelimField(String event, int index, String delimiter) {
        return null;
    }
    public String extractXMLField(String xPath, String expression, int index, String regex, String delimiter, int eventIndex) {
        try {
            File inputFile = new File(logPath);
            DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
            DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
            Document doc = dBuilder.parse(inputFile);
            doc.getDocumentElement().normalize();
            Element root = doc.getDocumentElement();
            NodeList all_child = root.getChildNodes();
            String tagName = "";
            for (int i=0; i<all_child.getLength();i++) {
                Node curNode = all_child.item(i);
                if (curNode.getNodeType() == Node.ELEMENT_NODE) { 
                    tagName = curNode.getNodeName();
                }
            }
            
            NodeList childrens = root.getElementsByTagName(tagName);
            Element desiredChild = (Element) childrens.item(eventIndex);
            NodeList xPathNode = desiredChild.getElementsByTagName(xPath);
            for (int i=0; i<xPathNode.getLength();i++) {
                String value = "";
                Node curNode = xPathNode.item(i);
                if (curNode.getNodeType() == Node.ELEMENT_NODE) {
                    Element curElement = (Element) curNode;
                    if(xmlExprDict.containsKey(expression)) {
                        if(xmlExprDict.get(expression)==1) {
                            value = curElement.getTextContent();
                        }
                    }
                    else {
                        value = curElement.getAttribute(expression);
                    }
                    
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

    //TODO: Split Events in xml file
    private String[] splitXMLEvents(String fileData){
        return null;
    }
  
    public static void main(String args[]){
        System.out.println("Hello There.");
        Path currentDir = Paths.get(".", "src\\Logs\\example_xml_log_data.xml");
        System.out.println(new MyParser(currentDir.toAbsolutePath().toString(), "..\\CommandTables\\xml_command_table.txt", " ").extractXMLField("Computer", "<text>", 0, "", "", 0));
    }
}