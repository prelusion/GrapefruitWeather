package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.AverageMeasurement;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.*;
import java.util.stream.Collectors;

public class FileAverageHandler implements Runnable {
    private final Logger logger;
    private final HashMap<Integer, List<AverageMeasurement>> measurementAverages;
    private int collectionId;

    public FileAverageHandler(HashMap<Integer, List<AverageMeasurement>> measurementAverages) {
        this.logger = LoggerFactory.getLogger(this.getClass());
        this.measurementAverages = measurementAverages;

        val files = FileHelper.extractExtensionSequences("/measurements", "wsamc");
        this.collectionId = files.size() == 0 ? 0 : files.get(0);
    }

    public static HashMap<Integer, List<AverageMeasurement>> loadAveragesFromFileSystem(List<Pair<Integer, LocalDateTime>> stations) {
        val collections = FileHelper.extractExtensionSequences("/measurements", "wsamc");

        val ids = stations.stream().map(integerLocalDateTimePair -> {
            byte[] id = new byte[7];
            MeasurementConverter.writeIntToByteArray(id, 0, 3, integerLocalDateTimePair.getLeft());
            MeasurementConverter.writeIntToByteArray(id, 3, 4, ((int) integerLocalDateTimePair.getRight().toEpochSecond(ZoneOffset.UTC)));

            return id;
        }).collect(Collectors.toList());

        HashMap<Integer, List<AverageMeasurement>> result = new HashMap<>();

        for (int id : collections) {
            val file = new File("/measurements/" + id + ".wsamc");

            try {
                byte[] idBuffer = new byte[7];

                val randomAccessFile = new RandomAccessFile(file, "r");
                val measurementCount = (int)(file.length() / 35);

                for (int i = measurementCount; i > 0; i--) {
                    // Read the station id and timestamp to the buffer.
                    randomAccessFile.seek((i - 1) * 35);
                    randomAccessFile.readFully(idBuffer);
                    if (ids.contains(idBuffer)) {
                        byte[] fullBuffer = new byte[35];
                        randomAccessFile.seek((i - 1) * 35);
                        randomAccessFile.readFully(fullBuffer);
                        val averages = result.computeIfAbsent(MeasurementConverter.getIntFromByteArray(idBuffer, 0, 3), integer -> new ArrayList<>());
                        val average = MeasurementConverter.convertByteArrayToAverage(fullBuffer);
                        average.setCollectionId(id);
                        average.setPosition(i - 1);
                        averages.add(average);
                        ids.remove(idBuffer);
                    }
                }
                randomAccessFile.close();
            } catch (IOException ignored) {
            }
        }

        return result;
    }

    public static HashMap<Integer, List<AverageMeasurement>> loadAveragesFromFileSystem() {
        val collections = FileHelper.extractExtensionSequences("/measurements", "wsamc");

        HashMap<Integer, List<AverageMeasurement>> result = new HashMap<>();

        for (int id : collections) {
            val file = new File("/measurements/" + id + ".wsamc");
            try {
                byte[] buffer = new byte[35];

                val randomAccessFile = new RandomAccessFile(file, "r");
                val measurementCount = (int)(file.length() / 35);

                for (int i = measurementCount; i > 0; i--) {
                    // Read the station id and timestamp to the buffer.
                    randomAccessFile.seek((i - 1) * 35);
                    randomAccessFile.readFully(buffer);
                    val averages = result.computeIfAbsent(MeasurementConverter.getIntFromByteArray(buffer, 0, 3), k -> new ArrayList<>());

                    if (averages.size() < 2) {
                        val average = MeasurementConverter.convertByteArrayToAverage(buffer);
                        average.setCollectionId(id);
                        average.setPosition(i - 1);
                        averages.add(average);
                    }
                }
                randomAccessFile.close();
            } catch (IOException ignored) {
            }
        }

        return result;
    }

    @Override
    public void run() {
        try {
            process();
        } catch (Exception exception) {
            logger.error("Exception in average file processor", exception);
        }
    }

    public void process() {
        Map<Optional<Integer>, List<AverageMeasurement>> values;
        synchronized (measurementAverages) {
            values = measurementAverages.keySet()
                    .stream()
                    .flatMap(stationId -> measurementAverages.get(stationId).stream().filter(AverageMeasurement::isModified))
                            .collect(Collectors.groupingBy(averageMeasurement -> Optional.ofNullable(averageMeasurement.getCollectionId())));
        }

        values.forEach((collectionId, measurements) -> {
            if (collectionId.isEmpty()) {
                return;
            }
            val file = new File("/measurements/" + collectionId.get() + ".wsamc");
            try {
                val randomAccessFile = new RandomAccessFile(file, "rw");
                measurements.forEach(averageMeasurement -> {
                    try {
                        randomAccessFile.seek(averageMeasurement.getPosition() * 35);
                        randomAccessFile.write(MeasurementConverter.convertAverageToByteArray(averageMeasurement));
                        averageMeasurement.setModified(false);
                    } catch (IOException ignored) {
                        logger.error("", ignored);
                    }
                });
                randomAccessFile.close();
            } catch (IOException ignored) {
                logger.error("", ignored);
            }
        });
        if (!values.containsKey(Optional.empty())) {
            return;
        }

        val file = new File(String.format("/measurements/%s.wsamc", collectionId));

        try {
            file.createNewFile();
            val randomAccessFile = new RandomAccessFile(file, "rw");

                for (AverageMeasurement averageMeasurement : values.get(Optional.empty())) {
                    val bytes = MeasurementConverter.convertAverageToByteArray(averageMeasurement);
                    try {
                        averageMeasurement.setCollectionId(collectionId);
                        averageMeasurement.setPosition((int) (randomAccessFile.length() / 35));
                        randomAccessFile.seek(randomAccessFile.length());
                        randomAccessFile.write(bytes);
                    } catch (IOException e) {
                        logger.error("", e);
                    }
                }

            randomAccessFile.close();
        } catch (IOException exception) {
            logger.error("", exception);
        }

        if (file.length() > (1024 * 1024 * 60)) {
            collectionId++;
        }
    }
}
