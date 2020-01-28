package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.AverageMeasurement;
import nl.hanze.weatherstation.models.Measurement;
import org.slf4j.LoggerFactory;

import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Queue;

public class AverageProcessor implements Runnable {
    private final Queue<Measurement> measurementAverageQueue;
    private final HashMap<Integer, List<AverageMeasurement>> measurementAverages;
    private final FileAverageHandler fileAverageHandler;

    public AverageProcessor(
            Queue<Measurement> measurementAverageQueue,
            HashMap<Integer, List<AverageMeasurement>> measurementAverages,
            FileAverageHandler fileAverageHandler
    ) {
        this.measurementAverageQueue = measurementAverageQueue;
        this.measurementAverages = measurementAverages;
        this.fileAverageHandler = fileAverageHandler;
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

    private void process() {
        synchronized (measurementAverages) {
            Measurement measurement;
            while ((measurement = measurementAverageQueue.poll()) != null) {
                Measurement finalMeasurement = measurement;
                if (!measurementAverages.containsKey(measurement.getStationId())) {
                    measurementAverages.put(measurement.getStationId(), new ArrayList<>());
                }

                AverageMeasurement averageMeasurement = measurementAverages.get(measurement.getStationId())
                        .stream()
                        .filter(a -> a.getDate().isEqual(finalMeasurement.getTimestamp().truncatedTo(ChronoUnit.HOURS)))
                        .findFirst()
                        .orElse(null);

                if (averageMeasurement == null) {
                    averageMeasurement = fileAverageHandler.loadAverageFromFileSystem(measurement.getStationId(), measurement.getTimestamp());
                    if (averageMeasurement != null) {
                        measurementAverages.get(measurement.getStationId()).add(averageMeasurement);
                    }
                }

                if (averageMeasurement == null) {
                    measurementAverages.get(measurement.getStationId()).add(averageMeasurement = new AverageMeasurement(finalMeasurement.getTimestamp()));
                }

                averageMeasurement.addMeasurement(measurement);
            }
        }
    }
}
