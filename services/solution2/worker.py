import os
import signal
import sys

import paho.mqtt.client as mqtt
import threading
import time

from panel import Panel
import json
import panelauth as p
import ssl

import hashlib

# https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php
# Possible bug in pyModBus: https://github.com/home-assistant/core/issues/52773
# Update? https://github.com/home-assistant/core/pull/53020
#https://community.home-assistant.io/t/modbus-connection-ok-but-unable-to-receive-data-from-the-device/318804/6

# {'plc': {'plcSystemTimestamp': 2271, 'readyTimer': 47, 'plcStatus': 11}, 'powerMeter': {'frequency': '60.01'}}
# Client is connected ? True
# wORKING ...
# DEBUG:pymodbus.transaction:Current transaction state - TRANSACTION_COMPLETE
# DEBUG:pymodbus.transaction:Running transaction 9950
# DEBUG:pymodbus.transaction:SEND: 0x26 0xde 0x0 0x0 0x0 0x6 0x0 0x3 0x0 0x0 0x0 0x1
# DEBUG:pymodbus.client.sync:New Transaction state 'SENDING'
# DEBUG:pymodbus.transaction:Changing transaction state from 'SENDING' to 'WAITING FOR REPLY'
# DEBUG:pymodbus.transaction:Transaction failed. (Modbus Error: [Invalid Message] No response received, expected at least 8 bytes (0 received)) 
# DEBUG:pymodbus.transaction:Retry on empty response - 3
# DEBUG:pymodbus.transaction:Changing transaction state from 'WAITING_FOR_REPLY' to 'RETRYING'
# DEBUG:pymodbus.transaction:Sleeping 0.3
# ERROR:pymodbus.client.sync:Connection to (192.168.1.111, 502) failed: timed out
# ERROR:pymodbus.client.sync:Connection to (192.168.1.111, 502) failed: timed out
# DEBUG:pymodbus.transaction:SEND: 0x26 0xde 0x0 0x0 0x0 0x6 0x0 0x3 0x0 0x0 0x0 0x1
# Error connection to Panel. Verify cable or IP address. REASON: ModbusTcpClient(192.168.1.111:502)
# {'fault': 'Error connection to Panel. Verify cable or IP address. REASON: ModbusTcpClient(192.168.1.111:502)'}
# SOLVED @ may 14 2022 00:37

debug = True
client = None
quitService = False
frequency = 20
threadLock = threading.Lock()

spamThreadLock = threading.Lock()
maxCommandCount = 0
lastSpamTimestamp = 0.0

controlPanel = None
panelAuthenticator = None
lastTokenId = None
eventTopic = "wocpoc2/event"
commandTopic = "wocpoc2/command"
commandKey = "plcCommand"
commandFault = "commandFault"

frequencyCount = 0

def on_connect(client, userdata, flags, rc):
    """On connect"""
    global threadLock
    global spamThreadLock
    global debug
    global commandTopic

    threadLock.acquire()
    spamThreadLock.acquire()
    if (debug):
        print("Connected with result code "+str(rc))
    client.subscribe(commandTopic, 0)
    spamThreadLock.release()
    threadLock.release()

def on_disconnect(client, userdata, rc):
    """On disconnect"""
    global threadLock
    global spamThreadLock
    global debug
    threadLock.acquire()
    spamThreadLock.acquire()
    if (debug):
        print("Disconnected with result code "+str(rc))
    spamThreadLock.release()
    threadLock.release()

def on_message(client, userdata, msg):
    """On message"""
    global debug
    global messageProcessing
    global quitService
    global lastTokenId
    global commandFault
    global threadLock

    if (threadLock.locked()):
        if (debug):
            print("Ignoring command. Panel still in process")
        client.publish(eventTopic, "{\"" + commandFault + "\":\"Ignoring command. Panel still in process. Reject !\"}")
        return

    threadLock.acquire()
    if (quitService):
        if (debug):
            print("Ignoring command. Quit process in progress ...")

        threadLock.release()
        return

    if (debug):
        print("Received message '"+str(msg.payload)+"' on topic '"+msg.topic+"' with QoS "+str(msg.qos))

    if (msg.qos != 0):
        errMsg = "Only QoS = 0 is allowed to send commands. Ignoring command."
        if (debug):
            print(errMsg)

        client.publish(eventTopic, "{\"" + commandFault + "\":\"" + errMsg + "\"}")

        threadLock.release()
        return

    if (checkSpam(1, 4)):
        errMsg = "Spam detected. Wait 4 seconds to send command"
        if (debug):
            print(errMsg)

        client.publish(eventTopic, "{\"" + commandFault + "\":\"" + errMsg + "\"}")

        threadLock.release()
        return

    try:
        res = json.loads(msg.payload.decode('utf-8'))
    except BaseException as e:
        if (not debug):
            client.publish(eventTopic, "{\"" + commandFault + "\":\"JSON parse error\"}")
        else:
            client.publish(eventTopic, "{\"" + commandFault + "\":\"JSON exception @ " + e.args[0] + "\"}")
        
        threadLock.release()
        return

    try:
        valid_format_value = validate_format(res)
    except BaseException as e:
        if (debug):
            print("Exception @ validate_format " + e.args[0])

        client.publish(eventTopic, "{\"" + commandFault + "\":\"Validate format error. " + e.args[0] + "\"}")
        threadLock.release()
        return

    try:
        valid_sig = is_valid_signature(valid_format_value)
    except BaseException as e:
        if (debug):
            print("Exception @ is_valid_signature with message: " + e.args[0])

        client.publish(eventTopic, "{\"" + commandFault + "\":\"Validate signature error. " + e.args[0] + "\"}")
        threadLock.release()
        return

    if (not valid_sig):
        if (debug):
            print("Invalid SIGNATURE. Reject !")

        client.publish(eventTopic, "{\"" + commandFault + "\":\"INVALID SIGNATURE. Reject !\"}")
        threadLock.release()
        return

    try:
        valid_totp = is_valid_TOTP(valid_format_value)
    except BaseException as e:
        if (debug):
            print("Exception @ is_valid_TOTP with message: " + str(e.args[0]))

        client.publish(eventTopic, "{\"" + commandFault + "\":\"Validate Auth TOTP error. " + e.args[0] + "\"}")
        threadLock.release()
        return

    if (not valid_totp):
        if (debug):
            print("Invalid or expired token TOTP. Reject !")

        client.publish(eventTopic, "{\"" + commandFault + "\":\"Invalid or expired token TOTP. Reject !\"}")
        threadLock.release()
        return

    if (lastTokenId == valid_format_value[0]):
        if (debug):
            print("Token is VALID, but is rejected !")

        client.publish(eventTopic, "{\"" + commandFault + "\":\"Valid but rejected. Reason: Same last ID !\"}")
        threadLock.release()
        return

    try:
        setCommand(valid_format_value)
    except BaseException as e:
        if (debug):
            print("Could not execute command: " + e.args[0])

        client.publish(eventTopic, "{\"" + commandFault + "\":\"Could not set command to panel: " + e.args[0] + "\"}")
        threadLock.release()
        return

    m = hashlib.sha256(res[commandKey].encode())
    lastTokenId = valid_format_value[0]
    client.publish(eventTopic, "{\"commandSuccess\": \"" + m.digest().hex() + "\"}")

    clearCheckSpam()

    threadLock.release()

def clearCheckSpam() -> None:
    global lastSpamTimestamp
    global maxCommandCount
    global spamThreadLock

    spamThreadLock.acquire()

    lastSpamTimestamp = time.time()
    maxCommandCount = 1

    spamThreadLock.release()

def checkSpam(maxCommands: int, delay: float) -> bool:
    global maxCommandCount
    global lastSpamTimestamp
    global spamThreadLock

    isSpam = False

    spamThreadLock.acquire()

    tmp = time.time() - lastSpamTimestamp

    if (tmp < delay):
        maxCommandCount += 1

        if (maxCommandCount > maxCommands):
            lastSpamTimestamp = time.time()
            isSpam = True
    else:
        lastSpamTimestamp = time.time()

    spamThreadLock.release()

    return isSpam

def setCommand(valid_format_value):
    global controlPanel
    global frequencyCount
    global frequency
    global debug

    if (controlPanel == None):
        raise BaseException("Control panel driver is not ready")

    COMMAND_SET_RESET = 1
    COMMAND_SET_MONITORE = 2
    COMMAND_SET_PUMP_ON = 3
    COMMAND_TOGGLE_AUTOMATIC_MODE = 4
    COMMAND_TEST = 5

    tmp = valid_format_value[2]

    if (tmp == COMMAND_SET_RESET):
        try:
            controlPanel.plc.setResetSystem()
            frequencyCount = frequency - 1
            return
        except BaseException as e:
            if (not debug):
                raise BaseException("Could not reset panel system. Verify ModBus TCP/IP connection cable")
            else:
                raise BaseException("Panel system reset error with message: " + e.args[0])

    if (tmp == COMMAND_SET_MONITORE):
        try:
            controlPanel.plc.setSystemReady()
            frequencyCount = frequency - 1
            return
        except BaseException as e:
            if (not debug):
                raise BaseException("Could not start monitoring system. Verify ModBus TCP/IP connection cable")
            else:
                raise BaseException("Panel start monitoring system error with message: " + e.args[0])

    if (tmp == COMMAND_SET_PUMP_ON):
        try:
            controlPanel.plc.setPumpON()
            frequencyCount = frequency - 1
            return
        except BaseException as e:
            if (not debug):
                raise BaseException("Could not turn ON water pump. Verify ModBus TCP/IP connection cable")
            else:
                raise BaseException("Panel turn ON water pump error with message: " + e.args[0])

    if (tmp == COMMAND_TOGGLE_AUTOMATIC_MODE):
        try:
            controlPanel.plc.toggleAutomaticMode()
            frequencyCount = frequency - 1
            return
        except BaseException as e:
            if (not debug):
                raise BaseException("Could not toggle automatic mode. Verify ModBus TCP/IP connection cable")
            else:
                raise BaseException("Panel toggle automatic mode error with message: " + e.args[0])

    if (tmp == COMMAND_TEST):
        return

    raise BaseException("Invalid panel command")

def is_valid_TOTP(valid_format_value) -> bool:
    global panelAuthenticator

    if (panelAuthenticator == None):
        raise BaseException("Panel authenticator TOTP not initialized")

    return panelAuthenticator.getAuthTotp() == valid_format_value[1]


def is_valid_signature(valid_format_value) -> bool:
    global debug

    if (panelAuthenticator == None):
        if (not debug):
            raise BaseException("Panel authenticator error")
        else:
            raise BaseException("panelAuthenticator not initialized")

    try:
        signMessage = panelAuthenticator.signMessage(valid_format_value[4]).hex().lower()
    except BaseException as e:
        if (not debug):
            raise BaseException("Internal panel authentication error")
        else:
            raise BaseException("Internal panel authentication in C library error with message: " + e.args[0])

    return valid_format_value[3] == signMessage

def validate_format(parsedJson):
    global commandKey
    tmp = len(parsedJson)
    if (tmp != 1):
        raise BaseException("Wrong required key(s) = " + str(tmp) + ". Expected 1 key")

    if (not commandKey in parsedJson):
        raise BaseException("Missing '" + commandKey + "' token")

    commandValue = parsedJson[commandKey]

    if (not isinstance(commandValue, str)):
        raise BaseException("Expected string token")

    if (len(commandValue) != 88):
        raise BaseException("Wrong string token size")

    commandValues = commandValue.split(".")

    if (len(commandValues) != 4):
        raise BaseException("Wrong command format")

    tmp = commandValues[0]
    if (len(tmp) != 10):
        raise BaseException("Wrong token id token size")

    try:
        tmp = int(tmp)
    except:
        raise BaseException("Could not parse id token")

    if (tmp < 0 or tmp > 4294967295):
        raise BaseException("Invalid ID interval")

    values = []

    values.append(tmp)

    tmp = commandValues[1]

    if (len(tmp) != 6):
        raise BaseException("Wrong Auth2 size")

    try:
        tmp = int(tmp)
    except:
        raise BaseException("Could not parse Auth2 value")

    values.append(tmp)

    tmp = commandValues[2]

    if (len(tmp) != 5):
        raise BaseException("Invalid command size")

    try:
        tmp = int(tmp)
    except:
        raise BaseException("Could not parse command value")

    values.append(tmp)
    values.append(commandValues[3].lower())
    values.append(commandValues[0] + commandValues[1] + commandValues[2])

    return values

class BrokerClient(threading.Thread):
    def __init__(self, name, clientId):
        threading.Thread.__init__(self)
        self.name = name
        self.clientId = clientId

    def run(self):
        global client
        global quitService
        global debug
        global frequency
        global eventTopic
        global threadLock

        data = {}

        global frequencyCount
        forceUpdate = True

        threadLock.acquire()

        client = mqtt.Client(client_id=self.clientId, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        client.tls_set(
            ca_certs="../../security/cli/ca.crt",
            certfile="../../security/cli/endpoint.crt",
            keyfile="../../security/cli/endpoint.key",
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        client.tls_insecure_set(True) # For test only. Never use this in real world
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message

        print("Initiating client ", client)

        threadLock.release()

        keepInitialLoop = True

        while keepInitialLoop:
            threadLock.acquire()
            if (quitService):
                threadLock.release()
                print("Quitting signal")
                return

            try:
                client.connect("localhost", 8883, 10)
                client.loop_start()
                print("Connection success", client.is_connected())
                threadLock.release()
                keepInitialLoop = False
            except BaseException as e:
                threadLock.release()
                print("Fail on connect. Trying again")
                print(e.args)
                time.sleep(3)

        while True:
            if (debug):
                print("Client is connected ?", client.is_connected())

            time.sleep(2)

            threadLock.acquire()

            if (quitService):
                threadLock.release()
                print("Quiting ...")
                break

            if client.is_connected():
                if (debug):
                    print("wORKING ...")

                if controlPanel != None:
                    data.clear()

                    isPanelError = None

                    try:
                        controlPanel.plc.readSensors(forceUpdate)
                        controlPanel.powerMeter.readSensors(forceUpdate)
                    except BaseException as e:
                        isPanelError = "Error connection to Panel. Verify cable or IP address."
                        if (debug):
                            print(isPanelError)

                    if (isPanelError == None):
                        tmp = controlPanel.plc.getSensorsStr(not forceUpdate)
                        if (len(tmp)):
                            data["plc"] = tmp

                        tmp = controlPanel.powerMeter.getSensorsStr(not forceUpdate)
                        if (len(tmp)):
                            data["powerMeter"] = tmp

                        if (frequencyCount < frequency):
                            frequencyCount += 1
                        else:
                            frequencyCount = 0

                        forceUpdate = (frequencyCount == frequency)
                    else:
                        frequencyCount = 0
                        data["fault"] = isPanelError

                if (debug):
                    print(data)

                if (len(data)):
                    client.publish(eventTopic, json.dumps(data), 1, True)
            else:
                try:
                    client.reconnect()
                except BaseException as e:
                    print("Fail on connect. Trying again")
                    print(e.args)

            threadLock.release()

def quitAll():
    global quitService
    global threadLock

    threadLock.acquire()
    quitService = True
    threadLock.release()

def init_service(is_debug):
    global quitService
    global controlPanel
    global panelAuthenticator
    global debug

    debug = is_debug

    signal.signal(signal.SIGQUIT, signal_handler)
    print("PID ", os.getpid())

    print("Panel Auth2 module init: ", p.__doc__)

    panelAuthenticator = p.create(
        "This is your key. It can be any text with any char like @123#~. Don't tell this key to anybody",
        "MNSDSNRSMRSDOOJWMU2TMOJSGZTGIM3B", # This is Your AUTH2 key. Copy and paste in your google authenticator. Don't tell this key to anybody
    )

    controlPanel = Panel('192.168.1.111') # TODO Refactor to initializer. No mocks !!!
    thread1 = BrokerClient("Name", "testClientId")

    thread1.start()
    print("Starting broker thread ", thread1)

    thread1.join()

def signal_handler(signum, stack):
    print("SIGNAL RECIEVED", signum, stack)
    print("Closing processes. Wait ...")
    quitAll()
    print("Closing ...")
    sys.exit()
