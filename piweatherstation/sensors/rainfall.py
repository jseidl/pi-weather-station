from gpiozero import Button
from datetime import datetime

from piweatherstation.core.base import TickCounterSensor

BUCKET_SIZE = 0.2794

class RainfallSensor(TickCounterSensor):

    name = "rainfall"

    def setup(self):

        gpio_pin = 26

        self.reset_counters()

        self.button = Button(gpio_pin)
        self.button.when_pressed = self.register_tick

    def get_measurements(self):

        reading = float(self.ticks.value * BUCKET_SIZE)

        self.add_measurement(reading)
        self.reset_counters()

        return {
            'current': self.last(),
            'max': self.max(),
            'average': self.mean()
        }
