"""
commit XXXXXX of https://github.com/thdfw/gwks/pico/flowmeter/hall_to_api.py
This code looks for a rest API over wifi

Instructions: run ./start_api.sh from https://github.com/thegridelectric/starter-scripts/tree/jm/nodename
on a pi whose ip address is base_url below

"""
import gc
import time

import machine
import network
import ubinascii
import ujson
import urequests
import utime

# *********************************************
# PARAMETERS
# *********************************************
wifi_name = "SSID"
wifi_password = "PASS"

base_url = "http://192.168.0.165:8000"

HB_FREQUENCY_S = 3
PULSE_PIN = 28
DEADMAND_MILLISECONDS = 10


# Connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting to wifi...")
    wlan.connect(wifi_name, wifi_password)
    while not wlan.isconnected():
        time.sleep(1)
print(f"Connected to wifi {wifi_name}")


# *********************************************
# Catch pulses
# *********************************************
latest = 0

def pulse_callback(pin):
    """
    Callback function to record the current frequency at each tick 
    and post to /dist-flow/hz
    """
    global latest
    timestamp = utime.time_ns()
    if timestamp - latest > 1_000_000 * DEADMAND_MILLISECONDS:
        frequency = int(1/(timestamp-latest)*1e9 * 1e6)
        latest = timestamp
        url = base_url + "/dist-flow/hz"
        payload = {'MicroHz': frequency}
        headers = {'Content-Type': 'application/json'}
        json_payload = ujson.dumps(payload)
        try:
            response = urequests.post(url, data=json_payload, headers=headers)
            response.close()
        except Exception as e:
            print(f"Error posting tick: {e}")
        gc.collect()


pulse_pin = machine.Pin(PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
pulse_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=pulse_callback)



# *********************************************
# Publish Heartbeat
# *********************************************
hb = 0

def publish_heartbeat(timer):
    """
    Publish a heartbeat, assuming no omega tick in the last 5 minutes.
    Acts as a keepalive
    """
    global hb
    global latest
    hb = (hb + 1) % 16
    hbstr = "{:x}".format(hb)
    payload =  {'MyHex': hbstr, 'TypeName': 'hb', 'Version': '000'}
    headers = {'Content-Type': 'application/json'}
    json_payload = ujson.dumps(payload)
    url = base_url + "/dist-flow/hb"
    try:
        response = urequests.post(url, data=json_payload, headers=headers)
        response.close()
    except Exception as e:
        print(f"Error posting hb: {e}")
    gc.collect()

# Create a timer to publish heartbeat every 3 seconds
heartbeat_timer = machine.Timer(-1)
heartbeat_timer.init(period=3000, mode=machine.Timer.PERIODIC, callback=publish_heartbeat)

try:
    while True:
        utime.sleep(5)
except KeyboardInterrupt:
    print("Program interrupted by user")