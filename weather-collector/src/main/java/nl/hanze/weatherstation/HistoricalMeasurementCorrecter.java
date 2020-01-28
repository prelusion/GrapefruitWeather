package nl.hanze.weatherstation;

import com.google.common.collect.EvictingQueue;
import lombok.val;
import nl.hanze.weatherstation.models.Measurement;

import java.util.*;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;

public class HistoricalMeasurementCorrecter implements MeasurementCorrecter {
    private final HashMap<Integer, Queue<Measurement>> measurementHistory;

    public HistoricalMeasurementCorrecter(HashMap<Integer, Queue<Measurement>> measurementHistory) {
        this.measurementHistory = measurementHistory;
    }

    private OptionalDouble calculateExpectedResult(int stationId, Function<Measurement, Double> measurementFunction) {
        Queue<Measurement> measurementQueue = measurementHistory.get(stationId);

        if (measurementQueue == null) {
            measurementHistory.put(stationId, EvictingQueue.create(30));
            return OptionalDouble.empty();
        }

        val values = measurementQueue.stream().map(measurementFunction).filter(Objects::nonNull).collect(Collectors.toList());

        if (values.size() == 0) {
            return OptionalDouble.empty();
        }

        double currentAverage = values.get(0);
        for (Double value : values) {
            currentAverage = currentAverage + 0.5 * (value - currentAverage);
        }

        return OptionalDouble.of(currentAverage);
    }

    /**
     * Method that can correct invalid measurements based on a getter and setter.
     * The correction will be calculated from all previous readings.
     *
     * @param measurement Measurement to check and correct.
     * @param measurementFunction Function to get the property that should be checked en corrected.
     * @param setter Setter to set the corrected value.
     * @param <T> Measurement type
     */
    private <T> void correctMeasurementProperty(Measurement measurement, Function<Measurement, Double> measurementFunction, Consumer<Double> setter) {
        if (measurementFunction.apply(measurement) == null) {
            val expectedValue = calculateExpectedResult(measurement.getStationId(), measurementFunction);

            if (expectedValue.isPresent()) {
                setter.accept(expectedValue.getAsDouble());
            }
        }
    }

    public Measurement correctMeasurement(Measurement measurement) {
        val expectedTemperature = calculateExpectedResult(measurement.getStationId(), Measurement::getTemperature);

        if (expectedTemperature.isPresent()) {
            if (measurement.getTemperature() == null || ((expectedTemperature.getAsDouble() - measurement.getTemperature()) / expectedTemperature.getAsDouble() * 100) > 20) {
                measurement.setTemperature(expectedTemperature.getAsDouble());
            }
        }

        correctMeasurementProperty(measurement, Measurement::getDewPoint, measurement::setDewPoint);
        correctMeasurementProperty(measurement, Measurement::getStationAirPressure, measurement::setStationAirPressure);
        correctMeasurementProperty(measurement, Measurement::getSeaAirPressure, measurement::setSeaAirPressure);
        correctMeasurementProperty(measurement, Measurement::getVisibility, measurement::setVisibility);
        correctMeasurementProperty(measurement, Measurement::getAirSpeed, measurement::setAirSpeed);
        correctMeasurementProperty(measurement, Measurement::getRainFall, measurement::setRainFall);
        correctMeasurementProperty(measurement, Measurement::getSnowFall, measurement::setSnowFall);
        correctMeasurementProperty(measurement, Measurement::getCloudPercentage, measurement::setCloudPercentage);
        correctMeasurementProperty(measurement, m -> {
            val windDirection = m.getWindDirection();
            return (windDirection == null) ? null : windDirection.doubleValue();
        }, v -> measurement.setWindDirection(v.intValue()));

        return measurement;
    }
}
