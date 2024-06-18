import serial

PORT = '/dev/cu.usbmodem2101'
BAUDRATE = 115200

try:
    serial_connection = serial.Serial(PORT, BAUDRATE)
    txt_file = open('/Users/thomas/Documents/gwks/pico/picodata.txt', 'wb')

    while True:
        data = serial_connection.read(32)
        if data:
            print(data)
            txt_file.write(data)
        
except serial.SerialException as e:
    print(f"Serial port error: {e}")

except IOError as e:
    print(f"IOError: {e}")

except Exception as e:
    print(f"Exception occurred: {e}")

finally:
    if 'serial_connection' in locals() and serial_connection.is_open:
        serial_connection.close()
    if 'txt_file' in locals():
        txt_file.close()
