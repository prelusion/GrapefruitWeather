package nl.hanze.weatherstation;

import nl.hanze.weatherstation.models.Measurement;

public interface MeasurementCorrecter {
    /**
     * Calculate missing values and correct invalid values of a measurement.
     *
     * @param measurement The measurement to correct.
     * @return The correced measurement.
     */
    Measurement correctMeasurement(Measurement measurement);
}
