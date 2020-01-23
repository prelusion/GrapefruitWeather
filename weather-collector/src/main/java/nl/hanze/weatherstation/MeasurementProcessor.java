package nl.hanze.weatherstation;

import lombok.val;
import lombok.var;
import nl.hanze.weatherstation.models.Measurement;
import org.slf4j.Logger;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;

public class MeasurementProcessor implements Runnable {
    private final Logger logger;
    private final Queue<String> rawDataQueue;
    private final Queue<Measurement> measurementQueue;

    public MeasurementProcessor(Logger logger, Queue<String> rawDataQueue, Queue<Measurement> measurementQueue) {
        this.logger = logger;
        this.rawDataQueue = rawDataQueue;
        this.measurementQueue = measurementQueue;
    }

    private List<Measurement> convertData() {
        List<Measurement> measurements = new ArrayList<>();
        val xmlString = rawDataQueue.poll();

        if (xmlString == null) {
            return measurements;
        }

        var currentIndex = 0;

        while (true) {
            // Find the index of the next measurement.
            currentIndex = xmlString.indexOf("<MEASUREMENT>", currentIndex);

            if (currentIndex == -1) {
                // No more measurements!
                break;
            }

            // Skip the first tag so it won't be picket up next round.
            currentIndex += 12;

            String stationId = getTagText(xmlString, "STN", currentIndex);
            String date = getTagText(xmlString, "DATE", currentIndex);
            String time = getTagText(xmlString, "TIME", currentIndex);
            String temperature = getTagText(xmlString, "TEMP", currentIndex);
            String dewPoint = getTagText(xmlString, "DEWP", currentIndex);
            String stationPressure = getTagText(xmlString, "STP", currentIndex);
            String seaPressure = getTagText(xmlString, "SLP", currentIndex);
            String visibility = getTagText(xmlString, "VISIB", currentIndex);
            String airSpeed = getTagText(xmlString, "WDSP", currentIndex);
            String rainFall = getTagText(xmlString, "PRCP", currentIndex);
            String snowFall = getTagText(xmlString, "SNDP", currentIndex);
            String events = getTagText(xmlString, "FRSHTT", currentIndex);
            String cloudPercentage = getTagText(xmlString, "CLDC", currentIndex);
            String windDirection = getTagText(xmlString, "WNDDIR", currentIndex);

            Measurement measurement = new Measurement();

            measurement.setStationId(Integer.parseInt(stationId));
            measurement.setTimestamp(LocalDateTime.parse(date + "T" + time));
            measurement.setTemperature(temperature.isEmpty() ? null : Double.parseDouble(temperature));
            measurement.setDewPoint(dewPoint.isEmpty() ? null : Double.parseDouble(temperature));
            measurement.setStationAirPressure(stationPressure.isEmpty() ? null : Double.parseDouble(stationPressure));
            measurement.setSeaAirPressure(seaPressure.isEmpty() ? null : Double.parseDouble(seaPressure));
            measurement.setVisibility(visibility.isEmpty() ? null : Double.parseDouble(visibility));
            measurement.setAirSpeed(airSpeed.isEmpty() ? null : Double.parseDouble(airSpeed));
            measurement.setRainFall(rainFall.isEmpty() ? null : Double.parseDouble(rainFall));
            measurement.setSnowFall(snowFall.isEmpty() ? null : Double.parseDouble(snowFall));
            measurement.setCloudPercentage(cloudPercentage.isEmpty() ? null : Double.parseDouble(cloudPercentage));
            measurement.setWindDirection(windDirection.isEmpty() ? null : Integer.parseInt(windDirection));

            if (!events.isEmpty()) {
                measurement.setIsFreezing(Boolean.parseBoolean(String.valueOf(events.charAt(0))));
                measurement.setIsRaining(Boolean.parseBoolean(String.valueOf(events.charAt(1))));
                measurement.setIsSnowing(Boolean.parseBoolean(String.valueOf(events.charAt(2))));
                measurement.setIsHail(Boolean.parseBoolean(String.valueOf(events.charAt(3))));
                measurement.setIsThunder(Boolean.parseBoolean(String.valueOf(events.charAt(4))));
                measurement.setIsStrongWind(Boolean.parseBoolean(String.valueOf(events.charAt(5))));
            }

            measurements.add(measurement);
        }

        return measurements;
    }

    private String getTagText(String xml, String tag, int fromIndex) {
        fromIndex = xml.indexOf("<" + tag + ">", fromIndex) + tag.length() + 2;
        return xml.substring(fromIndex, xml.indexOf('<', fromIndex));
    }

    public void processData() {
        for (Measurement measurement : convertData()) {
            measurementQueue.offer(measurement);
        }
    }

    @Override
    public void run() {
        while (true) {
            if (Thread.currentThread().isInterrupted()) {
                logger.info(String.format("%s interrupted", this.getClass().toString()));
                return;
            }

            processData();
        }
    }
}
