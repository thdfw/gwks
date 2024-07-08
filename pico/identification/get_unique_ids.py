"""
This code finds and prints the unique ID of each connected Pico.
For this code to work, the connected Picos must have a copy of the info.py file,
containing the info() function, which prints the unique ID of the Pico.
"""

from serial.tools import list_ports
import serial
import time

print('\nLooking for Picos...')

def find_picos():
    '''Returns a list of all connected Picos'''
    picos = []
    for port in list_ports.comports():
        # print("- Checking", port.device)
        if port.manufacturer != None:
            if "MicroPython" in port.manufacturer:
                picos.append(port.device)
    return picos


def get_info_pico(pico, timeout):
    '''
    Calls the find.find() function on the Pico
    and reads the unique ID that it prints
    '''
    
    # Initialize a serial connection to the device
    s = serial.Serial(pico, baudrate=115200)
    if s.isOpen()==False:
        s.open()
    
    # Interrupt running program and switch to REPL mode
    s.write(b'\x03\x03')
    s.write(b'\x02')

    # Import info.py and run the info() function which prints the ID
    s.write(b'import info\r')
    s.write(b'info.info()\r')
    
    # Receive answer (within timeout)
    text = ''
    t1 = time.time()
    while True:
        num_bytes = s.inWaiting()
        if num_bytes >0:
            c = s.read(num_bytes)
            c = c.decode('utf-8')
            text += c    
        if time.time() - t1 > timeout:
            break
    
    # Crop text to get the answer
    if 'Traceback' in text:
        info = ''
    else:    
        keyword = 'info.info()\r'
        pos1 = text.find(keyword)
        info = text[pos1 + len(keyword):]
        pos2 = info.find('\r')
        info = info[:pos2]       
        info = info.strip() 
        
    return info 


# Find all connected Picos and print their location and ID
for pico in find_picos():
    info = get_info_pico(pico, timeout=0.5)
    print (f'=> Pico found at {pico}, with unique ID: {info}')
print('')