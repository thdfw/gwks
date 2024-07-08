"""
This file should be placed on the Pico so that it can be identified 
by connected device(s) when running get_unique_ids.py
"""

import machine
import ubinascii

pico_unique_id = ubinascii.hexlify(machine.unique_id()).decode()

def info():
    print(pico_unique_id)