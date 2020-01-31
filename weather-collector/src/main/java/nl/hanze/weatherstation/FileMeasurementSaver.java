package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.Measurement;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Queue;

public class FileMeasurementSaver implements Runnable {
    private final Logger logger;
    private final Queue<Measurement> measurementQueue;
    private final Queue<Measurement> measurementAverageQueue;
    private int collectionId;
    private int collectionCheckCounter = 100;

    public FileMeasurementSaver(
            Queue<Measurement> measurementQueue,
            Queue<Measurement> measurementAverageQueue
    ) {
        this.logger = LoggerFactory.getLogger(this.getClass());
        this.measurementQueue = measurementQueue;
        this.measurementAverageQueue = measurementAverageQueue;

        val files = FileHelper.extractExtensionSequences("/measurements", "wsmc");
        this.collectionId = files.size() == 0 ? 0 : files.get(0);
    }

    @Override
    public void run() {
        while (true) {
            if (Thread.currentThread().isInterrupted()) {
                return;
            }

            try {
                process();
            } catch (Exception exception) {
                logger.error("Exception in file measurement saver", exception);
            }
        }
    }

    public void process() {
        val file = new File(String.format("/measurements/%s.wsmc", collectionId));

        try {
            file.createNewFile();

            try (val outputStream = new FileOutputStream(file, true)) {
                Measurement measurement;
                while ((measurement = measurementQueue.poll()) != null) {
                    outputStream.write(MeasurementConverter.convertMeasurementToByteArray(measurement));

                    // When the measurement is saved it can be offered to the average queue.
                    measurementAverageQueue.offer(measurement);
                }
            }
        } catch (IOException exception) {
            logger.error("Writing measurement to file failed", exception);
        }

        if (file.length() > (1024 * 1024 * 30)) {
            collectionId++;
        }
    }
}
