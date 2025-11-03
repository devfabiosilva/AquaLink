
from lib.automation.registers import Registers
from lib.automation.sensors import Sensors
from lib.exception.automationcontrolerror import AutomationControlError
from lib.util.operators import *
import panel

class Ac12m0p:
    def __init__(self, panel: panel):
        self.panel = panel

    KEY_RESERVOIR_LEVEL = "reservoirLevel"
    KEY_RESERVOIR_LEVEL_FAULT = "reservoirLevelFault"
    KEY_RESERVOIR_SENSOR_VOLTAGE = "reservoirSensorVoltage"
    KEY_ERROR_STATUS = "errorStatus"
    KEY_PLC_SYSTEM_TIMESTAMP = "plcSystemTimestamp"
    KEY_READY_TIMER = "readyTimer"
    KEY_WATER_PUMP_TIMER = "waterPumpTimer"
    KEY_PLC_STATUS = "plcStatus"

    FLAG_SYSTEM_STATUS = 1
    FLAG_SYSTEM_READY = FLAG_SYSTEM_STATUS << 1
    FLAG_PUMP_STATUS = FLAG_SYSTEM_READY << 1
    FLAG_AUTOMATIC_MODE = FLAG_PUMP_STATUS << 1
    FLAG_SYSTEM_TESTING_INDICATOR_PANEL = FLAG_AUTOMATIC_MODE << 1

    reservoirLevel = 0
    errorStatus = 0
    plcTimestamp = 0
    readyTimerSnapshot = 0
    waterPumpTimerSnapshot = 0
    plcSystemStatus = False
    plcSystemReady = False
    waterPumpStatus = False
    automaticMode = False
    panelIndicatorTester = False

    eventChanged = True

    reservoirLevelUpdated = True
    errorStatusUpdated = True
    readyTimerSnapshotUpdated = True
    waterPumpTimerSnapshotUpdated = True
    plcSystemStatusUpdated = True
    plcSystemReadyUpdated = True
    waterPumpStatusUpdated = True
    automaticModeUpdated = True
    panelIndicatorTesterUpdated = True

    sensorResult = {}
    sensorResultStr = {}

    def plcCleanUp(self):
        self.reservoirLevel = 0
        self.errorStatus = 0
        self.plcTimestamp = 0
        self.readyTimerSnapshot = 0
        self.waterPumpTimerSnapshot = 0
        self.plcSystemStatus = False
        self.plcSystemReady = False
        self.waterPumpStatus = False
        self.automaticMode = False
        self.panelIndicatorTester = False

        self.eventChanged = True

        self.reservoirLevelUpdated = True
        self.errorStatusUpdated = True
        self.readyTimerSnapshotUpdated = True
        self.waterPumpTimerSnapshotUpdated = True
        self.plcSystemStatusUpdated = True
        self.plcSystemReadyUpdated = True
        self.waterPumpStatusUpdated = True
        self.automaticModeUpdated = True
        self.panelIndicatorTesterUpdated = True

        self.sensorResult.clear()
        self.sensorResultStr.clear()

    def readSensors(self, forceUpdate = False):
        try:
            shortValue = self.panel.modbus.readShort(Registers.Inputs.Analog.MB_WATER_LEVEL_SENSOR)
        except:
            self.plcCleanUp()
            raise

        self.reservoirLevelUpdated = (shortValue != self.reservoirLevel)
        self.eventChanged = self.reservoirLevelUpdated
        self.reservoirLevel = shortValue

        try:
            shortValue = self.panel.modbus.readShort(Registers.System.MB_ERROR_REG_ADDRESS)
        except:
            self.plcCleanUp()
            raise

        self.errorStatusUpdated = (shortValue != self.errorStatus)
        self.eventChanged |= self.errorStatusUpdated
        self.errorStatus = shortValue

        try:
            self.plcTimestamp = optUtil(self.panel.modbus.readInt(Registers.System.MB_SYSTEM_TIMER))
        except:
            self.plcCleanUp()
            raise

        try:
            longValue = optUtil(self.panel.modbus.readInt(Registers.System.MB_SYSTEM_READY_TIMER))
        except:
            self.plcCleanUp()
            raise

        self.readyTimerSnapshotUpdated = (longValue > -1)
        self.eventChanged |= self.readyTimerSnapshotUpdated
        self.readyTimerSnapshot = longValue

        try:
            longValue = optUtil(self.panel.modbus.readInt(Registers.System.MB_SYSTEM_WATER_PUMP_TIMER))
        except:
            self.plcCleanUp()
            raise

        self.waterPumpTimerSnapshotUpdated = (longValue > -1)
        self.eventChanged |= self.waterPumpTimerSnapshotUpdated
        self.waterPumpTimerSnapshot = longValue

        booleanValue = (self.errorStatus == AutomationControlError.MB_ERROR_SUCCESS)
        self.eventChanged |= (booleanValue != self.plcSystemStatus)
        self.plcSystemStatus = booleanValue

        try:
            booleanValue = self.panel.modbus.readCoil(Registers.Inputs.Discrete.MB_READY_MONITORE_STATUS)
        except:
            self.plcCleanUp()
            raise
        
        self.plcSystemReadyUpdated = (booleanValue != self.plcSystemReady)
        self.eventChanged |= self.plcSystemReadyUpdated
        self.plcSystemReady = booleanValue

        try:
            booleanValue = self.panel.modbus.readCoil(Registers.Inputs.Discrete.MB_PUMP_REG)
        except:
            self.plcCleanUp()
            raise

        self.waterPumpStatusUpdated = (booleanValue != self.waterPumpStatus)
        self.eventChanged |= self.waterPumpStatusUpdated
        self.waterPumpStatus = booleanValue

        try:
            booleanValue = self.panel.modbus.readCoil(Registers.Inputs.Discrete.MB_TEST_PANEL_INDICATOR_REG)
        except:
            self.plcCleanUp()
            raise

        self.panelIndicatorTesterUpdated = (booleanValue != self.panelIndicatorTester)
        self.eventChanged |= self.panelIndicatorTesterUpdated
        self.panelIndicatorTester = booleanValue

        try:
            booleanValue = self.panel.modbus.readCoil(Registers.Inputs.Discrete.MB_BUTTON_AUTOMATIC_MODE)
        except:
            self.plcCleanUp()
            raise

        self.automaticModeUpdated = (booleanValue != self.automaticMode)
        self.eventChanged |= self.automaticModeUpdated
        self.automaticMode = booleanValue

        self.eventChanged |= forceUpdate

    def getReservoirLevelHelper(self):
        sensorValue = self.reservoirLevel
        if (sensorValue > Sensors.ReservoirLevel.PRESSURE_SENSOR_FAIL_HIGH or self.errorStatus == AutomationControlError.MB_ERROR_CODE_RESERVOIR_OVERFLOW):
            raise AutomationControlError("CRITICAL: Water level overflow or pressure sensor malfunction")

        if (sensorValue < Sensors.ReservoirLevel.PRESSURE_SENSOR_FAIL_LOW or self.errorStatus == AutomationControlError.MB_ERROR_CODE_RESERVOIR_SENSOR_ERR):
            raise AutomationControlError("CRITICAL: Water level below expected. Check pressure sensor or communication cable")

        if (sensorValue > Sensors.ReservoirLevel.PRESSURE_SENSOR_RESERVOIR_FULL_UPPER_LIMIT):
            sensorValue = Sensors.ReservoirLevel.PRESSURE_SENSOR_RESERVOIR_FULL_UPPER_LIMIT
        elif (sensorValue < Sensors.ReservoirLevel.PRESSURE_SENSOR_RESERVOIR_EMPTY):
            sensorValue = Sensors.ReservoirLevel.PRESSURE_SENSOR_RESERVOIR_EMPTY

        return (int)((1000*(sensorValue - Sensors.ReservoirLevel.PRESSURE_SENSOR_RESERVOIR_EMPTY)) / (Sensors.ReservoirLevel.PRESSURE_SENSOR_RESERVOIR_RANGE))

    def getReservoirLevel(self):
        return self.getReservoirLevelHelper() / 10.0

    def getReservoirLevelStr(self):
        return fixedPoint(self.getReservoirLevelHelper(), 2, 1)

    def getSensorVoltage(self):
        return self.reservoirLevel * Sensors.ReservoirLevel.K_CONST

    def getSensorVoltageStr(self):
        return fixedPoint((int)((self.reservoirLevel * Sensors.ReservoirLevel.ADC_SENSOR_MAX) / Sensors.ReservoirLevel.ADC_SENSOR_STEP), 4, 3)

    def getPlcTimestamp(self):
        return self.plcTimestamp

    def getReadyTimer(self):
        if (self.readyTimerSnapshot >= 0):
            return self.plcTimestamp - self.readyTimerSnapshot

        return 0

    def getWaterPumpTimer(self):
        if (self.waterPumpTimerSnapshot >= 0):
            return self.plcTimestamp - self.waterPumpTimerSnapshot

        return 0

    def getPlcStatus(self):
        shortValue = 0

        if (self.plcSystemStatus):
            shortValue = self.FLAG_SYSTEM_STATUS

        if (self.plcSystemReady):
            shortValue |= self.FLAG_SYSTEM_READY

        if (self.waterPumpStatus):
            shortValue |= self.FLAG_PUMP_STATUS

        if (self.automaticMode):
            shortValue |= self.FLAG_AUTOMATIC_MODE

        if (self.panelIndicatorTester):
            shortValue |= self.FLAG_SYSTEM_TESTING_INDICATOR_PANEL

        return shortValue

    def updateHelper(self, destination, key, value, shouldAdd):
        if (shouldAdd):
            destination[key] = value

    def getSensors(self, showOnlyUpdated = False):
        if ((not showOnlyUpdated) and (not self.eventChanged) and (len(self.sensorResult) != 0)):
            return self.sensorResult

        self.sensorResult.clear()

        if (showOnlyUpdated):
            try:
                value = self.getReservoirLevel()
                key = self.KEY_RESERVOIR_LEVEL
            except AutomationControlError as e:
                value = e.args[0]
                key = self.KEY_RESERVOIR_LEVEL_FAULT

            self.updateHelper(self.sensorResult, key, value, self.reservoirLevelUpdated)
            self.updateHelper(self.sensorResult, self.KEY_RESERVOIR_SENSOR_VOLTAGE, self.getSensorVoltage(), self.reservoirLevelUpdated)
            self.updateHelper(self.sensorResult, self.KEY_ERROR_STATUS, self.errorStatus, self.errorStatusUpdated)
            self.updateHelper(self.sensorResult, self.KEY_PLC_SYSTEM_TIMESTAMP, self.plcTimestamp, self.eventChanged)
            self.updateHelper(
                self.sensorResult,
                self.KEY_READY_TIMER,
                self.getReadyTimer(),
                self.readyTimerSnapshotUpdated
            )
            self.updateHelper(
                self.sensorResult,
                self.KEY_WATER_PUMP_TIMER,
                self.getWaterPumpTimer(),
                self.waterPumpTimerSnapshotUpdated
            )
            self.updateHelper(
                self.sensorResult,
                self.KEY_PLC_STATUS,
                self.getPlcStatus(),
                self.plcSystemStatusUpdated or self.plcSystemReadyUpdated or self.waterPumpStatusUpdated or self.automaticModeUpdated
            )

            return self.sensorResult

        try:
            self.sensorResult[self.KEY_RESERVOIR_LEVEL] = self.getReservoirLevel()
        except AutomationControlError as e:
            self.sensorResult[self.KEY_RESERVOIR_LEVEL_FAULT] = e.args[0]

        self.sensorResult[self.KEY_RESERVOIR_SENSOR_VOLTAGE] = self.getSensorVoltage()
        self.sensorResult[self.KEY_ERROR_STATUS] = self.errorStatus
        self.sensorResult[self.KEY_PLC_SYSTEM_TIMESTAMP] = self.plcTimestamp
        self.sensorResult[self.KEY_READY_TIMER] = self.getReadyTimer()
        self.sensorResult[self.KEY_WATER_PUMP_TIMER] = self.getWaterPumpTimer()
        self.sensorResult[self.KEY_PLC_STATUS] = self.getPlcStatus()

        return self.sensorResult

    def getSensorsStr(self, showOnlyUpdated = False):
        if ((not showOnlyUpdated) and (not self.eventChanged) and (len(self.sensorResultStr) != 0)):
            return self.sensorResultStr

        self.sensorResultStr.clear()

        if (showOnlyUpdated):
            try:
                value = self.getReservoirLevelStr()
                key = self.KEY_RESERVOIR_LEVEL
            except AutomationControlError as e:
                value = e.args[0]
                key = self.KEY_RESERVOIR_LEVEL_FAULT

            self.updateHelper(self.sensorResultStr, key, value, self.reservoirLevelUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_RESERVOIR_SENSOR_VOLTAGE, self.getSensorVoltageStr(), self.reservoirLevelUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_ERROR_STATUS, self.errorStatus, self.errorStatusUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_PLC_SYSTEM_TIMESTAMP, self.plcTimestamp, self.eventChanged)
            self.updateHelper(
                self.sensorResultStr,
                self.KEY_READY_TIMER,
                self.getReadyTimer(),
                self.readyTimerSnapshotUpdated
            )
            self.updateHelper(
                self.sensorResultStr,
                self.KEY_WATER_PUMP_TIMER,
                self.getWaterPumpTimer(),
                self.waterPumpTimerSnapshotUpdated
            )
            self.updateHelper(
                self.sensorResultStr,
                self.KEY_PLC_STATUS,
                self.getPlcStatus(),
                self.plcSystemStatusUpdated or self.plcSystemReadyUpdated or self.waterPumpStatusUpdated or self.automaticModeUpdated
            )

            return self.sensorResultStr

        try:
            self.sensorResultStr[self.KEY_RESERVOIR_LEVEL] = self.getReservoirLevelStr()
        except AutomationControlError as e:
            self.sensorResultStr[self.KEY_RESERVOIR_LEVEL_FAULT] = e.args[0]

        self.sensorResultStr[self.KEY_RESERVOIR_SENSOR_VOLTAGE] = self.getSensorVoltageStr()
        self.sensorResultStr[self.KEY_ERROR_STATUS] = self.errorStatus
        self.sensorResultStr[self.KEY_PLC_SYSTEM_TIMESTAMP] = self.plcTimestamp
        self.sensorResultStr[self.KEY_READY_TIMER] = self.getReadyTimer()
        self.sensorResultStr[self.KEY_WATER_PUMP_TIMER] = self.getWaterPumpTimer()
        self.sensorResultStr[self.KEY_PLC_STATUS] = self.getPlcStatus()

        return self.sensorResultStr

    def setResetSystem(self):
        self.panel.modbus.writeCoil(Registers.Outputs.Discrete.EMERGENCY_RESET_SYSTEM_REG, True)


    def setSystemReady(self):
        self.panel.modbus.writeCoil(Registers.Outputs.Discrete.SET_SYSTEM_READY_REG, True)

    def setPumpON(self):
        self.panel.modbus.writeCoil(Registers.Outputs.Discrete.SET_PUMP_ON, True)

    def toggleAutomaticMode(self):
        self.panel.modbus.writeCoil(Registers.Outputs.Discrete.MB_BUTTON_TOGGLE_AUTOMATIC_MODE, True)