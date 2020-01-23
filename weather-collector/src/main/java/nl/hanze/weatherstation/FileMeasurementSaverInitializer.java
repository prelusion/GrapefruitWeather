package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.Measurement;
import org.slf4j.Logger;

import java.io.File;
import java.util.Arrays;
import java.util.Objects;
import java.util.Queue;
import java.util.regex.Pattern;

public class FileMeasurementSaverInitializer {
    public FileMeasurementSaver initialize(
            Logger logger,
            Queue<Measurement> measurementSaveQueue,
            MeasurementConverter measurementConverter
    ) {
        return new FileMeasurementSaver(logger, measurementSaveQueue, measurementConverter, null, null, getCurrentIndex());
    }

    private int getCurrentIndex() {
        val files = new File("/measurements").listFiles();

        if (files == null) {
            return 0;
        }

        val pattern = Pattern.compile("^[0-9]+\\.wsmc$");

        return Arrays.stream(files).map(f -> {
            val matcher = pattern.matcher(f.getName());

            return matcher.find() ? matcher.group(0) : null;
        }).filter(Objects::nonNull)
                .mapToInt(Integer::parseInt)
                .max()
                .orElse(0);
    }
}
