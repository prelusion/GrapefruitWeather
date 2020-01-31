import nl.hanze.weatherstation.MeasurementConverter;
import nl.hanze.weatherstation.models.AverageMeasurement;
import org.junit.Assert;
import org.junit.Test;

import java.time.LocalDateTime;
import java.util.Random;

public class ConversionTests {
    @Test
    public void intToBinaryAndBack() {
        byte[] bytes = new byte[6];

        // Test different numbers.
        for (int i = -8388608; i < 8388608; i++) {
            // Test different offsets.
            for (int j = 0; j < 2; j++) {
                MeasurementConverter.writeIntToByteArray(bytes, j, 3, i);
                Assert.assertEquals(i, MeasurementConverter.getIntFromByteArray(bytes, j, 3));
            }
        }
    }

    @Test
    public void averageToBinaryAndBack() {
        Random random = new Random();
        int stationId = random.nextInt(8000);
        AverageMeasurement averageMeasurement = new AverageMeasurement(LocalDateTime.now());
        averageMeasurement.setCount(random.nextInt(100));
        averageMeasurement.setTemperature(random.nextDouble() * 100 - 50);
        averageMeasurement.setDewPoint(random.nextDouble() * 100 - 50);
        averageMeasurement.setStationAirPressure(random.nextDouble() * 100 - 50);
        averageMeasurement.setSeaAirPressure(random.nextDouble() * 100 - 50);
        averageMeasurement.setVisibility(random.nextDouble() * 100 - 50);
        averageMeasurement.setAirSpeed(random.nextDouble() * 100 - 50);
        averageMeasurement.setRainFall(random.nextDouble() * 100 - 50);
        averageMeasurement.setSnowFall(random.nextDouble() * 100 - 50);
        averageMeasurement.setCloudPercentage(random.nextDouble() * 100 - 50);
        averageMeasurement.setWindDirection(random.nextInt(300));
        byte[] bytes = MeasurementConverter.convertAverageToByteArray(stationId, averageMeasurement);
        AverageMeasurement averageMeasurement2 = MeasurementConverter.convertByteArrayToAverage(bytes);
        Assert.assertTrue(averageMeasurement.getDate().isEqual(averageMeasurement2.getDate()));
        Assert.assertEquals(averageMeasurement.getCount(), averageMeasurement2.getCount());
        Assert.assertEquals(averageMeasurement.getTemperature(), averageMeasurement2.getTemperature(), 0.1);
        Assert.assertEquals(averageMeasurement.getDewPoint(), averageMeasurement2.getDewPoint(), 0.1);
        Assert.assertEquals(averageMeasurement.getStationAirPressure(), averageMeasurement2.getStationAirPressure(), 0.1);
        Assert.assertEquals(averageMeasurement.getSeaAirPressure(), averageMeasurement2.getSeaAirPressure(), 0.1);
        Assert.assertEquals(averageMeasurement.getVisibility(), averageMeasurement2.getVisibility(), 0.1);
        Assert.assertEquals(averageMeasurement.getAirSpeed(), averageMeasurement2.getAirSpeed(), 0.1);
        Assert.assertEquals(averageMeasurement.getRainFall(), averageMeasurement2.getRainFall(), 0.1);
        Assert.assertEquals(averageMeasurement.getSnowFall(), averageMeasurement2.getSnowFall(), 0.1);
        Assert.assertEquals(averageMeasurement.getCloudPercentage(), averageMeasurement2.getCloudPercentage(), 0.1);
        Assert.assertEquals(averageMeasurement.getWindDirection(), averageMeasurement2.getWindDirection());
    }
}
