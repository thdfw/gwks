# :gift: Setting up a new Pico

## Finding the Pico's unique identifier

In `identifcation/`, the `info.py` and `get_unique_ids.py` codes are provided. Save `info.py` on the Pico.
- Either run `info.py` directly on the Pico (in Thonny)
- Or physically connect the Pico to a device and run `get_unique_ids.py` on that device

## Installing necessary libraries

Install the `umqtt.simple` package on the Pico:
- Plug in the Pico to a computer
- In Thonny, go to Tools / Manage Packages...
- Search for `umqtt.simple` and install the package

# :mailbox_with_mail: Sending and receiving messages with MQTT

## Start a MQTT broker 

- If necessary, install Mosquitto on the device
- If necessary\*, edit the configuration file `mosquitto.conf` (generally located in `/etc/mosquitto/`)
- Start mosquitto (with the configuration file): `mosquitto` (`mosquitto -c path/to/mosquitto.conf`)
- If you encounter "Error: Address already in use" and are using Mosquitto>=2.0, run `sudo systemctl stop mosquitto.service` and try again.

\*When using Mosquitto>=2.0, running `mosquitto` will only allow for connections from clients running on this machine. Make sure to uncommment/add the following lines to the configuration file and start mosquitto with the configuration file to allow remote access.
```
allow_anonymous true
listener 1883 0.0.0.0
```

The terminal should be displaying something like this:
```
1720491672: mosquitto version 2.0.11 starting
1720491672: Config loaded from /etc/mosquitto/mosquitto.conf.
1720491672: Opening ipv4 listen socket on port 1883.
1720491672: mosquitto version 2.0.11 running
```
## Connect the Pico to the MQTT broker and publish messages

Open `examples/pico_to_mqtt.py` or any other file destined to publish MQTT messages from the Pico, and follow these steps:
- Fill in the parameters: `wifi_name`, `wifi_password`, `mqtt_broker` (the local IP address of the device on which the MQTT broker is running, i.e. the Raspberry Pi), `mqtt_username`, and `mqtt_password` (if there is a username and password)
- Specify the topic on which the messages should be published (`mqtt_topic`) as well as the Pico's client name (`client_name`)
- Save the file on the Pico and run it - if you want it to run automatically as soon as the Pico is connected to power, save it as `main.py`

A new connection should appear in the MQTT broker's terminal window as soon as the code starts running.

## Receiving messages

On the Raspberry Pi, in a new terminal window, run `examples/mqtt_to_pi.py` or any other file destined to receive MQTT messages from the Pico. Edit the `mqtt_broker` and `mqtt_topic` variables if necessary. This new connection should show up in the first terminal window.