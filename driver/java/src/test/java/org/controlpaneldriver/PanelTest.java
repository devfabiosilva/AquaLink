package org.controlpaneldriver;

import org.apache.plc4x.java.api.exceptions.PlcConnectionException;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import static org.controlpaneldriver.exception.AutomationControlError.MB_ERROR_SUCCESS;

/**
 * To run this test you need to be connected to Panel control. It works only on real-time mode
 *
 * You need to set correct ModBus TCP IP address at AUTOMATION_PANEL_IP_ADDRESS
 */
@Ignore
public class PanelTest {
    private Panel panel;
    private final String AUTOMATION_PANEL_IP_ADDRESS = "modbus:tcp://192.168.1.111";
    private final long TIMEOUT = 1000;

    @Before
    public void setUp() throws PlcConnectionException {
        panel = new Panel(AUTOMATION_PANEL_IP_ADDRESS, TIMEOUT);
    }

    @Test
    public void testPlcMonitorStr() throws Throwable {
        do {
            panel.getPlc().readSensors(false);
            System.out.println(panel.getPlc().getSensorsStr(true));
            panel.getPowerMeter().readSensors(false);
            System.out.println(panel.getPowerMeter().getSensorsStr(true));
            Thread.sleep(1000);
        } while (panel.getPlc().getWaterPumpStatus() || panel.getPlc().getErrorStatus() == MB_ERROR_SUCCESS);
    }

    @Test
    public void testPlcMonitor() throws Throwable {
        do {
            panel.getPlc().readSensors(false);
            System.out.println(panel.getPlc().getSensors(true));
            panel.getPowerMeter().readSensors(false);
            System.out.println(panel.getPowerMeter().getSensors(true));
            Thread.sleep(1000);
        } while (panel.getPlc().getWaterPumpStatus() || panel.getPlc().getErrorStatus() == MB_ERROR_SUCCESS);
    }

    @Test
    public void testPlcMonitorStrAll() throws Throwable {
        do {
            panel.getPlc().readSensors(false);
            System.out.println(panel.getPlc().getSensorsStr(false));
            panel.getPowerMeter().readSensors(false);
            System.out.println(panel.getPowerMeter().getSensorsStr(false));
            Thread.sleep(1000);
        } while (panel.getPlc().getWaterPumpStatus() || panel.getPlc().getErrorStatus() == MB_ERROR_SUCCESS);
    }

    @Test
    public void testPlcMonitorAll() throws Throwable {
        do {
            panel.getPlc().readSensors(false);
            System.out.println(panel.getPlc().getSensors(false));
            panel.getPowerMeter().readSensors(false);
            System.out.println(panel.getPowerMeter().getSensors(false));
            Thread.sleep(1000);
        } while (panel.getPlc().getWaterPumpStatus() || panel.getPlc().getErrorStatus() == MB_ERROR_SUCCESS);
    }

    @Test
    public void powerMeterStrTest() throws Throwable {
        System.out.println(panel.getPowerMeter());
        panel.getPowerMeter().readSensors(false);
        System.out.println(panel.getPowerMeter());
    }

    @Test
    public void powerMeterReadSensorsTest() throws Throwable {
        System.out.println(panel.getPowerMeter().getSensorsStr(false));
        panel.getPowerMeter().readSensors(false);
        System.out.println(panel.getPowerMeter().getSensorsStr(false));
        System.out.println(panel.getPowerMeter().getSensorsStr(true));
        panel.getPowerMeter().readSensors(false);
        System.out.println(panel.getPowerMeter().getSensorsStr(false));
        panel.getPowerMeter().readSensors(false);
        System.out.println(panel.getPowerMeter().getSensorsStr(true));
    }

    @Test
    public void setResetSystemTest() throws Throwable {
        panel.getPlc().setResetSystem();
        System.out.println("Result ");
    }

    @Test
    public void setSystemReadyTest() throws Throwable {
        panel.getPlc().setSystemReady();
        System.out.println("Result ");
    }

    @Test
    public void setPumpON() throws Throwable {
        panel.getPlc().setPumpON();
        System.out.println("Result ");
    }

    @Test
    public void toggleAutomaticModeTest() throws Throwable {
        panel.getPlc().toggleAutomaticMode();
        System.out.println("Result ");
    }
}
