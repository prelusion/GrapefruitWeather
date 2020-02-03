package nl.hanze.weatherstation;

import org.apache.log4j.Logger;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;
import java.util.Queue;

public class SocketHandler implements Runnable {
    private Logger logger;
    private Socket socket;
    private Queue<String> rawDataQueue;

    public SocketHandler(Socket socket, Queue<String> rawDataQueue) {
        this.logger = Logger.getLogger(this.getClass());
        this.socket = socket;
        this.rawDataQueue = rawDataQueue;
    }

    @Override
    public void run() {
        try {
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            StringBuilder xmlString = new StringBuilder();

            while (true) {
                String line;
                if (Thread.currentThread().isInterrupted() || (line = reader.readLine()) == null) {
                    socket.close();
                    return;
                }

                xmlString.append(line);
                if (line.equals("</WEATHERDATA>")) {
                    rawDataQueue.offer(xmlString.toString());
                    xmlString.setLength(0);
                }
            }
        } catch (IOException exception) {
            logger.error("Error occurred on handing socket", exception);
        }
    }
}
