import os
import signal
import sys

import paho.mqtt.client as mqtt
import threading
import time

from panel import Panel
import json

# https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php
debug = True
client = None
quitService = False
frequency = 20
threadLock = threading.Lock()

controlPanel = None

def on_connect(client, userdata, flags, rc):
    """On connect"""
    global debug
    if (debug):
        print("Connected with result code "+str(rc))
    client.subscribe("wocpoc2/command", 1)

def on_disconnect(client, userdata, rc):
    """On disconnect"""
    global debug
    if (debug):
        print("Disconnected with result code "+str(rc))

def on_message(client, userdata, msg):
    """On message"""
    global debug
    if (debug):
        print("Received message '"+str(msg.payload)+"' on topic '"+msg.topic+"' with QoS "+str(msg.qos))
    print(msg.payload)

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

        data = {}

        frequencyCount = 0
        forceUpdate = True

        threadLock.acquire()

        client = mqtt.Client(client_id=self.clientId, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
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
                client.connect("localhost", 1883, 10)
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
                        isPanelError = "Error connection to Panel. Verify cable or IP address. REASON: " + e.args[0]
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
                    client.publish("wocpoc2/event", json.dumps(data), 1, True)
            else:
                try:
                    client.reconnect()
                except BaseException as e:
                    print("Fail on connect. Trying again")
                    print(e.args)

            threadLock.release()

def quitAll():
    global quitService

    threadLock.acquire()
    quitService = True
    threadLock.release()

def init_service():
    global quitService
    global controlPanel

    signal.signal(signal.SIGQUIT, signal_handler)
    print("PID ", os.getpid())

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
