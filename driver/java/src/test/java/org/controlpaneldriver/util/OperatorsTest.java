package org.controlpaneldriver.util;
import org.junit.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.controlpaneldriver.util.Operators.opUtil;

public class OperatorsTest {

    @Test
    public void opUtilTest() {
        //op1|op2
        short op1 = 3;
        short op2 = 1;
        int value1 = op1 | (op2 << 16);
        System.out.println(value1);
        assertThat(opUtil(value1)).isEqualTo(0x30001L);

        op1 = (short)0xFFFF;
        op2 = (short)0xFFFF;
        value1 = op1 | (op2 << 16);
        System.out.println(value1);
        assertThat(opUtil(value1)).isEqualTo(-1L);

        //op1 = (short)0xFFFF;
        op2 = (short)(~(0x0BF6))+1;
        value1 = op1&0xFFFF | (op2 << 16);
        System.out.println(value1);
        assertThat(opUtil(value1)).isEqualTo(-3062L);

    }

    @Test
    public void fixedPointTest() {
    }
}