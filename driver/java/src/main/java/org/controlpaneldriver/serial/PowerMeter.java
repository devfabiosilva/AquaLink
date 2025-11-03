package org.controlpaneldriver.serial;

import org.controlpaneldriver.Panel;
import org.controlpaneldriver.exception.AutomationControlError;

import java.util.Map;
import java.util.TreeMap;

import static java.lang.Thread.sleep;
import static org.controlpaneldriver.automation.Registers.Inputs.*;
import static org.controlpaneldriver.modbusutil.ModBusUtil.HOLDING_REGISTER;
import static org.controlpaneldriver.util.Operators.fixedPoint;

public class PowerMeter {

    public static final String KEY_TOTAL_KWH = "totalKWh";
    public static final String KEY_IMPORT_KWH = "importKWh";
    public static final String KEY_EXPORT_KWH = "exportKWh";
    public static final String KEY_ACTIVE_POWER = "activePower";
    public static final String KEY_REACTIVE_POWER = "reactivePower";
    public static final String KEY_REACTIVE_POWER_FAULT = "reactivePowerError";
    public static final String KEY_CURRENT = "current";
    public static final String KEY_VOLTAGE = "voltage";
    public static final String KEY_POWER_FACTOR = "powerFactor";
    public static final String KEY_FREQUENCY = "frequency";

    private final Panel panel;

    private int totalKWh = 0;
    private int importKwh = 0;
    private int exportKWh = 0;
    private int reactivePower = 0;
    private short activePower = 0;
    private short current = 0;
    private short voltage = 0;
    private short powerFactor = 0;
    private short frequency = 0;

    private boolean eventChanged = true;

    private boolean totalKWhUpdated = true;
    private boolean importKwhUpdated = true;
    private boolean exportKWhUpdated = true;
    private boolean reactivePowerUpdated = true;
    private boolean activePowerUpdated = true;
    private boolean currentUpdated = true;
    private boolean voltageUpdated = true;
    private boolean powerFactorUpdated = true;
    private boolean frequencyUpdated = true;

    private TreeMap<String, Object> sensorResult = null;
    private TreeMap<String, Object> sensorResultStr = null;

    private void powerMeterCleanUp() {
        this.totalKWh = 0;
        this.importKwh = 0;
        this.exportKWh = 0;
        this.reactivePower = 0;
        this.activePower = 0;
        this.current = 0;
        this.voltage = 0;
        this.powerFactor = 0;
        this.frequency = 0;

        this.eventChanged = true;

        this.totalKWhUpdated = true;
        this.importKwhUpdated = true;
        this.exportKWhUpdated = true;
        this.reactivePowerUpdated = true;
        this.activePowerUpdated = true;
        this.currentUpdated = true;
        this.voltageUpdated = true;
        this.powerFactorUpdated = true;
        this.frequencyUpdated = true;

        if (this.sensorResult != null)
            this.sensorResult.clear();

        if (this.sensorResultStr != null)
            this.sensorResultStr.clear();

        panel.unlock();
    }
    private void updateHelper(Map<String, Object> destination, String key, Object value, boolean shouldAdd) {
        if (shouldAdd)
            destination.put(key, value);
    }

    public PowerMeter(Panel panel) {
        this.panel = panel;
    }

    public void readSensors(boolean forceUpdate) throws Throwable {
        int intValue;
        short shortValue;

        while (panel.isLocked())
            sleep(10);

        panel.lock();

        try {
            intValue = panel.readInt(TOTAL_KWH_REG, HOLDING_REGISTER);
        } catch (Throwable e) {
            powerMeterCleanUp();
            throw e;
        }

        this.totalKWhUpdated = (intValue != this.totalKWh);
        this.eventChanged = this.totalKWhUpdated;
        this.totalKWh = intValue;

        try {
            intValue = panel.readInt(IMPORT_KWH_REG, HOLDING_REGISTER);
        } catch (Throwable e) {
            powerMeterCleanUp();
            throw e;
        }

        this.importKwhUpdated = (intValue != this.importKwh);
        this.eventChanged |= this.importKwhUpdated;
        this.importKwh = intValue;

        try {
            intValue = panel.readInt(EXPORT_KWH_REG, HOLDING_REGISTER);
        } catch (Throwable e) {
            powerMeterCleanUp();
            throw e;
        }

        this.exportKWhUpdated = (intValue != this.exportKWh);
        this.eventChanged |= this.exportKWhUpdated;
        this.exportKWh = intValue;

        try {
            shortValue = panel.readShort(ACTIVE_POWER_REG, HOLDING_REGISTER);
        } catch (Throwable e) {
            powerMeterCleanUp();
            throw e;
        }

        this.activePowerUpdated = (shortValue != this.activePower);
        this.eventChanged |= this.activePowerUpdated;
        this.activePower = shortValue;

        try {
            shortValue = panel.readShort(CURRENT_REG, HOLDING_REGISTER);
        } catch (Throwable e) {
            powerMeterCleanUp();
            throw e;
        }

        this.currentUpdated = (shortValue != this.current);
        this.eventChanged |= this.currentUpdated;
        this.current = shortValue;

        try {
            shortValue = panel.readShort(VOLTAGE_REG, HOLDING_REGISTER);
        } catch (Throwable e) {
            powerMeterCleanUp();
            throw e;
        }

        this.voltageUpdated = (shortValue != this.voltage);
        this.eventChanged |= this.voltageUpdated;
        this.voltage = shortValue;

        try {
            shortValue = panel.readShort(POWER_FACTOR_REG, HOLDING_REGISTER);
        } catch (Throwable e) {
            powerMeterCleanUp();
            throw e;
        }

        this.powerFactorUpdated = (shortValue != this.powerFactor);
        this.eventChanged |= this.powerFactorUpdated;
        this.powerFactor = shortValue;

        try {
            shortValue = panel.readShort(FREQUENCY_REG, HOLDING_REGISTER);
        } catch (Throwable e) {
            powerMeterCleanUp();
            throw e;
        }

        this.frequencyUpdated = (shortValue != this.frequency);
        this.eventChanged |= this.frequencyUpdated;
        this.frequency = shortValue;

        try {
            intValue = getReactivePowerHelper();
        } catch (AutomationControlError e) {
            powerMeterCleanUp();
            throw e;
        }

        this.reactivePowerUpdated = (intValue != this.reactivePower);
        this.eventChanged |= this.reactivePowerUpdated;
        this.reactivePower = intValue;

        this.eventChanged |= forceUpdate;

        panel.unlock();
    }

    public double getTotalKWh() {
        return this.totalKWh / 100.0;
    }

    public String getTotalKWhStr() {
        return fixedPoint(this.totalKWh, 8, 2);
    }

    public double getImportKWh() {
        return this.importKwh / 100.0;
    }

    public String getImportKWhStr() {
        return fixedPoint(this.importKwh, 8, 2);
    }

    public double getExportKWh() {
        return this.exportKWh / 100.0;
    }

    public String getExportKWhStr() {
        return fixedPoint(this.exportKWh, 8, 2);
    }

    public double getActivePower() {
        return this.activePower / 1000.0;
    }

    public String getActivePowerStr() {
        return fixedPoint(this.activePower, 6, 3);
    }

    public double getCurrent() {
        return this.current / 100.0;
    }

    public String getCurrentStr() {
        return fixedPoint(this.current, 4, 2);
    }

    public double getVoltage() {
        return this.voltage / 10.0;
    }

    public String getVoltageStr() {
        return fixedPoint(this.voltage, 4, 1);
    }

    public double getPowerFactor() {
        return this.powerFactor / 1000.0;
    }

    public String getPowerFactorStr() {
        return fixedPoint(this.powerFactor, 4, 3);
    }

    public double getFrequency() {
        return this.frequency / 100.0;
    }

    public String getFrequencyStr() {
        return fixedPoint(this.frequency, 4, 2);
    }

    private int getReactivePowerHelper() throws AutomationControlError {
        final int K_FACTOR = 1000000;
        if (this.powerFactor > 1000 || this.powerFactor < -1000)
            throw new AutomationControlError("Error. Inconsistent data");

        return (int)(this.voltage*this.current*Math.sqrt(K_FACTOR - Math.pow(this.powerFactor, 2))/1000000.0);
    }

    public double getReactivePower() throws AutomationControlError {
        return getReactivePowerHelper() / 1000.0;
    }

    public String getReactivePowerStr() throws AutomationControlError {
        return fixedPoint(getReactivePowerHelper(), 6, 3);
    }

    public Map<String, Object> getSensors(boolean showOnlyUpdated) {
        String key;
        Object value;

        if (this.sensorResult == null)
            this.sensorResult = new TreeMap<>();

        if ((!showOnlyUpdated) && (!this.eventChanged) && (sensorResult.size() != 0))
            return this.sensorResult;

        sensorResult.clear();

        if (showOnlyUpdated) {

            updateHelper(this.sensorResult, KEY_TOTAL_KWH, getTotalKWh(), this.totalKWhUpdated);
            updateHelper(this.sensorResult, KEY_IMPORT_KWH, getImportKWh(), this.importKwhUpdated);
            updateHelper(this.sensorResult, KEY_EXPORT_KWH, getExportKWh(), this.exportKWhUpdated);
            updateHelper(this.sensorResult, KEY_ACTIVE_POWER, getActivePower(), this.activePowerUpdated);

            if (this.reactivePowerUpdated) {
                try {
                    value = getReactivePower();
                    key = KEY_REACTIVE_POWER;
                } catch (AutomationControlError e) {
                    value = e.getMessage();
                    key = KEY_REACTIVE_POWER_FAULT;
                }

                updateHelper(this.sensorResult, key, value, true);
            }

            updateHelper(this.sensorResult, KEY_CURRENT, getCurrent(), this.currentUpdated);
            updateHelper(this.sensorResult, KEY_VOLTAGE, getVoltage(), this.voltageUpdated);
            updateHelper(this.sensorResult, KEY_POWER_FACTOR, getPowerFactor(), this.powerFactorUpdated);
            updateHelper(this.sensorResult, KEY_FREQUENCY, getFrequency(), this.frequencyUpdated);

            return this.sensorResult;
        }

        sensorResult.put(KEY_TOTAL_KWH, getTotalKWh());
        sensorResult.put(KEY_IMPORT_KWH, getImportKWh());
        sensorResult.put(KEY_EXPORT_KWH, getExportKWh());
        sensorResult.put(KEY_ACTIVE_POWER, getActivePower());

        try {
            value = getReactivePower();
            key = KEY_REACTIVE_POWER;
        } catch (AutomationControlError e) {
            value = e.getMessage();
            key = KEY_REACTIVE_POWER_FAULT;
        }

        sensorResult.put(key, value);
        sensorResult.put(KEY_CURRENT, getCurrent());
        sensorResult.put(KEY_VOLTAGE, getVoltage());
        sensorResult.put(KEY_POWER_FACTOR, getPowerFactor());
        sensorResult.put(KEY_FREQUENCY, getFrequency());

        return this.sensorResult;
    }

    public Map<String, Object> getSensorsStr(boolean showOnlyUpdated) {
        String key;
        String value;

        if (this.sensorResultStr == null)
            this.sensorResultStr = new TreeMap<>();

        if ((!showOnlyUpdated) &&(!this.eventChanged) && (sensorResultStr.size() != 0))
            return this.sensorResultStr;

        sensorResultStr.clear();

        if (showOnlyUpdated) {

            updateHelper(this.sensorResultStr, KEY_TOTAL_KWH, getTotalKWhStr(), this.totalKWhUpdated);
            updateHelper(this.sensorResultStr, KEY_IMPORT_KWH, getImportKWhStr(), this.importKwhUpdated);
            updateHelper(this.sensorResultStr, KEY_EXPORT_KWH, getExportKWhStr(), this.exportKWhUpdated);
            updateHelper(this.sensorResultStr, KEY_ACTIVE_POWER, getActivePowerStr(), this.activePowerUpdated);

            if (this.reactivePowerUpdated) {
                try {
                    value = getReactivePowerStr();
                    key = KEY_REACTIVE_POWER;
                } catch (AutomationControlError e) {
                    value = e.getMessage();
                    key = KEY_REACTIVE_POWER_FAULT;
                }

                updateHelper(this.sensorResultStr, key, value, true);
            }

            updateHelper(this.sensorResultStr, KEY_CURRENT, getCurrentStr(), this.currentUpdated);
            updateHelper(this.sensorResultStr, KEY_VOLTAGE, getVoltageStr(), this.voltageUpdated);
            updateHelper(this.sensorResultStr, KEY_POWER_FACTOR, getPowerFactorStr(), this.powerFactorUpdated);
            updateHelper(this.sensorResultStr, KEY_FREQUENCY, getFrequencyStr(), this.frequencyUpdated);

            return this.sensorResultStr;
        }

        sensorResultStr.put(KEY_TOTAL_KWH, getTotalKWhStr());
        sensorResultStr.put(KEY_IMPORT_KWH, getImportKWhStr());
        sensorResultStr.put(KEY_EXPORT_KWH, getExportKWhStr());
        sensorResultStr.put(KEY_ACTIVE_POWER, getActivePowerStr());

        try {
            value = getReactivePowerStr();
            key = KEY_REACTIVE_POWER;
        } catch (AutomationControlError e) {
            value = e.getMessage();
            key = KEY_REACTIVE_POWER_FAULT;
        }

        sensorResultStr.put(key, value);
        sensorResultStr.put(KEY_CURRENT, getCurrentStr());
        sensorResultStr.put(KEY_VOLTAGE, getVoltageStr());
        sensorResultStr.put(KEY_POWER_FACTOR, getPowerFactorStr());
        sensorResultStr.put(KEY_FREQUENCY, getFrequencyStr());

        return this.sensorResultStr;
    }

    public boolean gotEvents() {
        return this.eventChanged;
    }

    public String toString() {
        return this.getSensorsStr(false).toString();
    }
}
