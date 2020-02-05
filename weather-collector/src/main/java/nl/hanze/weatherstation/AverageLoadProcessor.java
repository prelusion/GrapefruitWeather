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

    public AverageLoadProcessor(Queue<Measurement> measurementAverageQueue, Queue<Measurement> measurementAverageLoadQueue, HashMap<Integer, List<AverageMeasurement>> measurementAverages) {
        this.logger = LoggerFactory.getLogger(getClass());
        this.measurementAverageQueue = measurementAverageQueue;
        this.measurementAverageLoadQueue = measurementAverageLoadQueue;
        this.measurementAverages = measurementAverages;
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

        synchronized (measurementAverages) {
            measurements.stream().map(m -> Pair.of(m.getStationId(), m.getTimestamp().truncatedTo(ChronoUnit.HOURS))).forEach(m -> {
                val averages = measurementAverages.computeIfAbsent(m.getLeft(), i -> new ArrayList<>());
                val average = averages.stream()
                        .filter(averageMeasurement -> averageMeasurement.getDate().equals(m.getRight()))
                        .findFirst();

                if (average.isEmpty()) {
                    val a = loadedAverages.getOrDefault(m.getLeft(), new ArrayList<>())
                            .stream()
                            .filter(averageMeasurement -> m.getRight().isEqual(averageMeasurement.getDate()))
                            .findFirst()
                            .orElse(new AverageMeasurement(m.getLeft(), m.getRight()));
                    averages.add(a);
                }
            });
        }

        for (Measurement m: measurements) {
            measurementAverageQueue.offer(m);
        }
    }
}
