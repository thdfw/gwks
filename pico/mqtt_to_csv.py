"""
This code reads MQTT messages on a given topic and saves them as rows in a CSV file.
Instructions: 
- Place the provided .conf file in /opt/homebrew/etc/mosquitto/, or similar
- In Terminal, run "/opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf"
- In Thonny, run the code that publishes messages to the topic
- Run this code
"""

import csv
import paho.mqtt.client as mqtt
from datetime import datetime 

# MQTT info
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "hall_sensor"

# CSV file name is topic and time
now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
csv_file = f"{mqtt_topic}_{now}.csv"

# Callback functions 
def on_connect(client, userdata, flags, rc):
    print(f"Connected and subscribed to {mqtt_topic}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, message):
    data = message.payload.decode()
    print(f"Received data: {data}")

    # Write to CSV file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data])

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever()
