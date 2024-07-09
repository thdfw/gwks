"""
This code should be running on a Raspberry Pi or other computer.
It receives and prints messages published on an MQTT topic.
"""

import paho.mqtt.client as mqtt

# Parameters
mqtt_broker = "localhost"
mqtt_topic = "hall_sensor"
mqtt_port = 1883

def on_connect(client, userdata, flags, rc):
    '''Connect and subscribe to the given MQTT topic'''
    print(f"Connected and subscribed to {mqtt_topic}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, message):
    '''This function is called at every received message'''
    data = message.payload.decode()
    print(f"Received: {data}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever()