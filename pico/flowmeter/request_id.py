'''
Run this code on the Pi to find the unique ID of the Pico(s) 
that are subscribed to a given MQTT topic
'''

import paho.mqtt.client as mqtt
import sys

mqtt_broker = "localhost"
mqtt_port = 1883

client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port)

mqtt_topic = str(input("MQTT topic (e.g. 'hall_sensor'): "))

def on_connect(client, userdata, flags, rc):
    client.subscribe(mqtt_topic)

def on_message(client, userdata, message):
    data = message.payload.decode()
    if 'Pico unique ID' in data:
        print(data)
        sys.exit()

client.publish(mqtt_topic, "Request for unique_id")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever()