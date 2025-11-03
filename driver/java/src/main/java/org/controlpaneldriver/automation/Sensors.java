package org.controlpaneldriver.automation;

public class Sensors {
    private Sensors() {}
    public static class ReservoirLevel {
        private ReservoirLevel() {}
        public static final short PRESSURE_SENSOR_FAIL_LOW = 6000;
        public static final short PRESSURE_SENSOR_FAIL_HIGH = 30000;
        public static final short PRESSURE_SENSOR_RESERVOIR_FULL_UPPER_LIMIT = 29000;
        public static final short PRESSURE_SENSOR_RESERVOIR_FULL_LOWER_LIMIT = 24600;
        public static final short PRESSURE_SENSOR_RESERVOIR_EMPTY = 7000;
        public static final short PRESSURE_SENSOR_RESERVOIR_RANGE = PRESSURE_SENSOR_RESERVOIR_FULL_UPPER_LIMIT - PRESSURE_SENSOR_RESERVOIR_EMPTY;
        public static final double K_CONST = 5.0/32000;
        public static final int ADC_SENSOR_MAX = 5000;
        public static final int ADC_SENSOR_STEP = 32000;
    }
}
