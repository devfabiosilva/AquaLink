package org.controlpaneldriver.plc;

import org.controlpaneldriver.Panel;
import org.controlpaneldriver.exception.AutomationControlError;

import java.util.Map;
import java.util.TreeMap;

import static java.lang.Thread.sleep;
import static org.controlpaneldriver.automation.Registers.Inputs.Analog.MB_WATER_LEVEL_SENSOR;
import static org.controlpaneldriver.automation.Registers.Inputs.Discrete.*;
import static org.controlpaneldriver.automation.Registers.Outputs.Discrete.*;
import static org.controlpaneldriver.automation.Registers.System.*;
import static org.controlpaneldriver.automation.Sensors.ReservoirLevel.*;
import static org.controlpaneldriver.exception.AutomationControlError.*;
import static org.controlpaneldriver.modbusutil.ModBusUtil.HOLDING_REGISTER;
import static org.controlpaneldriver.util.Operators.*;

public class Ac12m0p {

    public static final String KEY_RESERVOIR_LEVEL = "reservoirLevel";
    public static final String KEY_RESERVOIR_LEVEL_FAULT = "reservoirLevelFault";
    public static final String KEY_RESERVOIR_SENSOR_VOLTAGE = "reservoirSensorVoltage";
    public static final String KEY_ERROR_STATUS = "errorStatus";
    public static final String KEY_PLC_SYSTEM_TIMESTAMP = "plcSystemTimestamp";
    public static final String KEY_READY_TIMER = "readyTimer";
    public static final String KEY_WATER_PUMP_TIMER = "waterPumpTimer";
    public static final String KEY_PLC_STATUS = "plcStatus";

    public static final short FLAG_SYSTEM_STATUS = (short)1;
    public static final short FLAG_SYSTEM_READY = FLAG_SYSTEM_STATUS << 1;
    public static final short FLAG_PUMP_STATUS = FLAG_SYSTEM_READY << 1;
    public static final short FLAG_AUTOMATIC_MODE = FLAG_PUMP_STATUS << 1;
    public static final short FLAG_SYSTEM_TESTING_INDICATOR_PANEL = FLAG_AUTOMATIC_MODE << 1;

    private final Panel panel;

    private short reservoirLevel = 0;
    private short errorStatus = 0;
    private long plcTimestamp = 0;
    private long waterPumpTimerSnapshot = 0;
    private long readyTimerSnapshot = 0;
    private boolean plcSystemStatus = false;
    private boolean plcSystemReady = false;
    private boolean waterPumpStatus = false;
    private boolean automaticMode = false;
    private boolean panelIndicatorTester = false;

    private boolean eventChanged = true;

    private boolean reservoirLevelUpdated = true;
    private boolean errorStatusUpdated = true;
    private boolean waterPumpTimerSnapshotUpdated = true;
    private boolean readyTimerSnapshotUpdated = true;
    private boolean plcSystemStatusUpdated = true;
    private boolean plcSystemReadyUpdated = true;
    private boolean waterPumpStatusUpdated = true;
    private boolean automaticModeUpdated = true;
    private boolean panelIndicatorTesterUpdated = true;

    private TreeMap<String, Object> sensorResult = null;
    private TreeMap<String, Object> sensorResultStr = null;

    private void plcCleanUp() {
        this.reservoirLevel = 0;
        this.errorStatus = 0;
        this.plcTimestamp = 0;
        this.waterPumpTimerSnapshot = 0;
        this.readyTimerSnapshot = 0;
        this.plcSystemStatus = false;
        this.plcSystemReady = false;
        this.waterPumpStatus = false;
        this.automaticMode = false;
        this.panelIndicatorTester = false;

        this.eventChanged = true;

        this.reservoirLevelUpdated = true;
        this.errorStatusUpdated = true;
        this.waterPumpTimerSnapshotUpdated = true;
        this.readyTimerSnapshotUpdated = true;
        this.plcSystemStatusUpdated = true;
        this.plcSystemReadyUpdated = true;
        this.waterPumpStatusUpdated = true;
        this.automaticModeUpdated = true;
        this.panelIndicatorTesterUpdated = true;

        if (sensorResult != null)
            sensorResult.clear();

        if (sensorResultStr != null)
            sensorResultStr.clear();

        panel.unlock();
    }

    private void updateHelper(Map<String, Object> destination, String key, Object value, boolean shouldAdd) {
        if (shouldAdd)
            destination.put(key, value);
    }

    private int reservoirLevelHelper() throws AutomationControlError {
        short sensorValue = this.reservoirLevel;

        if (sensorValue > PRESSURE_SENSOR_FAIL_HIGH || this.errorStatus == MB_ERROR_CODE_RESERVOIR_OVERFLOW)
            throw new AutomationControlError("CRITICAL: Water level overflow or pressure sensor malfunction");

        if (sensorValue < PRESSURE_SENSOR_FAIL_LOW || this.errorStatus == MB_ERROR_CODE_RESERVOIR_SENSOR_ERR)
            throw new AutomationControlError("CRITICAL: Water level below expected. Check pressure sensor or communication cable.");

        if (sensorValue > PRESSURE_SENSOR_RESERVOIR_FULL_UPPER_LIMIT)
            sensorValue = PRESSURE_SENSOR_RESERVOIR_FULL_UPPER_LIMIT;
        else if (sensorValue < PRESSURE_SENSOR_RESERVOIR_EMPTY)
            sensorValue = PRESSURE_SENSOR_RESERVOIR_EMPTY;

        return (1000*(sensorValue - PRESSURE_SENSOR_RESERVOIR_EMPTY)) / PRESSURE_SENSOR_RESERVOIR_RANGE;
    }

    public Ac12m0p(Panel panel) {
        this.panel = panel;
    }

    public void readSensors(boolean forceUpdate) throws Throwable {
        boolean booleanValue;
        short shortValue;
        long longValue;

        while (panel.isLocked())
            sleep(10);

        panel.lock();

        try {
            shortValue = panel.readShort(MB_WATER_LEVEL_SENSOR, HOLDING_REGISTER);
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        this.reservoirLevelUpdated = (shortValue != this.reservoirLevel);
        this.eventChanged = this.reservoirLevelUpdated;
        this.reservoirLevel = shortValue;

        try {
            shortValue = panel.readShort(MB_ERROR_REG_ADDRESS, HOLDING_REGISTER);
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        this.errorStatusUpdated = (shortValue != this.errorStatus);
        this.eventChanged |= this.errorStatusUpdated;
        this.errorStatus = shortValue;

        try {
            this.plcTimestamp = opUtil(panel.readInt(MB_SYSTEM_TIMER, HOLDING_REGISTER));
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        try {
            longValue = opUtil(panel.readInt(MB_SYSTEM_READY_TIMER, HOLDING_REGISTER));
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        this.readyTimerSnapshotUpdated = (longValue > -1);
        this.eventChanged |= this.readyTimerSnapshotUpdated;
        this.readyTimerSnapshot = longValue;

        try {
            longValue = opUtil(panel.readInt(MB_SYSTEM_WATER_PUMP_TIMER, HOLDING_REGISTER));
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        this.waterPumpTimerSnapshotUpdated = (longValue > -1);
        this.eventChanged |= this.waterPumpTimerSnapshotUpdated;
        this.waterPumpTimerSnapshot = longValue;

        booleanValue = (this.errorStatus == MB_ERROR_SUCCESS);
        this.plcSystemStatusUpdated = (booleanValue != this.plcSystemStatus);
        this.eventChanged |= this.plcSystemStatusUpdated;
        this.plcSystemStatus = booleanValue;

        try {
            booleanValue = panel.readCoil(MB_READY_MONITORE_STATUS);
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        this.plcSystemReadyUpdated = (booleanValue != this.plcSystemReady);
        this.eventChanged |= this.plcSystemReadyUpdated;
        this.plcSystemReady = booleanValue;

        try {
            booleanValue = panel.readCoil(MB_PUMP_REG);
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        this.waterPumpStatusUpdated = (booleanValue != this.waterPumpStatus);
        this.eventChanged |= this.waterPumpStatusUpdated;
        this.waterPumpStatus = booleanValue;

        try {
            booleanValue = panel.readCoil(MB_TEST_PANEL_INDICATOR_REG);
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        this.panelIndicatorTesterUpdated = (booleanValue != this.waterPumpStatus);
        this.eventChanged |= this.panelIndicatorTesterUpdated;
        this.panelIndicatorTester = booleanValue;

        try {
            booleanValue = panel.readCoil(MB_BUTTON_AUTOMATIC_MODE);
        } catch (Throwable e) {
            this.plcCleanUp();
            throw e;
        }

        this.automaticModeUpdated = (booleanValue != this.automaticMode);
        this.eventChanged |= this.automaticModeUpdated;
        this.automaticMode = booleanValue;

        this.eventChanged |= forceUpdate;

        panel.unlock();
    }

    public double getReservoirLevel() throws AutomationControlError {
        return reservoirLevelHelper() / 1000.0;
    }

    public String getReservoirLevelStr() throws AutomationControlError {
        return fixedPoint(reservoirLevelHelper(), 2, 1);
    }

    public double getSensorVoltage() {
        return this.reservoirLevel * K_CONST;
    }

    public String getSensorVoltageStr() {
        return fixedPoint((this.reservoirLevel * ADC_SENSOR_MAX) / ADC_SENSOR_STEP, 4, 3);
    }

    public short getErrorStatus() {
        return this.errorStatus;
    }

    public long getPlcTimestamp() {
        return this.plcTimestamp;
    }

    public long getReadyTimer() {
        if (this.readyTimerSnapshot >= 0)
            return this.plcTimestamp - this.readyTimerSnapshot;

        return 0;
    }

    public long getWaterPumpTimer() {
        if (this.waterPumpTimerSnapshot >= 0)
            return this.plcTimestamp - this.waterPumpTimerSnapshot;

        return 0;
    }

    public boolean getPlcSystemStatus() {
        return this.plcSystemStatus;
    }

    public boolean getPlcSystemReady() {
        return this.plcSystemReady;
    }

    public boolean getWaterPumpStatus() {
        return this.waterPumpStatus;
    }

    public boolean getAutomaticMode() {
        return this.automaticMode;
    }

    public short getPlcStatus() {
        short shortValue = 0;

        if (this.plcSystemStatus)
            shortValue = FLAG_SYSTEM_STATUS;

        if (this.plcSystemReady)
            shortValue |= FLAG_SYSTEM_READY;

        if (this.waterPumpStatus)
            shortValue |= FLAG_PUMP_STATUS;

        if (this.automaticMode)
            shortValue |= FLAG_AUTOMATIC_MODE;

        if (this.panelIndicatorTester)
            shortValue |= FLAG_SYSTEM_TESTING_INDICATOR_PANEL;

        return shortValue;
    }

    public Map<String, Object> getSensors(boolean showOnlyUpdated) {
        if (this.sensorResult == null)
            this.sensorResult = new TreeMap<>();

        if ((!showOnlyUpdated) && (!this.eventChanged) && (sensorResult.size() != 0))
            return this.sensorResult;

        sensorResult.clear();

        if (showOnlyUpdated) {
            String key;
            Object value;

            try {
                value = getReservoirLevel();
                key = KEY_RESERVOIR_LEVEL;
            } catch (AutomationControlError e) {
                value = e.getMessage();
                key = KEY_RESERVOIR_LEVEL_FAULT;
            }

            updateHelper(this.sensorResult, key, value, this.reservoirLevelUpdated);
            updateHelper(this.sensorResult, KEY_RESERVOIR_SENSOR_VOLTAGE, getSensorVoltage(), this.reservoirLevelUpdated);
            updateHelper(this.sensorResult, KEY_ERROR_STATUS, this.errorStatus, this.errorStatusUpdated);
            updateHelper(this.sensorResult, KEY_PLC_SYSTEM_TIMESTAMP, this.plcTimestamp, this.eventChanged);
            updateHelper(
                    this.sensorResult,
                    KEY_READY_TIMER,
                    getReadyTimer(),
                    this.readyTimerSnapshotUpdated
            );
            updateHelper(
                    this.sensorResult,
                    KEY_WATER_PUMP_TIMER,
                    getWaterPumpTimer(),
                    this.waterPumpTimerSnapshotUpdated
            );
            updateHelper(
                    this.sensorResult,
                    KEY_PLC_STATUS,
                    getPlcStatus(),
                    this.plcSystemStatusUpdated || this.plcSystemReadyUpdated || this.waterPumpStatusUpdated || this.automaticModeUpdated
            );

            return this.sensorResult;
        }

        try {
            sensorResult.put(KEY_RESERVOIR_LEVEL, getReservoirLevel());
        } catch (AutomationControlError e) {
            sensorResult.put(KEY_RESERVOIR_LEVEL_FAULT, e.getMessage());
        }

        sensorResult.put(KEY_RESERVOIR_SENSOR_VOLTAGE, getSensorVoltage());
        sensorResult.put(KEY_ERROR_STATUS, this.errorStatus);
        sensorResult.put(KEY_PLC_SYSTEM_TIMESTAMP, this.plcTimestamp);
        sensorResult.put(KEY_READY_TIMER, getReadyTimer());
        sensorResult.put(KEY_WATER_PUMP_TIMER, getWaterPumpTimer());
        sensorResult.put(KEY_PLC_STATUS, getPlcStatus());

        return this.sensorResult;
    }

    public Map<String, Object> getSensorsStr(boolean showOnlyUpdated) {
        if (this.sensorResultStr == null)
            this.sensorResultStr = new TreeMap<>();

        if ((!showOnlyUpdated) && (!this.eventChanged) && (sensorResultStr.size() != 0))
            return this.sensorResultStr;

        sensorResultStr.clear();

        if (showOnlyUpdated) {
            String key;
            Object value;

            try {
                value = getReservoirLevelStr();
                key = KEY_RESERVOIR_LEVEL;
            } catch (AutomationControlError e) {
                value = e.getMessage();
                key = KEY_RESERVOIR_LEVEL_FAULT;
            }

            updateHelper(this.sensorResultStr, key, value, this.reservoirLevelUpdated);
            updateHelper(this.sensorResultStr, KEY_RESERVOIR_SENSOR_VOLTAGE, getSensorVoltageStr(), this.reservoirLevelUpdated);
            updateHelper(this.sensorResultStr, KEY_ERROR_STATUS, this.errorStatus, this.errorStatusUpdated);
            updateHelper(this.sensorResultStr, KEY_PLC_SYSTEM_TIMESTAMP, this.plcTimestamp, this.eventChanged);
            updateHelper(
                    this.sensorResultStr,
                    KEY_READY_TIMER,
                    getReadyTimer(),
                    this.readyTimerSnapshotUpdated
            );
            updateHelper(
                    this.sensorResultStr,
                    KEY_WATER_PUMP_TIMER,
                    getWaterPumpTimer(),
                    this.waterPumpTimerSnapshotUpdated
            );
            updateHelper(
                    this.sensorResultStr,
                    KEY_PLC_STATUS,
                    getPlcStatus(),
                    this.plcSystemStatusUpdated || this.plcSystemReadyUpdated || this.waterPumpStatusUpdated || this.automaticModeUpdated
            );

            return this.sensorResultStr;
        }

        try {
            sensorResultStr.put(KEY_RESERVOIR_LEVEL, getReservoirLevelStr());
        } catch (AutomationControlError e) {
            sensorResultStr.put(KEY_RESERVOIR_LEVEL_FAULT, e.getMessage());
        }

        sensorResultStr.put(KEY_RESERVOIR_SENSOR_VOLTAGE, getSensorVoltageStr());
        sensorResultStr.put(KEY_ERROR_STATUS, this.errorStatus);
        sensorResultStr.put(KEY_PLC_SYSTEM_TIMESTAMP, this.plcTimestamp);
        sensorResultStr.put(KEY_READY_TIMER, getReadyTimer());
        sensorResultStr.put(KEY_WATER_PUMP_TIMER, getWaterPumpTimer());
        sensorResultStr.put(KEY_PLC_STATUS, getPlcStatus());

        return this.sensorResultStr;
    }

    public boolean gotEvents() {
        return this.eventChanged;
    }

    public void setResetSystem() throws Throwable {
        while (panel.isLocked())
            sleep(10);

        panel.lock();

        try {
            panel.writeCoil(EMERGENCY_RESET_SYSTEM_REG, true);
        } catch (Throwable e) {
            panel.unlock();
            throw e;
        }

        panel.unlock();
    }

    public void setSystemReady() throws Throwable {
        while (panel.isLocked())
            sleep(10);

        panel.lock();

        try {
            panel.writeCoil(SET_SYSTEM_READY_REG, true);
        } catch (Throwable e) {
            panel.unlock();
            throw e;
        }

        panel.unlock();
    }

    public void setPumpON() throws Throwable {
        while (panel.isLocked())
            sleep(10);

        panel.lock();

        try {
            panel.writeCoil(SET_PUMP_ON, true);
        } catch (Throwable e) {
            panel.unlock();
            throw e;
        }

        panel.unlock();
    }

    public void toggleAutomaticMode() throws Throwable {
        while (panel.isLocked())
            sleep(10);

        panel.lock();

        try {
            panel.writeCoil(MB_BUTTON_TOGGLE_AUTOMATIC_MODE, true);
        } catch (Throwable e) {
            panel.unlock();
            throw e;
        }

        panel.unlock();
    }

    public String toString() {
        return this.getSensorsStr(false).toString();
    }
}
