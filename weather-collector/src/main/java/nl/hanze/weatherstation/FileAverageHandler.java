package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.AverageMeasurement;
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
            }catch (Exception e) {
                logger.error("Saving averages failed", e);
            }
        }
    }

    public void process() {
        synchronized (measurementAverages) {
            val values = measurementAverages.keySet()
                    .stream()
                    .flatMap(stationId -> measurementAverages.get(stationId)
                            .stream()
                            .map(averageMeasurement -> MeasurementConverter.convertAverageToByteArray(stationId, averageMeasurement)))
                    .collect(Collectors.toList());

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
}
