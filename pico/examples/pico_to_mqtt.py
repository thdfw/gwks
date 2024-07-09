"""
This code should be running on a Pico. 
It publishes messages on a given MQTT topic every 10 seconds.
"""

from umqtt.simple import MQTTClient
import network
import time

# Fill in these parameters
wifi_name = ""
wifi_password = ""
mqtt_broker = ""
mqtt_username = ""
mqtt_password = ""
mqtt_port = 1883

# Specify the client name and topic
client_name = "pico_w"
mqtt_topic = b"counting"

# Connect to WiFi
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

# Publish a messsage every 10 seconds
counter = 0
while(1):
    client.publish(mqtt_topic, str(counter))
    counter += 1
    time.sleep(10)