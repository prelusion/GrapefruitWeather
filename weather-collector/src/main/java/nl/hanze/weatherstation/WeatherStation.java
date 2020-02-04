package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.Measurement;
import org.apache.log4j.Logger;
import org.apache.log4j.PropertyConfigurator;

import java.io.IOException;
import java.util.HashMap;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class WeatherStation {
    public static void main(String[] args) throws IOException {
        // This queue will hold all raw unprocessed measurements.
        Queue<String> rawDataQueue = new ConcurrentLinkedQueue<>();

        // This queue contains measurements that are processed.
        Queue<Measurement> measurementQueue = new ConcurrentLinkedQueue<>();

        // This queue contains measurements that will be converted to averages.
        Queue<Measurement> measurementAverageQueue = new ConcurrentLinkedQueue<>();
        Queue<Measurement> measurementAverageLoadQueue = new ConcurrentLinkedQueue<>();

        // This map holds 30 measurements per weather station so an average can be calculated when a result is missing.
        val measurementHistory = new HashMap<Integer, Queue<Measurement>>();

        val measurementAverages = FileAverageHandler.loadAveragesFromFileSystem();

        val measurementCorrector = new HistoricalMeasurementCorrecter(measurementHistory);
        val fileAverageHandler= new FileAverageHandler(measurementAverages);

        val measurementProcessorThread = new Thread(new MeasurementProcessor(measurementCorrector, rawDataQueue, measurementQueue, measurementHistory));
        val averageProcessorThread = new Thread(new AverageProcessor(measurementAverageQueue, measurementAverageLoadQueue, measurementAverages));
        val measurementSaverThread = new Thread(new FileMeasurementSaver(measurementQueue, measurementAverageQueue));
        val averageLoadProcessorThread = new Thread(new AverageLoadProcessor(measurementAverageQueue, measurementAverageLoadQueue, measurementAverages));
        val executor = Executors.newScheduledThreadPool(1);
        executor.scheduleAtFixedRate(fileAverageHandler, 0, 10, TimeUnit.MINUTES);

        measurementProcessorThread.start();
        averageProcessorThread.start();
        measurementSaverThread.start();
        averageLoadProcessorThread.start();

        val healthLogger = Logger.getLogger("server-health");
        val healthExecutor = Executors.newScheduledThreadPool(1);
        healthExecutor.scheduleAtFixedRate(() -> {
            if (!measurementProcessorThread.isAlive()) {
                healthLogger.warn("measurementProcessorThread restarted");
                measurementProcessorThread.start();
            }

            if (!averageProcessorThread.isAlive()) {
                healthLogger.warn("averageProcessorThread restarted");
                averageProcessorThread.start();
            }

            if (!measurementSaverThread.isAlive()) {
                healthLogger.warn("measurementSaverThread restarted");
                measurementSaverThread.start();
            }

            if (!averageLoadProcessorThread.isAlive()) {
                healthLogger.warn("averageLoadProcessorThread restarted");
                averageLoadProcessorThread.start();
            }

            healthLogger.info(String.format("Raw data queue size: %d, Measurement queue size: %d, Measurement average queue size: %d, Measurement average load queue size: %d", rawDataQueue.size(), measurementQueue.size(), measurementAverageQueue.size(), measurementAverageLoadQueue.size()));
        }, 0, 10, TimeUnit.SECONDS);

        Server server = new Server(7789, rawDataQueue);
        server.listen();
    }
}
