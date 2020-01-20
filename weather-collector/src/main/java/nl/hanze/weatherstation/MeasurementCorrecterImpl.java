package nl.hanze.weatherstation;

import com.google.common.collect.EvictingQueue;
import lombok.val;
import nl.hanze.weatherstation.models.Measurement;

import java.util.HashMap;
import java.util.Objects;
import java.util.OptionalDouble;
import java.util.Queue;
import java.util.function.Consumer;
import java.util.function.Function;

public class MeasurementCorrecterImpl implements MeasurementCorrecter {
    private Queue<Measurement> measurementQueue;
    private Queue<Measurement> measurementSaveQueue;
    private HashMap<Integer, Queue<Measurement>> measurementHistory;

    public MeasurementCorrecterImpl(Queue<Measurement> measurementQueue, Queue<Measurement> measurementSaveQueue, HashMap<Integer, Queue<Measurement>> measurementHistory) {
        this.measurementQueue = measurementQueue;
        this.measurementSaveQueue = measurementSaveQueue;
        this.measurementHistory = measurementHistory;
    }

    private OptionalDouble calculateExpectedResult(int stationId, Function<Measurement, Double> measurementFunction) {
        Queue<Measurement> measurementQueue = measurementHistory.get(stationId);

        if (measurementQueue == null) {
            measurementHistory.put(stationId, EvictingQueue.create(30));
            return OptionalDouble.empty();
        }

        // TODO exponential moving average.
        return measurementQueue.stream().map(measurementFunction).filter(Objects::nonNull).mapToDouble(m -> m).average();
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

    private void processMeasurement() {
        Measurement measurement = measurementQueue.poll();

        if (measurement == null) {
            return;
        }

        val expectedTemperature = calculateExpectedResult(measurement.getStationId(), Measurement::getTemperature);

        if (expectedTemperature.isPresent()) {
            if (measurement.getTemperature() == null/*|| 20% difference*/) {
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

        measurementHistory.get(measurement.getStationId()).add(measurement);
        measurementSaveQueue.offer(measurement);
    }

    @Override
    public void run() {
        while (true) {
            if (Thread.currentThread().isInterrupted()) {
                return;
            }

            processMeasurement();
        }
    }
}
