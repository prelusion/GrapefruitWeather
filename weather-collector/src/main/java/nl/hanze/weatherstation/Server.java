package nl.hanze.weatherstation;

import lombok.val;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Queue;

public class Server {
    private final int port;
    private final Queue<String> rawDataQueue;

    public Server(int port, Queue<String> rawDataQueue) {
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
        val socketHandler = new SocketHandler(socket, rawDataQueue);
        val thread = new Thread(socketHandler);
        thread.start();
    }
}
