#from pymodbus.client.sync import ModbusTcpClient #OLD Python 3.6
from pymodbus.client import ModbusTcpClient # new Python 3.10

class ModBusUtil:
    def __init__(self, ipAddress, port) -> None:
        self.ipAddress = ipAddress
        self.port = port
        self.master = ModbusTcpClient(ipAddress, port, retries=3, retry_on_empty=True)

    def readShort(self, address):
        result = self.master.read_holding_registers(address)
        # Note: Unlimited int cause parse error. See https://portingguide.readthedocs.io/en/latest/numbers.html
        # Solution is below:
        shortValue = result.registers[0]

        if (shortValue & 0x8000):
            shortValue = not shortValue
            shortValue = -(shortValue + 1)

        return shortValue

    def readInt(self, address):
        result = self.master.read_holding_registers(address, 2)
        return ((result.registers[0]<<16)|(result.registers[1]))

    def readCoil(self, address):
        result = self.master.read_coils(address, 1)
        return result.bits[0]

    def readInput(self, address):
        result = self.master.read_discrete_inputs(address, 1)
        return result.bits[0]

    def writeCoil(self, address, value):
        self.master.write_coil(address, value)

    def close(self):
        self.master.close()
