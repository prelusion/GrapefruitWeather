package nl.hanze.weatherstation;

import com.google.common.util.concurrent.Futures;
import lombok.val;
import nl.hanze.weatherstation.models.AverageMeasurement;
import nl.hanze.weatherstation.models.Measurement;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Queue;

public class AverageProcessor implements Runnable {
    private final Logger logger;
    private final Queue<Measurement> measurementAverageQueue;
    private final Queue<Measurement> measurementAverageLoadQueue;
    private final HashMap<Integer, List<AverageMeasurement>> measurementAverages;
    private final FileAverageHandler fileAverageHandler;

    public AverageProcessor(
            Queue<Measurement> measurementAverageQueue,
            Queue<Measurement> measurementAverageLoadQueue,
            HashMap<Integer, List<AverageMeasurement>> measurementAverages,
            FileAverageHandler fileAverageHandler
    ) {
        this.logger = LoggerFactory.getLogger(getClass());
        this.measurementAverageQueue = measurementAverageQueue;
        this.measurementAverageLoadQueue = measurementAverageLoadQueue;
        this.measurementAverages = measurementAverages;
        this.fileAverageHandler = fileAverageHandler;
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
                logger.error("Exception in average processor", exception);
            }
        }
    }

    private AverageMeasurement getAverage(int stationId, LocalDateTime date) {
        if (measurementAverages.containsKey(stationId)) {
            for (AverageMeasurement averageMeasurement: measurementAverages.get(stationId)) {
                if (averageMeasurement.getDate().isEqual(date.truncatedTo(ChronoUnit.HOURS))) {
                    return averageMeasurement;
                }
            }
        }

        return null;
    }

    private AverageMeasurement loadAverage(int stationId, LocalDateTime date) {
        if (measurementAverages.containsKey(stationId)) {
            for (AverageMeasurement averageMeasurement: measurementAverages.get(stationId)) {
                if (averageMeasurement.getDate().isEqual(date.truncatedTo(ChronoUnit.HOURS))) {
                    return averageMeasurement;
                }
            }
        } else {
            measurementAverages.put(stationId, new ArrayList<>());
        }

        AverageMeasurement averageMeasurement = fileAverageHandler.loadAverageFromFileSystem(stationId, date);

        if (averageMeasurement == null) {
            averageMeasurement = new AverageMeasurement(date);
        }

        measurementAverages.get(stationId).add(averageMeasurement);

        return averageMeasurement;
    }

    private void process() {
        synchronized (measurementAverages) {
            Measurement measurement;
            while ((measurement = measurementAverageQueue.poll()) != null) {
                val average = getAverage(measurement.getStationId(), measurement.getTimestamp());

                if (average != null) {
                    average.addMeasurement(measurement);
                } else {
                    measurementAverageLoadQueue.offer(measurement);
                }
            }
        }
    }
}
