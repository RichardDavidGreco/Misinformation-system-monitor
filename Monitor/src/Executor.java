import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Executor implements Runnable{
	private String command;
	private String arguments;
	
	public Executor(String cmd, String arg){
		command = cmd;
		arguments = arg;
	}

	@Override
	public void run() {
		Process p = null;
		String risposta = "";
		try {
			p = Runtime.getRuntime().exec(command+" "+arguments);
			BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));
			BufferedReader err = new BufferedReader(new InputStreamReader(p.getErrorStream()));
			if((risposta = in.readLine()) == null)
				printError(err);
			else
				printRisp(risposta, in);
		} catch (IOException e) {
			e.printStackTrace();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
	
	private static void printError(BufferedReader err) throws IOException{
		String error = null;
		while((error = err.readLine())!= null){
			System.out.println(error);
		}
	}
	
	public void printRisp(String first, BufferedReader in) throws IOException, InterruptedException{
		String risp = first;
		while((first = in.readLine())!= null){
			risp += first;
		}
		Thread t = new Thread(new Analyzer("python3 ../../text_analyzer.py", risp));
		t.start();
		t.join();
	}
	
}