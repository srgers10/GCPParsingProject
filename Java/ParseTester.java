import java.io.*;
public class ParseTester {
    static String logPath = "../Logs/example_log_data.log";
    static String commPath = "../CommandTables/example_command_table.txt";
    static String outputPath = "../JSON/java_example_output.json";
    static String split = "[\r\n]+";
    public static void main(String args[]){
        //useCLI(args);
        System.out.println("Parsing...");
        long startTime = System.currentTimeMillis();

        ParserCreator parser = new ParserCreator(logPath, commPath, split);
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
        long endTime = System.currentTimeMillis();

        long duration = (endTime - startTime);  
        System.out.println("Duration: "+ duration);
    }

    void useCLI(String[] args){
        String helpText = "java ParseTester -lp <log_path> -cp <command_path> -op <output_path> -s <splitter>";

        CliHelper cp = new CliHelper(args);

        logPath = cp.switchValue("-lp");
        commPath = cp.switchValue("-cp");
        outputPath = cp.switchValue("-op");
        split = cp.switchValue("-s");

        if (logPath.equals("") || commPath.equals("") || outputPath.equals("") || split.equals("")){
            System.out.println("Please use correct syntax:");
            System.out.println(helpText);
            return;
        }
   }
}