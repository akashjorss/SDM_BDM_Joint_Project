import org.apache.spark.streaming.api.java.JavaDStream;
import twitter4j.Status;

public class Display_Tweets {

    public static void displayAllTweets(JavaDStream<Status> tweets) {
        JavaDStream<String> statuses = tweets.map(status -> status.getUser().getName() + " -- " + status.getText());
        statuses.print();
    }

}
