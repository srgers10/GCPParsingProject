import java.nio.file.*;
import java.util.ArrayList;
import java.util.Dictionary;
import java.util.Hashtable;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.lang.*;

class MyParser{
    Dictionary<String, String>  delimDict;
    Dictionary<String, String> xmlExprDict;
    
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
        xmlExprDict = new Hashtable<String, String>(){{
            put("<text>", "1");
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
            System.out.println("File not found");
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
        File file = new File("C:\\Users\\pankaj\\Desktop\\test.txt"); 
        
        
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



    //TODO: Split Events in xml file
    private String[] splitXMLEvents(String fileData){
        return null;
    }
  
    public static void main(String args[]){
        System.out.println("Hello There.");
    }
}