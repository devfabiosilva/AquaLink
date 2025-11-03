package org.controlpaneldriver.automation;

public class Registers {

    private Registers() {}
    public static class System {
        private System() {}
        public static final short MB_ERROR_REG_ADDRESS = 0x0200;
        public static final short MB_SYSTEM_TIMER = 0x0201;
        public static final short MB_SYSTEM_READY_TIMER = 0x0203;
        public static final short MB_SYSTEM_WATER_PUMP_TIMER = 0x0205;
    }

    public static class Inputs {
        private Inputs() {}
        public static class Analog {
            private Analog() {}
            public static final short MB_WATER_LEVEL_SENSOR = 0x0000;
        }

        public static class Discrete {
            private Discrete() {}
            public static final short MB_BUTTON_AUTOMATIC_MODE = 0x709C;//0x0002;
            public static final short MB_READY_MONITORE_STATUS = 0x07F4;//0x0601;//
            public static final short MB_READY_STATE_STATUS = 0x0606;
            public static final short MB_PUMP_REG = 0x07F5;//0x0603;
            public static final short MB_TEST_PANEL_INDICATOR_REG = 0x09E8;
        }

        public static final short TOTAL_KWH_REG = 0x0207;
        public static final short EXPORT_KWH_REG = 0x0209;
        public static final short IMPORT_KWH_REG = 0x020B;
        public static final short VOLTAGE_REG = TOTAL_KWH_REG + 6;
        public static final short CURRENT_REG = VOLTAGE_REG + 1;
        public static final short ACTIVE_POWER_REG = CURRENT_REG + 1;
        public static final short POWER_FACTOR_REG = ACTIVE_POWER_REG + 1;
        public static final short FREQUENCY_REG = POWER_FACTOR_REG + 1;
    }

    public static class Outputs {
        private Outputs() {}
        public static class Discrete {
            private Discrete() {}
            public static final short EMERGENCY_RESET_SYSTEM_REG =  0x0607;
            public static final short SET_SYSTEM_READY_REG = 0x060A;
            public static final short SET_PUMP_ON = 0x060B;
            public static final short MB_BUTTON_TOGGLE_AUTOMATIC_MODE = 0x060C;
        }
    }
}