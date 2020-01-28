package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.Measurement;
import nl.hanze.weatherstation.models.AverageMeasurement;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
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

        // This map holds 30 measurements per weather station so an average can be calculated when a result is missing.
        val measurementHistory = new HashMap<Integer, Queue<Measurement>>();

        val measurementAverages = new HashMap<Integer, List<AverageMeasurement>>();

        val measurementCorrector = new HistoricalMeasurementCorrecter(measurementHistory);
        val fileAverageHandler= new FileAverageHandler(measurementAverages);

        val measurementProcessorThread = new Thread(new MeasurementProcessor(measurementCorrector, rawDataQueue, measurementQueue, measurementHistory));
        val averageProcessorThread = new Thread(new AverageProcessor(measurementAverageQueue, measurementAverages, fileAverageHandler));
        val measurementSaverThread = new Thread(new FileMeasurementSaver(measurementQueue, measurementAverageQueue));
        val executor = Executors.newScheduledThreadPool(1);
        executor.scheduleAtFixedRate(fileAverageHandler, 0, 1, TimeUnit.MINUTES);

        measurementProcessorThread.start();
        averageProcessorThread.start();
        measurementSaverThread.start();

        val healthLogger = LoggerFactory.getLogger("server-health");
        val healthExecutor = Executors.newScheduledThreadPool(1);
        healthExecutor.scheduleAtFixedRate(() -> {
            healthLogger.info("Raw data queue size: {}, Measurement queue size: {}, Measurement average queue size: {}", rawDataQueue.size(), measurementQueue.size(), measurementAverageQueue.size());
        }, 0, 5, TimeUnit.SECONDS);

        Server server = new Server(7789, rawDataQueue);
        server.listen();
    }
}
