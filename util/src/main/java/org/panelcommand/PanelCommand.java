package org.panelcommand;

import org.apache.commons.codec.digest.HmacUtils;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import static java.lang.String.format;
import static org.apache.commons.codec.digest.HmacAlgorithms.HMAC_SHA_256;

public class PanelCommand {
    private long id = 0;
    private final HmacUtils hm256;

    public PanelCommand(String key) throws NoSuchAlgorithmException {
        final MessageDigest digest = MessageDigest.getInstance("SHA-256");
        this.hm256 = new HmacUtils(
                HMAC_SHA_256,
                digest.digest(key.getBytes(StandardCharsets.UTF_8))
        );
    }

    public String signMessage(long totp, int command) {
        this.id &= 0xFFFFFFFF;
        totp &= 0xFFFFFFFF;
        command &= 0xFFFF;
        StringBuilder toBeSigned = new StringBuilder();
        String idStr = format("%010d", this.id++);
        String totpStr = format("%06d", totp);
        String commandStr = format("%05d", command);

        toBeSigned.append(idStr);
        toBeSigned.append(totpStr);
        toBeSigned.append(commandStr);

        return idStr + "." + totpStr + "." + commandStr + "." + this.hm256.hmacHex(toBeSigned.toString());
    }

    public String signMessageJsonString(long totp, int command) {
        return "{\"plcCommand\":\"" + signMessage(totp, command) + "\"}";
    }
}
