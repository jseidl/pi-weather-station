import math
import statistics

from gpiozero import Button
from datetime import datetime

from .core.base import SensorBase

ANEMOMETER_RADIUS = 9.0 # CM
SECONDS_IN_AN_HOUR = 3600
CMS_IN_A_KM = 100000.0
CMS_IN_A_METER = 1000.0
CMS_IN_A_MILE = 160934.0
ADJUSTMENT_FACTOR = 1.8

MEASUREMENTS_POOL_SIZE = 20

class AnemometerSensor(SensorBase):

    def __init__(self, gpio_pin):

        self.reset_counters(
                
        self.measurements = [0] * MEASUREMENTS_POOL_SIZE)

        self.button = Button(gpio_pin)
        self.button.when_pressed = self.register_tick

    def register_tick(self):
        self.ticks += 1
        self.logger.debug(f"Tick registered. Total ticks: {self.ticks}")

    def reset_counters(self):
        self.ticks = 0
        self.timestamp = datetime.utcnow()

    def add_measurement(self, measurement):

        # Makeshift circular buffer
        self.measurements.pop(0)
        self.measurements.append(measurement)

    def get_measurements(self):

        time_now = datetime.utcnow()

        measurement_duration = (time_now - self.timestamp).TotalSeconds

        circumference_cm = (2 * math.pi) * ANEMOMETER_RADIUS
        rotations = self.ticks / 2.0
        
        distance_cm = circumference_cm * rotations        
        speed_cm_per_sec = distance_cm / measurement_duration

        # distance_m = (distance_cm / CMS_IN_A_METER)
        # speed_m_per_sec = distance_m / measurement_duration

        # distance_km = (distance_cm / CMS_IN_A_KM)
        # speed_km_per_sec = distance_km / measurement_duration
        # speed_km_per_hour = speed_km_per_sec * SECONDS_IN_AN_HOUR 
        
        distance_mi = (distance_cm / CMS_IN_A_MILE)        
        speed_mi_per_sec = distance_mi / measurement_duration
        speed_mi_per_hour = speed_mi_per_sec * SECONDS_IN_AN_HOUR

        measurement = speed_mi_per_hour * ADJUSTMENT_FACTOR,

        self.add_measurement(measurement)
        self.reset_counters()

        return {
            'current': measurement,
            'gust': max(self.measurements),
            'average': statistics.mean(self.measurements)
        }
