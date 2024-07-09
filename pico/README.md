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

# :mailbox_with_mail: Sending and receiving messages with MQTT

## Sending messages (Pico -> Raspberry Pi) 

### Start a MQTT broker on the Raspberry Pi

- If necessary, install Mosquitto on the device
- If necessary, edit the configuration file `mosquitto.conf`, generally located in /etc/mosquitto/
- Run mosquitto with the configuration file: `mosquitto -c path/to/mosquitto.conf`

### Connect the Pico to the WiFi and MQTT broker, and publish messages

Open `examples/pico_to_mqtt.py` or any other file destined to publish MQTT messages from the Pico, and follow these steps:
- Fill in the parameters: `wifi_name`, `wifi_password`, `mqtt_broker` (the local IP address of the device on which the MQTT broker is running, i.e. the Raspberry Pi), `mqtt_username`, and `mqtt_password` (if there is a username and password)
- Specify the topic on which the messages should be published (`mqtt_topic`) as well as the Pico's client name (`client_name`)
- Save the file on the Pico and run it - if you want it to run automatically as soon as the Pico is connected to power, save it as `main.py`

## Receiving messages (Raspberry Pi <- Pico)

On the Raspberry Pi, run `examples/mqtt_to_pi.py` or any other file destined to receive MQTT messages from the Pico. Edit the `mqtt_broker` and `mqtt_topic` variables if necessary.