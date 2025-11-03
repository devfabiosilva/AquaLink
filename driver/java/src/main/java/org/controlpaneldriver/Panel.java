package org.controlpaneldriver;

import org.apache.plc4x.java.api.exceptions.PlcConnectionException;
import org.controlpaneldriver.modbusutil.ModBusUtil;
import org.controlpaneldriver.plc.Ac12m0p;
import org.controlpaneldriver.serial.PowerMeter;

import java.util.concurrent.atomic.AtomicBoolean;

import static java.lang.Thread.sleep;

public class Panel extends ModBusUtil {

    private final Ac12m0p plc;
    private final PowerMeter powerMeter;
    private final AtomicBoolean panelCommLock = new AtomicBoolean(false);

    public Panel(String uri, long timeout) throws PlcConnectionException {
        super(uri, timeout);
        this.plc = new Ac12m0p(this);
        this.powerMeter = new PowerMeter(this);
    }

    public Ac12m0p getPlc() {
        return this.plc;
    }

    public PowerMeter getPowerMeter() {
        return this.powerMeter;
    }

    public boolean isLocked() {
        return this.panelCommLock.get();
    }

    public void lock() {
        this.panelCommLock.set(true);
    }

    public void unlock() {
        this.panelCommLock.set(false);
    }

    public void close() throws Exception {
        while (this.isLocked()) {
            sleep(5);
        }

        this.lock();

        try {
            this.connection().close();
        } catch (Exception e) {
            this.unlock();
            throw e;
        }

        this.unlock();
    }

}
