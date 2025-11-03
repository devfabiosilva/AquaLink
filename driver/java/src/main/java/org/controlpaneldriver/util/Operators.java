package org.controlpaneldriver.util;

import org.jetbrains.annotations.NotNull;

import static java.lang.String.format;

public class Operators {
    private Operators() {}

    public static long opUtil(long result) {
        int op = (int)result&0xFFFF;
        result >>= 16;
        result &= 0xFFFF;

        result |= ((long) op <<16);

        if ((result & 0x80000000L) != 0)
            result |= 0xFFFFFFFF00000000L;

        return result;
    }

    public static @NotNull String fixedPoint(int value, int size, int precision) {
        String valueStr = format("%0" + size + "d", value);
        int i = valueStr.length() - precision;
        return valueStr.substring(0, i) + "." + valueStr.substring(i);
    }
}
