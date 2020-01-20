package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.Measurement;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.HashMap;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class WeatherStation {
    public static void main(String[] args) throws IOException {

        // This queue will hold all raw unprocessed measurements.
        Queue<String> rawDataQueue = new ConcurrentLinkedQueue<>();

        // This queue contains measurements that are just converted from xml, but not yet corrected.
        Queue<Measurement> measurementQueue = new ConcurrentLinkedQueue<>();

        // This queue contains measurements that have been corrected and are ready to be saved.
        Queue<Measurement> measurementSaveQueue = new ConcurrentLinkedQueue<>();

        // This map holds 30 measurements per weather station so an average can be calculated when a result is missing.
        HashMap<Integer, Queue<Measurement>> measurementHistory = new HashMap<>();

        Thread measurementProcessorThread = new Thread(new MeasurementProcessorImpl(rawDataQueue, measurementQueue));
        Thread measurementCorrectorThread = new Thread(new MeasurementCorrecterImpl(measurementQueue, measurementSaveQueue, measurementHistory));
        Thread measurementSaverThread = new Thread(new FileMeasurementSaver(measurementSaveQueue));

        measurementProcessorThread.start();
        measurementCorrectorThread.start();
        measurementSaverThread.start();

        val healthLogger = LoggerFactory.getLogger("server-health");
        ScheduledExecutorService healthExecutor = Executors.newScheduledThreadPool(1);
        healthExecutor.scheduleAtFixedRate(() -> {
            val rawDataQueueSize = rawDataQueue.size();
            val measurementQueueSize = measurementQueue.size();
            val measurementSaveQueueSize = measurementSaveQueue.size();

            healthLogger.info("Raw data queue size: {}, Measurement queue size: {}, Measurement save queue size: {}", rawDataQueueSize, measurementQueueSize, measurementSaveQueueSize);
        }, 0, 5, TimeUnit.SECONDS);

        Server server = new Server(7789, rawDataQueue);
        server.listen();
    }
}
