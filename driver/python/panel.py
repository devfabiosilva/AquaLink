from lib.plc.ac12m0p import Ac12m0p
from lib.protocol.modbusutil import ModBusUtil
from lib.serial.powermeter import PowerMeter

class Panel():
    def __init__(self, ipAddress, port = 502):
        self.modbus = ModBusUtil(ipAddress, port)
        self.plc = Ac12m0p(self)
        self.powerMeter = PowerMeter(self)

    def close(self):
        self.modbus.close()
