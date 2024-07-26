"""
commit XXXXXXof https://github.com/thdfw/gwks/pico/flowmeter/primary_to_api.py
This code looks for a rest API over wifi

Instructions: run ./start_api.sh from https://github.com/thegridelectric/starter-scripts/tree/jm/nodename
on a pi whose ip address is base_url below

"""
import urequests
import ujson
import machine
import utime
import network
import time
import ubinascii


base_url = "http://192.168.0.165:8000"
node_name = "primary-flow"
HB_FREQUENCY_S = 3


wifi_name = "OurKatahdin"
wifi_password = "classyraven882"

# Address for beech2 in somerset
base_url = "http://192.168.0.165:8000"

pico_unique_id = ubinascii.hexlify(machine.unique_id()).decode()


PULSE_PIN = 28


# *********************************************
# Connecting to WiFi and MQTT broker
# *********************************************

# Connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting to wifi...")
    wlan.connect(wifi_name, wifi_password)
    while not wlan.isconnected():
        time.sleep(1)
print(f"Connected to wifi {wifi_name}")


# Publish a first timestamp
url = base_url + "/primary-flow/tick"
payload = {'timestamp_ns': utime.time_ns()}
headers = {'Content-Type': 'application/json'}
json_payload = ujson.dumps(payload)
response = urequests.post(url, data=json_payload, headers=headers)


