"""
This code connects to a given wifi and MQTT broker.
It then sends a timestamp through MQTT at each pulse of the hall sensor.
Instructions: 
- If using mosquitto 2.0, place the provided .conf file in /etc/mosquitto/, or similar
- In Terminal, run "mosquitto -c /etc/mosquitto/mosquitto.conf"
- Run this code on the Pico W (either call it main.py or through Thonny)
- Save the data to a CSV file live by running mqtt_to_csv.py
"""

import machine
import utime
import network
from umqtt.simple import MQTTClient
import time

# *********************************************
# PARAMETERS
# *********************************************

wifi_name = "lbnl-visitor"
wifi_password = ""

mqtt_broker = "198.128.196.115"
mqtt_username = ""
mqtt_password = ""

mqtt_port = 1883
mqtt_topic = b"hall_sensor"

client_name = "pico_w"

HALL_PULSE_PIN = 28

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

# Connect to MQTT broker
client = MQTTClient(client_name, mqtt_broker, user=mqtt_username, password=mqtt_password, port=mqtt_port)
client.connect()
print(f"Connected to mqtt broker {mqtt_broker} as client {client_name}")

# *********************************************
# Reading timestamps
# *********************************************

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
