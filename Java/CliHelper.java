import java.io.*;
import java.util.*;
/**
 * Allows the ParseTester to run with arguments to help with the automation. Takes the following arguments
 * <hr>
 * -lp 'logPath' -cp 'commandPath' -op 'outputPath' -s 'splitter'
 * <ul>
 *  <li><b>logPath. </b><i>This is the path to the file you want to parse.</i></li> 
 *  <li><b>commandPath. </b><i>This is the path to the command file which includes your regex and delimiter instructions.</i></li> 
 *  <li><b>outputPath. </b><i>This is the path where the parser will save the parsed data to JSON format</i></li> 
 *  <li><b>splitter.</b> This is the RegEx used to split the events. By default it use ([\n\r]+) which splits the file by new line and carrige returns</li> 
 * </ul>
 * <hr>
 * @author Stephen Rogers
 * @author Patrick Kelly
 * @author Utsav Shrestha
 */
public class CliHelper{
    private String[] args = null;
    private HashMap<String, Integer> switchIndexes = new HashMap<String, Integer>();
    private TreeSet<Integer> takenIndexes  = new TreeSet<Integer>();

    public CliHelper(String[] args) {
        parse(args);
    }

    void parse(String[] arguments){
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