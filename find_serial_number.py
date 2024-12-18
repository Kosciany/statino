from serial.tools import list_ports
comports = list_ports.comports()

for comport in comports:
    if comport.serial_number is not None:
        print(comport.serial_number)
        print(comport.manufacturer)
