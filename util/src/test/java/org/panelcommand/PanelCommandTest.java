package org.panelcommand;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

public class PanelCommandTest {
    private PanelCommand panelCommand;

    @Before
    public void setUp() throws Exception {
        panelCommand = new PanelCommand("secret");
    }

    @Test
    public void generateTokenTest() {
        String result = panelCommand.signMessage(1, 1);
        Assert.assertEquals(
                "0000000000.000001.00001.e394a725f043b4c8fb3f6bd6da60a2185e08ff8b14980d59a2671b3d36d57556",
                result
        );
        result = panelCommand.signMessage(1, 1);
        Assert.assertEquals(
                "0000000001.000001.00001.6d34e1b81fdec8412d4d1c6451558cb4267bae7bfad04573928c1eb237cdd0f2",
                result
        );
    }

    @Test
    public void generateTokenJsonTest() {
        String result = panelCommand.signMessageJsonString(1, 1);
        Assert.assertEquals(
                "{\"plcCommand\":\"0000000000.000001.00001.e394a725f043b4c8fb3f6bd6da60a2185e08ff8b14980d59a2671b3d36d57556\"}",
                result
        );
        result = panelCommand.signMessageJsonString(1, 1);
        Assert.assertEquals(
                "{\"plcCommand\":\"0000000001.000001.00001.6d34e1b81fdec8412d4d1c6451558cb4267bae7bfad04573928c1eb237cdd0f2\"}",
                result
        );
    }
}