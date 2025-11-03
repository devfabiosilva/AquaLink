from pymodbus.client.sync import ModbusTcpClient
## Initial release.
## Test PLC panel.
## Connect IoT Gateway between Cloud service and Automation control
client = ModbusTcpClient('192.168.1.111')
client.write_coil(0x060B, True)
result = client.read_coils(0x603,1)
print(result.bits[0])
client.close()
