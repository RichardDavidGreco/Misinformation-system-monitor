import java.io.BufferedReader;
import java.io.IOException;

public class Analyzer extends Executor{

	public Analyzer(String cmd, String arg) {
		super(cmd, arg);
	}
	
	public void printRisp(String first, BufferedReader in) throws IOException, InterruptedException{
		String risp = first;
		while((first = in.readLine())!= null){
			risp += first;
		}
		System.out.println(risp);
	}

}
