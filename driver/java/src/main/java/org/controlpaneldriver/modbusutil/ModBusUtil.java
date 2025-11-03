package org.controlpaneldriver.modbusutil;

import org.apache.plc4x.java.PlcDriverManager;
import org.apache.plc4x.java.api.PlcConnection;
import org.apache.plc4x.java.api.exceptions.PlcConnectionException;
import org.apache.plc4x.java.api.messages.PlcReadRequest;
import org.apache.plc4x.java.api.messages.PlcReadResponse;
import org.apache.plc4x.java.api.messages.PlcWriteRequest;
import org.apache.plc4x.java.api.messages.PlcWriteResponse;
import org.apache.plc4x.java.api.types.PlcResponseCode;
import org.jetbrains.annotations.NotNull;
import org.controlpaneldriver.exception.MBError;

import java.util.Collection;
import java.util.Iterator;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class ModBusUtil {
    private final PlcConnection plcConnection;
    public static final String HOLDING_REGISTER = "holding-register";
    public static final String COIL = "coil";
    public static final String DISCRETE_INPUT = "discrete-input";
    private final long timeout;

    public ModBusUtil(String uri, long timeout) throws PlcConnectionException {
        this.plcConnection = new PlcDriverManager().getConnection(uri);
        this.timeout = timeout;
    }

    @NotNull
    private PlcReadResponse mbReqSync(
            short address,
            String fieldName,
            String type,
            long timeout,
            short numberOfRegisters
    ) throws MBError, ExecutionException, InterruptedException, TimeoutException {

        if (!this.plcConnection.getMetadata().canRead())
            throw new MBError("Can not read");

        PlcReadRequest.Builder builder = this.plcConnection.readRequestBuilder();

        builder.addItem(fieldName, type + ":" + address + "[" + numberOfRegisters + "]");
        PlcReadRequest readRequest = builder.build();
        PlcReadResponse response = readRequest.execute().get(timeout, TimeUnit.MILLISECONDS);

        PlcResponseCode responseCode = response.getResponseCode(fieldName);

        if (responseCode == PlcResponseCode.OK)
            return response;

        throw new MBError("Can't read request " + responseCode);
    }

    @NotNull
    private PlcWriteResponse mbWriteSync(
            short address,
            String fieldName,
            String type,
            long timeout,
            Object... values
    ) throws MBError, ExecutionException, InterruptedException, TimeoutException {

        if (!this.plcConnection.getMetadata().canRead())
            throw new MBError("Can not write");

        PlcWriteRequest.Builder builder = this.plcConnection.writeRequestBuilder();

        builder.addItem(fieldName, type + ":" + address + "[" + values.length + "]", values);
        PlcWriteRequest writeRequest = builder.build();
        PlcWriteResponse response = writeRequest.execute().get(timeout, TimeUnit.MILLISECONDS);

        PlcResponseCode responseCode = response.getResponseCode(fieldName);
        if (responseCode == PlcResponseCode.OK)
            return response;

        throw new MBError("Can't write request " + responseCode);
    }

    private double mbToDouble(@NotNull Collection<Short> v) throws MBError {
        long l;
        /* IEEE 754 standard ! */

        Iterator<Short> t = v.iterator();

        if (v.size() != 4)
            throw new MBError("Not an IEEE 754 Double standard");

        l = (long)(t.next()&0xFFFF)<<48;
        l |= (long)(t.next()&0xFFFF)<<32;
        l |= (long)(t.next()&0xFFFF)<<16;
        l |= (t.next()&0xFFFF);

        return Double.longBitsToDouble(l);
    }

    private float mbToFloat(@NotNull Collection<Short> vector) throws MBError {
        int i;
        /* IEEE 754 standard ! */

        Iterator<Short> t = vector.iterator();

        if (vector.size() != 2)
            throw new MBError("Not an IEEE 754 float standard");

        i = (t.next()&0xFFFF)<<16;
        i |= (t.next()&0xFFFF);

        return Float.intBitsToFloat(i);
    }

    private int mbToInt(@NotNull Collection<Short> vector) throws MBError {
        int i;
        // 32 bits
        if (vector.size() != 2)
            throw new MBError("Int is not 32 bits");

        Iterator<Short> t = vector.iterator();

        i = (t.next()&0xFFFF)<<16;
        i |= t.next()&0xFFFF;

        return i;
    }

    public float readFloat(short address, String type) throws Throwable {
        final String fieldName = "field-5";
        PlcReadResponse response = mbReqSync(address, fieldName, type, timeout, (short) 2);
        return mbToFloat(response.getAllShorts(fieldName));
    }
    public double readDouble(short address, String type) throws Throwable {
        final String fieldName = "field-1";
        PlcReadResponse response = mbReqSync(address, fieldName, type, timeout, (short) 4);
        return mbToDouble(response.getAllShorts(fieldName));
    }

    public short readShort(short address, String type) throws Throwable {
        final String fieldName = "field-2";
        PlcReadResponse response = mbReqSync(address, fieldName, type, timeout, (short) 1);
        return response.getShort(fieldName);
    }

    public int readInt(short address, String type) throws Throwable {
        final String fieldName = "field-3";
        PlcReadResponse response = mbReqSync(address, fieldName, type, timeout, (short) 2);
        return mbToInt(response.getAllShorts(fieldName));
    }

    public boolean readCoil(short address) throws Throwable {
        final String fieldName = "field-4";
        PlcReadResponse response = mbReqSync(address, fieldName, COIL, timeout, (short) 1);
        return response.getBoolean(fieldName);
    }

    public boolean readInput(short address) throws Throwable {
        final String fieldName = "field-7";
        PlcReadResponse response = mbReqSync(address, fieldName, DISCRETE_INPUT, timeout, (short) 1);
        return response.getBoolean(fieldName);
    }

    public void writeCoil(short address, boolean value) throws Throwable {
        final String fieldName = "field-5";
        mbWriteSync(address, fieldName, COIL, timeout, value);
    }

    public void writeSingleRegister(short address, short value) throws Throwable {
        final String fieldName = "field-6";
        mbWriteSync(address, fieldName, HOLDING_REGISTER, timeout, value);
    }

    public void connect() throws PlcConnectionException {
        this.plcConnection.connect();
    }

    public boolean isConnected() {
        return this.plcConnection.isConnected();
    }

    public PlcConnection connection() {
        return this.plcConnection;
    }

}
