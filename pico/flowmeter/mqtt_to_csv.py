"""
This code reads MQTT messages on a given topic and saves them as rows in a CSV file.
Instructions: 
- If using mosquitto 2.0, place the provided .conf file in /etc/mosquitto/, or similar
- In Terminal, run "mosquitto -c /etc/mosquitto/mosquitto.conf"
- Run pico_to_mqtt.py on the Pico W (either call it main.py or through Thonny)
- Run this code to save the data to a CSV file live
"""

import csv
import paho.mqtt.client as mqtt
from datetime import datetime 
import os 

# *********************************************
# PARAMETERS
# *********************************************

mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "hall_sensor"

# Directory to save the CSV files
directory = os.getcwd() + '/mqtt_files/'

# *********************************************
# Writing received MQTT messages to a CSV file
# *********************************************

now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
csv_file = directory + f"{mqtt_topic}_{now}.csv"

def on_connect(client, userdata, flags, rc):
    '''Connect and subscribes to the given MQTT topic'''
    print(f"Connected and subscribed to {mqtt_topic}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, message):
    '''Writes the data received on the MQTT topic to the CSV'''
    data = message.payload.decode()
    print(f"Received data: {data}")
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever()