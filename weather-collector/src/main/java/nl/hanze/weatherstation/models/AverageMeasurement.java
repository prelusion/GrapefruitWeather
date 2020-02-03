package nl.hanze.weatherstation.models;

import lombok.Data;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

@Data
public class AverageMeasurement {
    private LocalDateTime date;
    private int count;
    private double temperature;
    private double dewPoint;
    private double stationAirPressure;
    private double seaAirPressure;
    private double visibility;
    private double airSpeed;
    private double rainFall;
    private double snowFall;
    private double cloudPercentage;
    private int windDirection;

    private Integer collectionId;
    private int position;
    private boolean modified;

    public AverageMeasurement(LocalDateTime date) {
        this.date = date.truncatedTo(ChronoUnit.HOURS);
    }

    public void addMeasurement(Measurement measurement) {
        if (measurement.getTemperature() != null) {
            this.setTemperature(getAverage(this.getCount(), this.getTemperature(), measurement.getTemperature()));
        }
        if (measurement.getDewPoint() != null) {
            this.setDewPoint(getAverage(this.getCount(), this.getDewPoint(), measurement.getDewPoint()));
        }
        if (measurement.getStationAirPressure() != null) {
            this.setStationAirPressure(getAverage(this.getCount(), this.getStationAirPressure(), measurement.getStationAirPressure()));
        }
        if (measurement.getSeaAirPressure() != null) {
            this.setSeaAirPressure(getAverage(this.getCount(), this.getSeaAirPressure(), measurement.getSeaAirPressure()));
        }
        if (measurement.getVisibility() != null) {
            this.setVisibility(getAverage(this.getCount(), this.getVisibility(), measurement.getVisibility()));
        }
        if (measurement.getAirSpeed() != null) {
            this.setAirSpeed(getAverage(this.getCount(), this.getAirSpeed(), measurement.getAirSpeed()));
        }
        if (measurement.getRainFall() != null) {
            this.setRainFall(getAverage(this.getCount(), this.getRainFall(), measurement.getRainFall()));
        }
        if (measurement.getSnowFall() != null) {
            this.setSnowFall(getAverage(this.getCount(), this.getSnowFall(), measurement.getSnowFall()));
        }
        if (measurement.getCloudPercentage() != null) {
            this.setCloudPercentage(getAverage(this.getCount(), this.getCloudPercentage(), measurement.getCloudPercentage()));
        }
        if (measurement.getWindDirection() != null) {
            this.setWindDirection((int) getAverage(this.getCount(), this.getWindDirection(), measurement.getWindDirection()));
        }
        count++;
    }

    private double getAverage(int count, double oldValue, double newValue) {
        return ((oldValue * count) + newValue)/(count+1);
    }
}
