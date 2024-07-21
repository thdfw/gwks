import serial

ser = serial.Serial('/dev/serial0', 9600)

try:
    while True:
        if ser.in_waiting > 0:
            received = ser.readline()#.decode('utf-8').rstrip()
            print("Received:", received)
except KeyboardInterrupt:
    print("Exiting program...")
finally:
    ser.close()