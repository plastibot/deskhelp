import serial

try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.isOpen()
    print ("port is opened")

except IOError:
    ser.close()
    ser.open()
    print("port was already open, was closed and opened again")

ser.write("1,7=")
