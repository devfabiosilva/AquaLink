from panel import Panel
import logging

def main():
    """Main file application"""

    logging.basicConfig()
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    panel = Panel('192.168.1.111')
    panel.plc.readSensors()

    print(panel.plc.getSensorsStr())
    print(panel.plc.getSensors())

    panel.powerMeter.readSensors()

    print(panel.powerMeter.getSensorsStr())
    print(panel.powerMeter.getSensors())
    #panel.plc.setResetSystem()
    #panel.plc.setPumpON()

    panel.close()

if __name__ == "__main__":
    main()
