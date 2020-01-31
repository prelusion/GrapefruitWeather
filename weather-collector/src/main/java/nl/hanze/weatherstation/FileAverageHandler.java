package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.AverageMeasurement;
import nl.hanze.weatherstation.models.Measurement;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
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
        val files = FileHelper.extractExtensionSequences("/measurements", "wsamc")
                .stream()
                .map(id -> new File("/measurements/" + id + ".wsamc"))
                .collect(Collectors.toList());

        val ids = stations.stream().map(integerLocalDateTimePair -> {
            byte[] id = new byte[7];
            MeasurementConverter.writeIntToByteArray(id, 0, 3, integerLocalDateTimePair.getLeft());
            MeasurementConverter.writeIntToByteArray(id, 3, 4, ((int) integerLocalDateTimePair.getRight().toEpochSecond(ZoneOffset.UTC)));

            return id;
        }).collect(Collectors.toList());

        HashMap<Integer, List<AverageMeasurement>> result = new HashMap<>();

        for (File file : files) {
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
                        val ding = result.computeIfAbsent(MeasurementConverter.getIntFromByteArray(idBuffer, 0, 3), integer -> new ArrayList<>());
                        ding.add(MeasurementConverter.convertByteArrayToAverage(fullBuffer));
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
        val files = FileHelper.extractExtensionSequences("/measurements", "wsamc")
                .stream()
                .map(id -> new File("/measurements/" + id + ".wsamc"))
                .collect(Collectors.toList());

        HashMap<Integer, List<AverageMeasurement>> result = new HashMap<>();

        for (File file : files) {
            try {
                byte[] buffer = new byte[35];

                val randomAccessFile = new RandomAccessFile(file, "r");
                val measurementCount = (int)(file.length() / 35);

                for (int i = measurementCount; i > 0; i--) {
                    // Read the station id and timestamp to the buffer.
                    randomAccessFile.seek((i - 1) * 35);
                    randomAccessFile.readFully(buffer);
                    result.computeIfAbsent(MeasurementConverter.getIntFromByteArray(buffer, 0, 3), k -> new ArrayList<>())
                            .add(MeasurementConverter.convertByteArrayToAverage(buffer));
                }
                randomAccessFile.close();
            } catch (IOException ignored) {
            }
        }

        return result;
    }

    public AverageMeasurement loadAverageFromFileSystem(int stationId, LocalDateTime date) {
        int timestamp = (int) date.truncatedTo(ChronoUnit.HOURS).toEpochSecond(ZoneOffset.UTC);

        byte[] idCompareBuffer = new byte[7];
        MeasurementConverter.writeIntToByteArray(idCompareBuffer, 0, 3, stationId);
        MeasurementConverter.writeIntToByteArray(idCompareBuffer, 3, 4, timestamp);

        val files = FileHelper.extractExtensionSequences("/measurements", "wsamc")
                .stream()
                .map(id -> new File("/measurements/" + id + ".wsamc"))
                .collect(Collectors.toList());

        for (File file : files) {
            try {
                byte[] idBuffer = new byte[7];

                val randomAccessFile = new RandomAccessFile(file, "r");
                val measurementCount = (int)(file.length() / 35);

                for (int i = measurementCount; i > 0; i--) {
                    // Read the station id and timestamp to the buffer.
                    randomAccessFile.seek((i - 1) * 35);
                    randomAccessFile.readFully(idBuffer);
                    if (Arrays.equals(idCompareBuffer, idBuffer)) {
                        byte[] fullBuffer = new byte[35];
                        randomAccessFile.seek((i - 1) * 35);
                        randomAccessFile.readFully(fullBuffer);

                        return MeasurementConverter.convertByteArrayToAverage(fullBuffer);
                    }
                }
                randomAccessFile.close();
            } catch (IOException exception) {
                logger.error("", exception);
            }
        }

        return null;
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
                logger.error("Exception in average file processor", exception);
            }
        }
    }

    public void process() {
        List<byte[]> values;
        synchronized (measurementAverages) {
            values = measurementAverages.keySet()
                    .stream()
                    .flatMap(stationId -> measurementAverages.get(stationId)
                            .stream()
                            .map(averageMeasurement -> MeasurementConverter.convertAverageToByteArray(stationId, averageMeasurement)))
                    .collect(Collectors.toList());
        }

        val files = FileHelper.extractExtensionSequences("/measurements", "wsamc")
                .stream()
                .map(id -> new File("/measurements/" + id + ".wsamc"))
                .collect(Collectors.toList());

        byte[] idCompareBuffer = new byte[7];

        for (File file : files) {
            try {
                val randomAccessFile = new RandomAccessFile(file, "rw");
                val measurementCount = (int) (file.length() / 35);

                for (int i = measurementCount; i > 0; i--) {
                    randomAccessFile.seek((i - 1) * 35);
                    randomAccessFile.readFully(idCompareBuffer);
                    val bytes = values.stream().filter(b -> idCompareBuffer[0] == b[0]
                            && idCompareBuffer[1] == b[1]
                            && idCompareBuffer[2] == b[2]
                            && idCompareBuffer[3] == b[3]
                            && idCompareBuffer[4] == b[4]
                            && idCompareBuffer[5] == b[5]
                            && idCompareBuffer[6] == b[6]).findFirst();

                    if (bytes.isPresent()) {
                        randomAccessFile.seek((i - 1) * 35);
                        randomAccessFile.write(bytes.get());
                        values.remove(bytes.get());
                    }
                }

                randomAccessFile.close();
            } catch (IOException exception) {
                logger.error("", exception);
            }
        }

        val file = new File(String.format("/measurements/%s.wsamc", collectionId));

        try {
            file.createNewFile();

            try (val outputStream = new FileOutputStream(file, true)) {
                for (byte[] value : values) {
                    outputStream.write(value);
                }
            }
        } catch (IOException exception) {
            logger.error("", exception);
        }

        if (file.length() > (1024 * 1024 * 30)) {
            collectionId++;
        }
    }
}
