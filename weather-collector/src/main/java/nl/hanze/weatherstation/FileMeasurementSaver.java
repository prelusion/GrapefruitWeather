package nl.hanze.weatherstation;

import com.google.common.primitives.Bytes;
import lombok.val;
import nl.hanze.weatherstation.models.Measurement;
import org.slf4j.Logger;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Queue;

public class FileMeasurementSaver implements Runnable {
    private final Logger logger;
    private final Queue<Measurement> measurementSaveQueue;
    private final MeasurementConverter measurementConverter;
    private final List<StationIndexEntry> stationIndex;
    private final Map<Integer, Integer> indexInsertLocations;
    private int collectionId;

    public FileMeasurementSaver(
            Logger logger,
            Queue<Measurement> measurementSaveQueue,
            MeasurementConverter measurementConverter,
            List<StationIndexEntry> stationIndex,
            Map<Integer, Integer> indexInsertLocations,
            int startCollectionId
    ) {
        this.logger = logger;
        this.measurementSaveQueue = measurementSaveQueue;
        this.measurementConverter = measurementConverter;
        this.stationIndex = stationIndex;
        this.indexInsertLocations = indexInsertLocations;
        this.collectionId = startCollectionId;
    }

    @Override
    public void run() {
        while (true) {
            if (Thread.currentThread().isInterrupted()) {
                logger.info(String.format("%s interrupted", this.getClass().toString()));
                return;
            }

            processBatch();
        }
    }

    /**
     * Collect a batch of measurements.
     */
    private List<Measurement> collect() {
        List<Measurement> measurements = new ArrayList<>();

        for (int i = 0; i < measurementSaveQueue.size(); i++) {
            val measurement = measurementSaveQueue.poll();

            if (measurement == null) {
                break;
            }

            measurements.add(measurement);
        }

        return measurements;
    }

    public void processBatch() {
        val measurements = collect().stream()
                .map(measurementConverter::convertMeasurementToByteArray)
                .reduce(Bytes::concat);

        if (!measurements.isPresent()) {
            return;
        }

        val file = new File(String.format("/measurements/%s.wsmc", collectionId));

        try {
            file.createNewFile();

            try (val outputStream = new FileOutputStream(file, true)) {
                outputStream.write(measurements.get());
            }
        } catch (IOException exception) {
            logger.error("Writing measurement to file failed", exception);
        }
    }
}
