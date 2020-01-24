package nl.hanze.weatherstation;

import lombok.val;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Queue;

public class Server {
    private final Logger logger;
    private final int port;
    private final Queue<String> rawDataQueue;

    public Server(Logger logger, int port, Queue<String> rawDataQueue) {
        this.logger = logger;
        this.port = port;
        this.rawDataQueue = rawDataQueue;
    }

    public void listen() throws IOException {
        val serverSocket = new ServerSocket(port);

        while (true) {
            if (Thread.currentThread().isInterrupted()) {
                serverSocket.close();
                return;
            }

            Socket socket = serverSocket.accept();
            handle(socket);
        }
    }

    private void handle(Socket socket) {
        val logger = LoggerFactory.getLogger(String.format("socket-handler-%d", socket.getLocalPort()));
        val socketHandler = new SocketHandler(socket, rawDataQueue, logger);
        val thread = new Thread(socketHandler);
        thread.start();
    }
}
