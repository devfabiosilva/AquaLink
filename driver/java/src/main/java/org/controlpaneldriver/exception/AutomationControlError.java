package org.controlpaneldriver.exception;

public class AutomationControlError extends Throwable {
    public static final short MB_ERROR_CODE_RESERVOIR_SENSOR_ERR = -1;
    public static final short MB_ERROR_CODE_RESERVOIR_OVERFLOW = -2;
    public static final short MB_ERROR_SUCCESS = 0;
    public AutomationControlError(String message) {
        super(message);
    }
}
