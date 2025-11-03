
class Registers:
        class System:
                MB_ERROR_REG_ADDRESS = 0x0200
                MB_ERROR_REG_ADDRESS = 0x0200
                MB_SYSTEM_TIMER = 0x0201
                MB_SYSTEM_READY_TIMER = 0x0203
                MB_SYSTEM_WATER_PUMP_TIMER = 0x0205

        class Inputs:
                class Analog:
                        MB_WATER_LEVEL_SENSOR = 0x0000

                class Discrete:
                        MB_BUTTON_AUTOMATIC_MODE = 0x709C #0x0002
                        MB_READY_MONITORE_STATUS = 0x07F4 #0x0601
                        MB_READY_STATE_STATUS = 0x0606
                        MB_PUMP_REG = 0x07F5 #0x0603
                        MB_TEST_PANEL_INDICATOR_REG = 0x09E8

                TOTAL_KWH_REG = 0x0207
                EXPORT_KWH_REG = 0x0209
                IMPORT_KWH_REG = 0x020B
                VOLTAGE_REG = TOTAL_KWH_REG + 6
                CURRENT_REG = VOLTAGE_REG + 1
                ACTIVE_POWER_REG = CURRENT_REG + 1
                POWER_FACTOR_REG = ACTIVE_POWER_REG + 1
                FREQUENCY_REG = POWER_FACTOR_REG + 1

        class Outputs:
                class Discrete:
                        EMERGENCY_RESET_SYSTEM_REG =  0x0607
                        SET_SYSTEM_READY_REG = 0x060A
                        SET_PUMP_ON = 0x060B
                        MB_BUTTON_TOGGLE_AUTOMATIC_MODE = 0x060C
