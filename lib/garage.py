import time
import RPi.GPIO as GPIO
from eventhook import EventHook


SHORT_WAIT = .2 #S (200ms)
"""
    The purpose of this class is to map the idea of a garage door to the pinouts on 
    the raspberrypi. It provides methods to control the garage door and also provides
    and event hook to notify you of the state change. It also doesn't maintain any
    state internally but rather relies directly on reading the pin.
"""
class GarageDoor(object):
    
    def __init__(self, config):

        # Config
        self.relay_pin = config['relay']
        self.state_pin = config['state']
        self.id = config['id']
        self.mode = int(config.get('state_mode') == 'normally_closed')
        self.invert_relay = bool(config.get('invert_relay'))

        # Setup
        self._state = None
        self.onStateChange = EventHook()

        # Set relay pin to output, state pin to input, and add a change listener to the state pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.setup(self.state_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.state_pin, GPIO.BOTH, callback=self.__stateChanged, bouncetime=300)


        # Set default relay state to false (off)
        GPIO.output(self.relay_pin, self.invert_relay)

    # Release rpi resources
    def __del__(self):
        GPIO.cleanup()

    # These methods all just mimick the button press, they dont differ other than that
    # but for api sake I'll create three methods. Also later we may want to react to state
    # changes or do things differently depending on the intended action

    def open(self):
        if self.state == 'closed':
            self.__press()

    def close(self):
        if self.state == 'open':
            self.__press()

    def stop(self):
        self.__press()

    # State is a read only property that actually gets its value from the pin
    @property
    def state(self):
        # Read the mode from the config. Then compare the mode to the current state. IE. If the circuit is normally closed and the state is 1 then the circuit is closed.
        # and vice versa for normally open
        state = GPIO.input(self.state_pin)
        if  state == self.mode:
            return 'closed'
        else:
            return 'open'

    # Mimick a button press by switching the GPIO pin on and off quickly
    def __press(self):
        GPIO.output(self.relay_pin, not self.invert_relay)
        time.sleep(SHORT_WAIT)
        GPIO.output(self.relay_pin, self.invert_relay)

   
    # Provide an event for when the state pin changes
    def __stateChanged(self, channel):
        if channel == self.state_pin:
            # Had some issues getting an accurate value so we are going to wait for a short timeout
            # after a statechange and then grab the state
            time.sleep(SHORT_WAIT)
            self.onStateChange.fire(self.state)

