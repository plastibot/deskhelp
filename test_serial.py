import serial
import time

try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.isOpen()
    print ("port is opened")

except IOError:
    ser.close()
    ser.open()
    print("port was already open, was closed and opened again")

ser.write("1,7=".encode())

time.sleep(3)

ser.write("1,5=".encode())

ser.close()
