import paho.mqtt.client as mqtt

import panelauth as p
import ssl

panelAuthenticator = None

def command(client, topic, uid, cmd, totp) -> bool:
    global panelAuthenticator
    commandKey = "plcCommand"

    if (isinstance(cmd, str)):
        try:
            cmd = int(cmd)
        except:
            print("Could not parse command to int. Invalid number")
            return True

    if (isinstance(totp, str)):
        try:
            totp = int(totp)
        except:
            print("Could not convert input to int. Invalid number\n")
            return True

    if ((cmd == -1) or (totp == -1)):
        return False

    uidStr = ('{:010d}').format(uid)
    totpStr = ('{:06d}').format(totp) # Google Authenticator
    commandStr = ('{:05d}').format(cmd)

    signature = panelAuthenticator.signMessage(uidStr + totpStr + commandStr).hex()
    token = uidStr + "." + totpStr + "." + commandStr + "." + signature
    print("Generated token: " + token)
    thisJson = "{\"" + commandKey + "\":\"" + token + "\"}"
    print("JSON -> " + thisJson + "\nSending command ...\n")

    client.publish(topic, thisJson, 0)

    return True

def main():
    global panelAuthenticator

    commandTopic = "wocpoc2/command"

    panelAuthenticator = p.create(
        "This is your key. It can be any text with any char like @123#~. Don't tell this key to anybody"
    )

    client = mqtt.Client("test_plc_command", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
    client.tls_set(
        "../../../security/cli/ca.crt",
        "../../../security/cli/endpoint.crt",
        "../../../security/cli/endpoint.key",
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    client.tls_insecure_set(True) # For test only. Never use this in real world
    client.connect("localhost", 8883)
    client.loop_start()

    isLoop = True
    i = 0

    print("\nChoose commands:\n\n\t1 - COMMAND_SET_RESET\n\t2 - COMMAND_SET_MONITORE\n\t3 - COMMAND_SET_PUMP_ON\n\t4 - TOGGLE_AUTOMATIC_MODE\n\t5 - TEST COMMAND\n\tq To quit")
    while isLoop:
        print("\nDigit your Panel Command: ")
        yourCommand = input()

        if (yourCommand == "q"):
            break

        print("\nDigit your OAuth: ")
        yourAuth = input()

        if (yourAuth == "q"):
            break

        isLoop = command(client, commandTopic, i, yourCommand, yourAuth)

        i = i + 1

    print("\nQuitting ...\n")

if __name__=="__main__":
    main()
