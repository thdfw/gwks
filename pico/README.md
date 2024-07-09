# :gift: Setting up a new Pico

## Installing necessary libraries

Install the `umqtt.simple` package on the Pico:
- Plug in the Pico to a computer
- In Thonny, go to Tools / Manage Packages...
- Search for `umqtt.simple` and install the package

## Finding the Pico's unique identifier

In `identifcation/`, the `info.py` and `get_unique_ids.py` codes are provided. Save `info.py` on the Pico.
- Either run `info.py` directly on the Pico (in Thonny)
- Or physically connect the Pico to a device and run `get_unique_ids.py` on that device

# :outbox_tray: Sending messages through MQTT (Pico -> Raspberry Pi) 

## Start a MQTT broker on the Raspberry Pi

- If necessary, install Mosquitto on the device
- Edit the configuration file `mosquitto.conf`, generally located in /etc/mosquitto/
- Run mosquitto with the configuration file: `mosquitto -c path/to/mosquitto.conf`

## Connect the Pico to the WiFi and MQTT broker, and publish messages

Open `examples/pico_to_mqtt.py` or any other file destined to publish MQTT messages from the Pico, and follow these three steps:
- Save the file on the Pico. If you want it to run automatically as soon as the Pico is connected to power, save it as `main.py`.
- Fill in the parameters: `wifi_name`, `wifi_password`, `mqtt_broker` (the local IP address of the device on which the MQTT broker is running, i.e. the Raspberry Pi), `mqtt_username`, and `mqtt_password` (if there is a username and password)
- Specify the topic on which the messages should be published (`mqtt_topic`) as well as the Pico's client name (`client_name`)

# :inbox_tray: Receiving the Pico's messages sent through MQTT

## Testing


mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "hall_sensor"

def on_connect(client, userdata, flags, rc):
    '''Connect and subscribes to the given MQTT topic'''
    print(f"Connected and subscribed to {mqtt_topic}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, message):
    '''This function is called at every received message'''
    data = message.payload.decode()
    print(f"Received data: {data}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever()