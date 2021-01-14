from gpiozero import Button
from datetime import datetime

from .core.base import TickCounterSensor

BUCKET_SIZE = 0.2794

class RainfallSensor(TickCounterSensor):

    def __init__(self, gpio_pin):

        self.reset_counters()

        self.button = Button(gpio_pin)
        self.button.when_pressed = self.register_tick

    def get_measurements(self):

        reading = self.ticks

        self.add_measurement(reading)
        self.reset_counters()

        return {
            'current': reading,
            'max': self.max(),
            'average': self.mean()
        }