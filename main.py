import os
import random
import yaml
import paho.mqtt.client as mqtt
import paho.mqtt
import re
import json
import voluptuous as vol
from voluptuous import Any

from lib.garage import GarageDoor
from lib.garage import TwoSwitchGarageDoor


print("Welcome to GarageBerryPi!")
discovery_info = {}

# Update the mqtt state topic


def update_state(value, topic):
    print("State change triggered: %s -> %s" % (topic, value))

    client.publish(topic, value, retain=True)

# The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: %s" % mqtt.connack_string(rc))
    # notify subscribed clients that we are available
    client.publish(availability_topic, payload_available, retain=True)
    print(
        "Sent payload: '" +
        CONFIG['mqtt']['payload_available'] +
        "' to topic: '" +
        CONFIG['mqtt']['availability_topic'] +
        "'")
    for config in CONFIG['doors']:
        command_topic = config['command_topic']
        print("Listening for commands on %s" % command_topic)
        client.subscribe(command_topic)

# Execute the specified command for a door


def execute_command(door, command):
    try:
        doorName = door.name
    except BaseException:
        doorName = door.id
    print("Executing command %s for door %s" % (command, doorName))
    if command == "OPEN" and door.state == 'closed':
        door.open()
    elif command == "CLOSE" and door.state == 'open':
        door.close()
    elif command == "STOP":
        door.stop()
    else:
        print("Invalid command: %s" % command)

CONFIG_SCHEMA = vol.Schema(
    {
    "mqtt": vol.Schema(
        {
            vol.Required("host"): str,
            vol.Required("port"): int,
            vol.Required("user"): str,
            vol.Required("password"): str,
            vol.Optional("discovery"): Any(bool, None),
            vol.Required("discovery_prefix"): str,
            vol.Optional("availability_topic"): Any(str, None),
            vol.Optional("payload_available"): Any(str,None),
            vol.Optional("payload_not_available"): Any(str, None)


        }
    ),
    "doors": [vol.Schema(
        {
            vol.Required("id"): str,
            vol.Optional("name"): Any(str, None),
            vol.Required("relay"): int,
            vol.Required("state"): int,
            vol.Optional("open"): int, # need to verify checks
            vol.Required("state_mode"): Any(None, 'normally_closed', 'normally_open'),
            vol.Optional("invert_relay"): bool, # need to verify checks
            vol.Optional("state_topic"): str, # need to verify checks
            vol.Required("command_topic"): str
        }
    )]
    })

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.yaml'), 'r') as ymlfile:
    file_CONFIG = yaml.load(ymlfile, Loader=yaml.FullLoader)

CONFIG = CONFIG_SCHEMA(file_CONFIG)
print ("Config suceesfully validated against schema")
print(json.dumps(VALIDATED_CONFIG, indent = 4))

### SETUP MQTT ###
user = CONFIG['mqtt']['user']
password = CONFIG['mqtt']['password']
host = CONFIG['mqtt']['host']
port = int(CONFIG['mqtt']['port'])
discovery = bool(CONFIG['mqtt'].get('discovery'))

if 'discovery_prefix' not in CONFIG['mqtt']:
    discovery_prefix = 'homeassistant'
elif CONFIG['mqtt']['discovery_prefix'] is None
    discovery_prefix = 'homeassistant'
else:
    discovery_prefix = CONFIG['mqtt']['discovery_prefix']
    
#
# if availability values specified in config use them
# if not use defaults 
#
if 'availability_topic' not in CONFIG['mqtt']:
    availability_topic = discovery_prefix + '/cover' + '/availability'
elif CONFIG['mqtt']['availability_topic'] is None
    availability_topic = discovery_prefix + '/cover' + '/availability'
else:
    availability_topic = CONFIG['mqtt']['availability_topic']

if 'payload_available' not in CONFIG['mqtt']:
    payload_available = 'online'
elif CONFIG['mqtt']['payload_available'] is None
    payload_available = 'online'
else:
    payload_available = CONFIG['mqtt']['payload_available']

if 'payload_not_available' not in CONFIG['mqtt']:
    payload_not_available = 'offline'
elif CONFIG['mqtt']['payload_not_available'] is None
    payload_not_available = 'offline'
else:
    payload_not_available = CONFIG['mqtt']['payload_not_available']

# client = mqtt.Client(client_id="MQTTGarageDoor_" + binascii.b2a_hex(os.urandom(6)), clean_session=True, userdata=None, protocol=4)
client = mqtt.Client(client_id="MQTTGarageDoor_{:6s}".format(str(random.randint(
    0, 999999))), clean_session=True, userdata=None, protocol=mqtt.MQTTv311)

client.on_connect = on_connect

client.username_pw_set(user, password=password)

# set a last will message so the broker will notify connected clients when
# we are not available
client.will_set(availability_topic, payload_not_available, retain=True)
print(
    "Set last will message: '" +
    payload_not_available +
    "' for topic: '" +
    availability_topic +
    "'")

client.connect(host, port, 60)


### SETUP END ###

### MAIN LOOP ###
if __name__ == "__main__":
    # Create door objects and create callback functions
    for doorCfg in CONFIG['doors']:

        # If no name it set, then set to id
        if 'name' not doorCfg:
            doorCfg['name'] = doorCfg['id']
        elif if doorCfg['name'] is None
            doorCfg['name'] = doorCfg['id']

        # Sanitize id value for mqtt
        doorCfg['id'] = re.sub(r'\W+', '', re.sub(r'\s', ' ', doorCfg['id']))

        if discovery is True:
            base_topic = discovery_prefix + "/cover/" + doorCfg['id']
            config_topic = base_topic + "/config"
            doorCfg['command_topic'] = base_topic + "/set"
            doorCfg['state_topic'] = base_topic + "/state"

        command_topic = doorCfg['command_topic']
        state_topic = doorCfg['state_topic']
        #
        # If the open switch is specified use a two switch garage door
        # otherwise use a door with only a closed switch.
        # The interface is the same.  The two switch garage door
        # reports the states "open" and "closed"
        #
        if "open" in doorCfg:
            door = TwoSwitchGarageDoor(doorCfg)
        else:
            door = GarageDoor(doorCfg)

        # Callback per door that passes a reference to the door
        def on_message(client, userdata, msg, door=door):
            execute_command(door, msg.payload.decode("utf-8"))

        # Callback per door that passes the doors state topic
        def on_state_change(value, topic=state_topic):
            update_state(value, topic)

        client.message_callback_add(command_topic, on_message)

        # You can add additional listeners here and they will all be executed
        # when the door state changes
        door.onStateChange.addHandler(on_state_change)

        # Publish initial door state
        client.publish(state_topic, door.state, retain=True)

        # If discovery is enabled publish configuration
        if discovery is True:
            discovery_info["name"] = doorCfg['name']
            discovery_info["command_topic"] = doorCfg['command_topic']
            discovery_info["state_topic"] = doorCfg['state_topic']
            discovery_info["availability_topic"] = availability_topic
            discovery_info["payload_available"] = payload_available
            discovery_info["payload_not_available"] = payload_not_available

            client.publish(
                config_topic,
                json.dumps(discovery_info),
                retain=True)

            print(
                "Sent audodiscovery config: " +
                json.dumps(
                    discovery_info,
                    indent=4))
            print("to topic: " + config_topic)

    # Main loop
    client.loop_forever()
