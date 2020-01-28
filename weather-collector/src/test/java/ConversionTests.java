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
        AverageMeasurement averageMeasurement1 = new AverageMeasurement(LocalDateTime.now());
        averageMeasurement1.setCount(random.nextInt(100));
        averageMeasurement1.setTemperature(random.nextDouble() * 100 - 50);
        averageMeasurement1.setDewPoint(random.nextDouble() * 100 - 50);
        averageMeasurement1.setStationAirPressure(random.nextDouble() * 100 - 50);
        averageMeasurement1.setSeaAirPressure(random.nextDouble() * 100 - 50);
        averageMeasurement1.setVisibility(random.nextDouble() * 100 - 50);
        averageMeasurement1.setAirSpeed(random.nextDouble() * 100 - 50);
        averageMeasurement1.setRainFall(random.nextDouble() * 100 - 50);
        averageMeasurement1.setSnowFall(random.nextDouble() * 100 - 50);
        averageMeasurement1.setCloudPercentage(random.nextDouble() * 100 - 50);
        averageMeasurement1.setWindDirection(random.nextInt(300));
        byte[] bytes = MeasurementConverter.convertAverageToByteArray(stationId, averageMeasurement1);
        AverageMeasurement averageMeasurement2 = MeasurementConverter.convertByteArrayToAverage(bytes);
        Assert.assertTrue(averageMeasurement1.getDate().isEqual(averageMeasurement2.getDate()));
        Assert.assertEquals(averageMeasurement1.getCount(), averageMeasurement2.getCount());
        Assert.assertEquals(averageMeasurement1.getTemperature(), averageMeasurement2.getTemperature(), 0.1);
        Assert.assertEquals(averageMeasurement1.getDewPoint(), averageMeasurement2.getDewPoint(), 0.1);
        Assert.assertEquals(averageMeasurement1.getStationAirPressure(), averageMeasurement2.getStationAirPressure(), 0.1);
        Assert.assertEquals(averageMeasurement1.getSeaAirPressure(), averageMeasurement2.getSeaAirPressure(), 0.1);
        Assert.assertEquals(averageMeasurement1.getVisibility(), averageMeasurement2.getVisibility(), 0.1);
        Assert.assertEquals(averageMeasurement1.getAirSpeed(), averageMeasurement2.getAirSpeed(), 0.1);
        Assert.assertEquals(averageMeasurement1.getRainFall(), averageMeasurement2.getRainFall(), 0.1);
        Assert.assertEquals(averageMeasurement1.getSnowFall(), averageMeasurement2.getSnowFall(), 0.1);
        Assert.assertEquals(averageMeasurement1.getCloudPercentage(), averageMeasurement2.getCloudPercentage(), 0.1);
        Assert.assertEquals(averageMeasurement1.getWindDirection(), averageMeasurement2.getWindDirection());
    }
}
