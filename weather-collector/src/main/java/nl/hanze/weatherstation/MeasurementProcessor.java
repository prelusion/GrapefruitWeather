package nl.hanze.weatherstation;

public interface MeasurementProcessor extends DataProcessor {
    /**
     * Process a measurement XML string.
     *
     * @param xmlString The measurement string.
     */
    void processData(String xmlString);
}
