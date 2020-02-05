package nl.hanze.weatherstation;

import lombok.val;
import nl.hanze.weatherstation.models.AverageMeasurement;
import nl.hanze.weatherstation.models.Measurement;

import java.nio.ByteBuffer;
import java.time.Instant;
import java.time.ZoneOffset;

public class MeasurementConverter {
    public static byte[] convertMeasurementToByteArray(Measurement measurement) {
        // Each measurement has a fixes size of 35 bytes.
        byte[] byteArray = new byte[35];

        // Bytes 0-3 are used for the station id.
        // The station id is saved as a 3 byte integer.
        val stationId = measurement.getStationId();
        writeIntToByteArray(byteArray, 0, 3, stationId);

        // Bytes 4-7 are used for the timestamp.
        // The timestamp is saved as a 4 byte integer.
        // TODO check timezone offset
        val epoch = measurement.getTimestamp().toEpochSecond(ZoneOffset.UTC);
        writeIntToByteArray(byteArray, 3, 4, Math.toIntExact(epoch));

        // Bytes 8-9 are used for null indication.
        // Each bit represents a measurement value.
        // When a bit is set to one that measurement is null.

        // Bytes 10-12 are used for the temperature.
        // The temperature is saved as a 3 byte integer.
        val temperature = measurement.getTemperature();
        if (temperature != null) {
            writeIntToByteArray(byteArray, 9, 3, (int)(temperature * 10));
        } else {
            byteArray[7] |= (1/* << 0*/);
        }

        // Bytes 13-15 are used for the dewpoint.
        // The dewpoint is saved as a 3 byte integer.
        val dewPoint = measurement.getDewPoint();
        if (dewPoint != null) {
            writeIntToByteArray(byteArray, 12, 3, (int)(dewPoint * 10));
        } else {
            byteArray[7] |= (1 << 1);
        }

        // Bytes 16-18 are used for the station air pressure.
        // The station air pressure is saved as a 3 byte integer.
        val stationAirPressure = measurement.getStationAirPressure();
        if (stationAirPressure != null) {
            writeIntToByteArray(byteArray, 15, 3, (int)(stationAirPressure * 10));
        } else {
            byteArray[7] |= (1 << 2);
        }

        // Bytes 19-21 are used for the sea air pressure.
        // The sea air pressure is saved as a 3 byte integer.
        val seaAirPressure = measurement.getSeaAirPressure();
        if (seaAirPressure != null) {
            writeIntToByteArray(byteArray, 18, 3, (int)(seaAirPressure * 10));
        } else {
            byteArray[7] |= (1 << 3);
        }

        // Bytes 22-23 are used for the visibility.
        // The visibility is saved as a 2 byte integer.
        val visibility = measurement.getVisibility();
        if (visibility != null) {
            writeIntToByteArray(byteArray, 21, 2, (int)(visibility * 10));
        } else {
            byteArray[7] |= (1 << 4);
        }

        // Bytes 24-25 are used for the airspeed.
        // The airspeed is saved as a 2 byte integer.
        val airspeed = measurement.getAirSpeed();
        if (airspeed != null) {
            writeIntToByteArray(byteArray, 23, 2, (int)(airspeed * 10));
        } else {
            byteArray[7] |= (1 << 5);
        }

        // Bytes 26-28 are used for the rainfall.
        // The rainfall is saved as a 3 byte integer.
        val rainfall = measurement.getRainFall();
        if (rainfall != null) {
            writeIntToByteArray(byteArray, 25, 3, (int)(rainfall * 100));
        } else {
            byteArray[7] |= (1 << 6);
        }

        // Bytes 29-30 are used for the snowfall.
        // The snowfall is saved as a 3 byte integer.
        val snowfall = measurement.getSnowFall();
        if (snowfall != null) {
            writeIntToByteArray(byteArray, 28, 3, (int)(snowfall * 10));
        } else {
            byteArray[7] |= (1 << 7);
        }

        val isFreezing = measurement.getIsFreezing();
        if (isFreezing != null) {
            byteArray[31] |= (1/* << 0*/);
        } else {
            byteArray[8] |= (1/* << 0*/);
        }

        val isRaining = measurement.getIsRaining();
        if (isRaining != null) {
            byteArray[31] |= (1 << 1);
        } else {
            byteArray[8] |= (1 << 1);
        }

        val isSnowing = measurement.getIsSnowing();
        if (isSnowing != null) {
            byteArray[31] |= (1 << 2);
        } else {
            byteArray[8] |= (1 << 2);
        }

        val isHail = measurement.getIsHail();
        if (isHail != null) {
            byteArray[31] |= (1 << 3);
        } else {
            byteArray[8] |= (1 << 3);
        }

        val isThunder = measurement.getIsThunder();
        if (isThunder != null) {
            byteArray[31] |= (1 << 4);
        } else {
            byteArray[8] |= (1 << 4);
        }

        val isStrongWind = measurement.getIsStrongWind();
        if (isStrongWind != null) {
            byteArray[31] |= (1 << 5);
        } else {
            byteArray[8] |= (1 << 5);
        }

        // Bytes 32-33 are used for the cloud percentage.
        // The cloud percentage is saved as a 2 byte integer.
        val cloudPercentage = measurement.getCloudPercentage();
        if (cloudPercentage != null) {
            writeIntToByteArray(byteArray, 31, 2, (int)(cloudPercentage * 10));
        } else {
            byteArray[8] |= (1 << 6);
        }

        // Bytes 34-35 are used for the cloud percentage.
        // The cloud percentage is saved as a 2 byte integer.
        val windDirection = measurement.getWindDirection();
        if (windDirection != null) {
            writeIntToByteArray(byteArray, 33, 2, windDirection);
        } else {
            byteArray[8] |= (1 << 7);
        }

        return byteArray;
    }

    public static byte[] convertAverageToByteArray(AverageMeasurement averageMeasurement) {
        // Each average has a fixes size of 35 bytes.
        byte[] byteArray = new byte[35];

        writeIntToByteArray(byteArray, 0, 3, averageMeasurement.getStationId());
        val epoch = averageMeasurement.getDate().toEpochSecond(ZoneOffset.UTC);
        writeIntToByteArray(byteArray, 3, 4, Math.toIntExact(epoch));
        writeIntToByteArray(byteArray, 7, 2, averageMeasurement.getCount());

        writeIntToByteArray(byteArray, 9, 3, (int)(averageMeasurement.getTemperature() * 10));
        writeIntToByteArray(byteArray, 12, 3, (int)(averageMeasurement.getDewPoint() * 10));
        writeIntToByteArray(byteArray, 15, 3, (int)(averageMeasurement.getStationAirPressure() * 10));
        writeIntToByteArray(byteArray, 18, 3, (int)(averageMeasurement.getSeaAirPressure() * 10));
        writeIntToByteArray(byteArray, 21, 2, (int)(averageMeasurement.getVisibility() * 10));
        writeIntToByteArray(byteArray, 23, 2, (int)(averageMeasurement.getAirSpeed() * 10));
        writeIntToByteArray(byteArray, 25, 3, (int)(averageMeasurement.getRainFall() * 100));
        writeIntToByteArray(byteArray, 28, 3, (int)(averageMeasurement.getSnowFall() * 10));
        writeIntToByteArray(byteArray, 31, 2, (int)(averageMeasurement.getCloudPercentage() * 10));
        writeIntToByteArray(byteArray, 33, 2, averageMeasurement.getWindDirection());

        return byteArray;
    }

    public static AverageMeasurement convertByteArrayToAverage(byte[] byteArray) {
        val stationId = getIntFromByteArray(byteArray, 0, 3);
        val epoch = getIntFromByteArray(byteArray, 3, 4);
        val averageMeasurement = new AverageMeasurement(stationId, Instant.ofEpochSecond(epoch).atZone(ZoneOffset.UTC).toLocalDateTime());

        averageMeasurement.setCount(getIntFromByteArray(byteArray, 7, 2));
        averageMeasurement.setTemperature(getIntFromByteArray(byteArray, 9, 3) / 10.0);
        averageMeasurement.setDewPoint(getIntFromByteArray(byteArray, 12, 3) / 10.0);
        averageMeasurement.setStationAirPressure(getIntFromByteArray(byteArray, 15, 3) / 10.0);
        averageMeasurement.setSeaAirPressure(getIntFromByteArray(byteArray, 18, 3) / 10.0);
        averageMeasurement.setVisibility(getIntFromByteArray(byteArray, 21, 2) / 10.0);
        averageMeasurement.setAirSpeed(getIntFromByteArray(byteArray, 23, 2) / 10.0);
        averageMeasurement.setRainFall(getIntFromByteArray(byteArray, 25, 3) / 100.0);
        averageMeasurement.setSnowFall(getIntFromByteArray(byteArray, 28, 3) / 10.0);
        averageMeasurement.setCloudPercentage(getIntFromByteArray(byteArray, 31, 2) / 10.0);
        averageMeasurement.setWindDirection(getIntFromByteArray(byteArray, 33, 2));

        return averageMeasurement;
    }

    public static int getIntFromByteArray(byte[] byteArray, int offset, int length) {
        byte[] buffer = new byte[4];
        System.arraycopy(byteArray, offset, buffer, 4 - length, length);

        if (length < 4) {
            for (int i = 0; i < 4 - length; i++) {
                buffer[i] = ((byteArray[offset] & 0b10000000) == 0b10000000) ? (byte)0xFF : (byte)0x00;
            }
        }

        return ByteBuffer.wrap(buffer).getInt();
    }

    public static void writeIntToByteArray(byte[] byteArray, int offset, int length, int number) {
        for (int i = 0; i < length; i++) {
            val shiftAmount = ((length - i - 1) * 8);
            byteArray[i + offset] = (byte) ((number & (0xFF << shiftAmount)) >> shiftAmount);
        }
    }
}
