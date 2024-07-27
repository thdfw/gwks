"""
commit d3808574 of https://github.com/thdfw/gwks/pico/flowmeter/hall_to_api.py
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
wifi_name = "ARRIS-3007"
wifi_password = "PASSWD"

base_url = "http://192.168.0.175:8000"

HB_FREQUENCY_S = 3
PULSE_PIN = 28
ALPHA = .1
HZ_THRESHOLD = .4

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
latest_ts = 0
exp_hz = 0
prev_published_hz = 0
publish_new = False

def pulse_callback(pin):
    """
    Callback function to record the current frequency at each tick 
    and post to /dist-flow/hz
    """
    global latest_ts
    global exp_hz
    global publish_new
    global prev_published_hz
    timestamp = utime.time_ns()
    hz = 1e9/(timestamp-latest_ts)
    exp_hz = ALPHA * hz + (1 - ALPHA) * exp_hz
    latest_ts = timestamp
    if (0 <= exp_hz  - prev_published_hz < HZ_THRESHOLD) or (0 < prev_published_hz - exp_hz < HZ_THRESHOLD):
        publish_new = True
    

pulse_pin = machine.Pin(PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_callback)

def publish_hz():
    global exp_hz
    global prev_published_hz
    global publish_new
    url = base_url + "/dist-flow/hz"
    payload = {'MicroHz': int(exp_hz * 1e6)}
    headers = {'Content-Type': 'application/json'}
    json_payload = ujson.dumps(payload)
    try:
        response = urequests.post(url, data=json_payload, headers=headers)
        response.close()
    except Exception as e:
        print(f"Error posting hz: {e}")
    gc.collect()
    publish_new = False
    prev_published_hz = exp_hz


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
    global latest_ts
    hb = (hb + 1) % 16
    hbstr = "{:x}".format(hb)
    payload =  {'MyHex': hbstr, 'TypeName': 'hb', 'Version': '000'}
    headers = {'Content-Type': 'application/json'}
    json_payload = ujson.dumps(payload)
    url = base_url + "/dist-flow/hb"
    timestamp = utime.time_ns()
    if (timestamp - latest_ts) / 10**9 > HB_FREQUENCY_S:
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
        utime.sleep(.2)
        if publish_new:
            publish_hz()
except KeyboardInterrupt:
    print("Program interrupted by user")
