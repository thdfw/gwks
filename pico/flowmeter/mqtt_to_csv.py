"""
This code reads MQTT messages on the topics 'hall_sensor' and 'ekm_sensor'
and saves them as timestamped rows in a CSV file in /home/pi/mqtt_files/

Instructions: 
- If using mosquitto 2.0, place the provided .conf file in /etc/mosquitto/, or similar
- In Terminal, run "mosquitto -c /etc/mosquitto/mosquitto.conf"
- Run pico_to_mqtt.py on the Pico W (either call it main.py or through Thonny)
- Run this code to save the data to CSV files live
"""

import csv
import paho.mqtt.client as mqtt
from datetime import datetime 
import time

# *********************************************
# PARAMETERS
# *********************************************

mqtt_broker = "localhost"
mqtt_port = 1883
hall_mqtt_topic = "hall_sensor"
ekm_mqtt_topic = "ekm_sensor"

# Directory to save the CSV files
directory = '/home/pi/mqtt_files/'

# *********************************************
# Writing received MQTT messages to a CSV file
# *********************************************

now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def on_connect(client, userdata, flags, rc):
    '''Connect and subscribes to the MQTT topics'''
    client.subscribe(hall_mqtt_topic)
    print(f"Connected and subscribed to {hall_mqtt_topic}")
    client.subscribe(ekm_mqtt_topic)
    print(f"Connected and subscribed to {ekm_mqtt_topic}")

def on_message(client, userdata, message):
    '''Writes the data received on the MQTT topics to distinct CSV files'''
    data = message.payload.decode()
    topic = message.topic
    csv_file = directory + f"{topic}_{now}.csv"
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time.time(), data])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever()