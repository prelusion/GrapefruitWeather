package nl.hanze.weatherstation.models;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class Measurement {
    private int stationId;
    private LocalDateTime timestamp;
    private Double temperature;
    private Double dewPoint;
    private Double stationAirPressure;
    private Double seaAirPressure;
    private Double visibility;
    private Double airSpeed;
    private Double rainFall;
    private Double snowFall;
    private Boolean isFreezing;
    private Boolean isRaining;
    private Boolean isSnowing;
    private Boolean isHail;
    private Boolean isThunder;
    private Boolean isStrongWind;
    private Double cloudPercentage;
    private Integer windDirection;
}
