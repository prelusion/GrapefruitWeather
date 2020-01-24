package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.Measurement;
import org.slf4j.Logger;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Queue;

public class FileMeasurementSaver implements Runnable {
    private final Logger logger;
    private final Queue<Measurement> measurementQueue;
    private final MeasurementConverter measurementConverter;
    private int collectionId;

    public FileMeasurementSaver(
            Logger logger,
            Queue<Measurement> measurementQueue,
            MeasurementConverter measurementConverter,
            int startCollectionId
    ) {
        this.logger = logger;
        this.measurementQueue = measurementQueue;
        this.measurementConverter = measurementConverter;
        this.collectionId = startCollectionId;
    }

    @Override
    public void run() {
        while (true) {
            if (Thread.currentThread().isInterrupted()) {
                return;
            }

            process();
        }
    }

    public void process() {
        val file = new File(String.format("/measurements/%s.wsmc", collectionId));

        try {
            file.createNewFile();

            try (val outputStream = new FileOutputStream(file, true)) {
                Measurement measurement;
                while ((measurement = measurementQueue.poll()) != null) {
                    outputStream.write(measurementConverter.convertMeasurementToByteArray(measurement));
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
