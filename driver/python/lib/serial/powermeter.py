import math
from lib.automation.registers import Registers
from lib.exception.automationcontrolerror import AutomationControlError
from lib.util.operators import fixedPoint
import panel

class PowerMeter:
    def __init__(self, panel: panel):
        self.panel = panel

    KEY_TOTAL_KWH = "totalKWh"
    KEY_IMPORT_KWH = "importKWh"
    KEY_EXPORT_KWH = "exportKWh"
    KEY_ACTIVE_POWER = "activePower"
    KEY_REACTIVE_POWER = "reactivePower"
    KEY_REACTIVE_POWER_FAULT = "reactivePowerError"
    KEY_CURRENT = "current"
    KEY_VOLTAGE = "voltage"
    KEY_POWER_FACTOR = "powerFactor"
    KEY_FREQUENCY = "frequency"

    totalKWh = 0
    importKwh = 0
    exportKWh = 0
    reactivePower = 0
    activePower = 0
    current = 0
    voltage = 0
    powerFactor = 0
    frequency = 0

    eventChanged = True

    totalKWhUpdated = True
    importKwhUpdated = True
    exportKWhUpdated = True
    reactivePowerUpdated = True
    activePowerUpdated = True
    currentUpdated = True
    voltageUpdated = True
    powerFactorUpdated = True
    frequencyUpdated = True

    sensorResult = {}
    sensorResultStr = {}

    def powerMeterCleanUp(self):
        self.totalKWh = 0
        self.importKwh = 0
        self.exportKWh = 0
        self.reactivePower = 0
        self.activePower = 0
        self.current = 0
        self.voltage = 0
        self.powerFactor = 0
        self.frequency = 0

        self.eventChanged = True

        self.totalKWhUpdated = True
        self.importKwhUpdated = True
        self.exportKWhUpdated = True
        self.reactivePowerUpdated = True
        self.activePowerUpdated = True
        self.currentUpdated = True
        self.voltageUpdated = True
        self.powerFactorUpdated = True
        self.frequencyUpdated = True

    def readSensors(self, forceUpdate = False):
        try:
            intValue = self.panel.modbus.readInt(Registers.Inputs.TOTAL_KWH_REG)
        except:
            self.powerMeterCleanUp()
            raise

        self.totalKWhUpdated = (intValue != self.totalKWh)
        self.eventChanged = self.totalKWhUpdated
        self.totalKWh = intValue

        try:
            intValue = self.panel.modbus.readInt(Registers.Inputs.IMPORT_KWH_REG)
        except:
            self.powerMeterCleanUp()
            raise

        self.importKwhUpdated = (intValue != self.importKwh)
        self.eventChanged |= self.importKwhUpdated
        self.importKwh = intValue

        try:
            intValue = self.panel.modbus.readInt(Registers.Inputs.EXPORT_KWH_REG)
        except:
            self.powerMeterCleanUp()
            raise

        self.exportKWhUpdated = (intValue != self.exportKWh)
        self.eventChanged |= self.exportKWhUpdated
        self.exportKWh = intValue

        try:
            shortValue = self.panel.modbus.readShort(Registers.Inputs.ACTIVE_POWER_REG)
        except:
            self.powerMeterCleanUp()
            raise

        self.activePowerUpdated = (shortValue != self.activePower)
        self.eventChanged |= self.activePowerUpdated
        self.activePower = shortValue

        try:
            shortValue = self.panel.modbus.readShort(Registers.Inputs.CURRENT_REG)
        except:
            self.powerMeterCleanUp()
            raise

        self.currentUpdated = (shortValue != self.current)
        self.eventChanged |= self.currentUpdated
        self.current = shortValue

        try:
            shortValue = self.panel.modbus.readShort(Registers.Inputs.VOLTAGE_REG)
        except:
            self.powerMeterCleanUp()
            raise

        self.voltageUpdated = (shortValue != self.voltage)
        self.eventChanged |= self.voltageUpdated
        self.voltage = shortValue

        try:
            shortValue = self.panel.modbus.readShort(Registers.Inputs.POWER_FACTOR_REG)
        except:
            self.powerMeterCleanUp()
            raise

        self.powerFactorUpdated = (shortValue != self.powerFactor)
        self.eventChanged |= self.powerFactorUpdated
        self.powerFactor = shortValue

        try:
            shortValue = self.panel.modbus.readShort(Registers.Inputs.FREQUENCY_REG)
        except:
            self.powerMeterCleanUp()
            raise

        self.frequencyUpdated = (shortValue != self.frequency)
        self.eventChanged |= self.frequencyUpdated
        self.frequency = shortValue

        try:
            intValue = self.getReactivePowerHelper()
        except AutomationControlError as e:
            self.powerMeterCleanUp()
            raise e

        self.reactivePowerUpdated = (intValue != self.reactivePower)
        self.eventChanged |= self.reactivePowerUpdated
        self.reactivePower = intValue

        self.eventChanged |= forceUpdate

    def getTotalKWh(self):
        return self.totalKWh / 100.0

    def getTotalKWhStr(self):
        return fixedPoint(self.totalKWh, 8, 2)

    def getImportKWh(self):
        return self.importKwh / 100.0

    def getImportKWhStr(self):
        return fixedPoint(self.importKwh, 8, 2)

    def getExportKWh(self):
        return self.exportKWh / 100.0

    def getExportKWhStr(self):
        return fixedPoint(self.exportKWh, 8, 2)

    def getActivePower(self):
        return self.activePower / 1000.0

    def getActivePowerStr(self):
        return fixedPoint(self.activePower, 6, 3)

    def getCurrent(self):
        return self.current / 100.0

    def getCurrentStr(self):
        return fixedPoint(self.current, 4, 2)

    def getVoltage(self):
        return self.voltage / 10.0

    def getVoltageStr(self):
        return fixedPoint(self.voltage, 4, 1)

    def getPowerFactor(self):
        return self.powerFactor / 1000.0

    def getPowerFactorStr(self):
        return fixedPoint(self.powerFactor, 4, 3)

    def getFrequency(self):
        return self.frequency / 100.0

    def getFrequencyStr(self):
        return fixedPoint(self.frequency, 4, 2)

    def getReactivePowerHelper(self):
        K_FACTOR = 1000000
        if (self.powerFactor > 1000 or self.powerFactor < -1000):
            raise AutomationControlError("Error. Inconsistent data")
        
        return (int)(self.current*self.voltage*math.sqrt(K_FACTOR - math.pow(self.powerFactor, 2))/1000000.0)

    def getReactivePower(self):
        return self.reactivePower / 1000.0

    def getReactivePowerStr(self):
        return fixedPoint(self.getReactivePowerHelper(), 6, 3)

    def updateHelper(self, destination, key, value, shouldAdd):
        if (shouldAdd):
            destination[key] = value

    def getSensors(self, showOnlyUpdated = False):
        if ((not showOnlyUpdated) and ( not self.eventChanged) and (len(self.sensorResult) != 0)):
            return self.sensorResult

        self.sensorResult.clear()

        if (showOnlyUpdated):
            self.updateHelper(self.sensorResult, self.KEY_TOTAL_KWH, self.getTotalKWh(), self.totalKWhUpdated)
            self.updateHelper(self.sensorResult, self.KEY_IMPORT_KWH, self.getImportKWh(), self.importKwhUpdated)
            self.updateHelper(self.sensorResult, self.KEY_EXPORT_KWH, self.getExportKWh(), self.exportKWhUpdated)
            self.updateHelper(self.sensorResult, self.KEY_ACTIVE_POWER, self.getActivePower(), self.activePowerUpdated)

            if (self.reactivePowerUpdated):
                try:
                    value = self.getReactivePower()
                    key = self.KEY_REACTIVE_POWER
                except AutomationControlError as e:
                    value = e.args[0]
                    key = self.KEY_REACTIVE_POWER_FAULT

                self.updateHelper(self.sensorResult, key, value, True)

            self.updateHelper(self.sensorResult, self.KEY_CURRENT, self.getCurrent(), self.currentUpdated)
            self.updateHelper(self.sensorResult, self.KEY_VOLTAGE, self.getVoltage(), self.voltageUpdated)
            self.updateHelper(self.sensorResult, self.KEY_POWER_FACTOR, self.getPowerFactor(), self.powerFactorUpdated)
            self.updateHelper(self.sensorResult, self.KEY_FREQUENCY, self.getFrequency(), self.frequencyUpdated)

            return self.sensorResult

        self.sensorResult[self.KEY_TOTAL_KWH] = self.getTotalKWh()
        self.sensorResult[self.KEY_IMPORT_KWH] = self.getImportKWh()
        self.sensorResult[self.KEY_EXPORT_KWH] = self.getExportKWh()
        self.sensorResult[self.KEY_ACTIVE_POWER] = self.getActivePower()

        try:
            value = self.getReactivePower()
            key = self.KEY_REACTIVE_POWER
        except AutomationControlError as e:
            value = e.args[0]
            key = self.KEY_REACTIVE_POWER_FAULT

        self.sensorResult[key] = value
        self.sensorResult[self.KEY_CURRENT] = self.getCurrent()
        self.sensorResult[self.KEY_VOLTAGE] = self.getVoltage()
        self.sensorResult[self.KEY_POWER_FACTOR] = self.getPowerFactor()
        self.sensorResult[self.KEY_FREQUENCY] = self.getFrequency()

        return self.sensorResult

    def getSensorsStr(self, showOnlyUpdated = False):
        if ((not showOnlyUpdated) and ( not self.eventChanged) and (len(self.sensorResultStr) != 0)):
            return self.sensorResultStr

        self.sensorResultStr.clear()

        if (showOnlyUpdated):
            self.updateHelper(self.sensorResultStr, self.KEY_TOTAL_KWH, self.getTotalKWhStr(), self.totalKWhUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_IMPORT_KWH, self.getImportKWhStr(), self.importKwhUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_EXPORT_KWH, self.getExportKWhStr(), self.exportKWhUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_ACTIVE_POWER, self.getActivePowerStr(), self.activePowerUpdated)

            if (self.reactivePowerUpdated):
                try:
                    value = self.getReactivePowerStr()
                    key = self.KEY_REACTIVE_POWER
                except AutomationControlError as e:
                    value = e.args[0]
                    key = self.KEY_REACTIVE_POWER_FAULT

                self.updateHelper(self.sensorResultStr, key, value, True)

            self.updateHelper(self.sensorResultStr, self.KEY_CURRENT, self.getCurrentStr(), self.currentUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_VOLTAGE, self.getVoltageStr(), self.voltageUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_POWER_FACTOR, self.getPowerFactorStr(), self.powerFactorUpdated)
            self.updateHelper(self.sensorResultStr, self.KEY_FREQUENCY, self.getFrequencyStr(), self.frequencyUpdated)

            return self.sensorResultStr

        self.sensorResultStr[self.KEY_TOTAL_KWH] = self.getTotalKWhStr()
        self.sensorResultStr[self.KEY_IMPORT_KWH] = self.getImportKWhStr()
        self.sensorResultStr[self.KEY_EXPORT_KWH] = self.getExportKWhStr()
        self.sensorResultStr[self.KEY_ACTIVE_POWER] = self.getActivePowerStr()

        try:
            value = self.getReactivePowerStr()
            key = self.KEY_REACTIVE_POWER
        except AutomationControlError as e:
            value = e.args[0]
            key = self.KEY_REACTIVE_POWER_FAULT

        self.sensorResultStr[key] = value
        self.sensorResultStr[self.KEY_CURRENT] = self.getCurrentStr()
        self.sensorResultStr[self.KEY_VOLTAGE] = self.getVoltageStr()
        self.sensorResultStr[self.KEY_POWER_FACTOR] = self.getPowerFactorStr()
        self.sensorResultStr[self.KEY_FREQUENCY] = self.getFrequencyStr()

        return self.sensorResultStr
