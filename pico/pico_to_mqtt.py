"""
This code connects to a given wifi and MQTT broker.
It then sends a timestamp through MQTT at each pulse of the hall sensor.
Instructions: 
- Place the provided .conf file in /opt/homebrew/etc/mosquitto/, or similar
- In Terminal, run "/opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf"
- In Thonny, run this code
- Save the data to a CSV by running mqtt_to_csv.py
"""

import machine
import utime
import network
from umqtt.simple import MQTTClient
import time

# *********************************************
# MQTT connection
# *********************************************

wifi_name = "lbnl-visitor"
wifi_password = ""

mqtt_broker = "198.128.196.115"
mqtt_port = 1883
mqtt_topic = b"hall_sensor"

wifi_name = "602"
wifi_password = "F=ma1686"
mqtt_broker = "192.168.86.79"

# Connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting to wifi...")
    wlan.connect(wifi_name, wifi_password)
    while not wlan.isconnected():
        time.sleep(1)
print(f"Connected to wifi {wifi_name}")

# Connect to MQTT broker
client = MQTTClient("thomas_pico_w_client", mqtt_broker, port=mqtt_port)
client.connect()
print(f"Connected to mqtt broker {mqtt_broker}")

# *********************************************
# Flow meter
# *********************************************

HALL_PULSE_PIN = 15
timestamps = []

# Callback function to record the timestamp of each pulse
def hall_pulse_callback(pin):
    global timestamps
    timestamp = utime.time_ns()
    client.publish(mqtt_topic, str(timestamp))
    timestamps.append(timestamp)

# Set up the pin for input and attach interrupt for rising edge
hall_pulse_pin = machine.Pin(HALL_PULSE_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
hall_pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=hall_pulse_callback)

try:
    while True:
        print(f"Pulse count during last second: {len(timestamps)}")
        timestamps.clear()
        utime.sleep(1)
        
except KeyboardInterrupt:
    print("Program interrupted by user")
