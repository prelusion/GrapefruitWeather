package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.AverageMeasurement;
import nl.hanze.weatherstation.models.Measurement;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Queue;
import java.util.stream.Collectors;

public class AverageLoadProcessor implements Runnable {
    private final Logger logger;
    private final Queue<Measurement> measurementAverageQueue;
    private final Queue<Measurement> measurementAverageLoadQueue;
    private final HashMap<Integer, List<AverageMeasurement>> measurementAverages;
    private final FileAverageHandler fileAverageHandler;

    public AverageLoadProcessor(Queue<Measurement> measurementAverageQueue, Queue<Measurement> measurementAverageLoadQueue, HashMap<Integer, List<AverageMeasurement>> measurementAverages, FileAverageHandler fileAverageHandler) {
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
                logger.error("Exception in load average processor", exception);
            }
        }
    }

    private void process() {
        List<Measurement> measurements = new ArrayList<>();
        Measurement measurement;
        while ((measurement = measurementAverageLoadQueue.poll()) != null) {
            measurements.add(measurement);
        }

        val ids = measurements.stream().map(m -> Pair.of(m.getStationId(), m.getTimestamp())).collect(Collectors.toList());

        val loadedAverages = FileAverageHandler.loadAveragesFromFileSystem(ids);

        measurements.forEach(measurement1 -> {
            val averages = measurementAverages.computeIfAbsent(measurement1.getStationId(), i -> new ArrayList<>());
            val average = averages.stream()
                    .filter(averageMeasurement -> averageMeasurement.getDate().equals(measurement1.getTimestamp()))
                    .findFirst();

            if (average.isEmpty()) {
                val a = loadedAverages.getOrDefault(measurement1.getStationId(), new ArrayList<>())
                        .stream()
                        .filter(averageMeasurement -> measurement1.getTimestamp().isEqual(averageMeasurement.getDate()))
                        .findFirst()
                        .orElse(new AverageMeasurement(measurement1.getTimestamp()));
                measurementAverages.get(measurement1.getStationId()).add(a);
            }
        });

        /*loadedAverages.forEach((stationId, averageMeasurements) -> {
            val averages = measurementAverages.computeIfAbsent(stationId, i -> new ArrayList<>());
            averageMeasurements.forEach(averageMeasurement -> {
                if (averages.stream().filter(averageMeasurement1 -> averageMeasurement1.getDate().isEqual(averageMeasurement.getDate())).count() == 0) {
                    averages.add(averageMeasurement);
                }
            });
        });*/

        for (Measurement m: measurements) {
            measurementAverageQueue.offer(m);
        }
    }
}
