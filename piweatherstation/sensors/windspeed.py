import math

from gpiozero import Button
from datetime import datetime

from piweatherstation.core.base import TickCounterSensor

# REMOVEME
from piweatherstation.util.statistics import iqr, std_dev

ANEMOMETER_RADIUS = 9.0 # CM
SECONDS_IN_AN_HOUR = 3600
CMS_IN_A_KM = 100000.0
CMS_IN_A_METER = 1000.0
CMS_IN_A_MILE = 160934.0
ADJUSTMENT_FACTOR = 1.8

class WindSpeedSensor(TickCounterSensor):

    name = "windspeed"
    _update_interval = 15

    def setup(self):

        gpio_pin = 20

        self.reset_counters()

        self.button = Button(gpio_pin)
        self.button.when_pressed = self.register_tick

    def get_measurements(self):

        time_now = datetime.utcnow()

        measurement_duration = (time_now - self.timestamp).total_seconds()

        circumference_cm = (2 * math.pi) * ANEMOMETER_RADIUS
        rotations = self.ticks.value / 2.0
        
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

        measurement = speed_mi_per_hour * ADJUSTMENT_FACTOR

        self.add_measurement(measurement)
        self.reset_counters()

        return {
            'current': self.last(),
            'max': self.max(),
            'average': self.mean(),
            # Debug stuff
            'raw_samples': self.filtered_measurements(method=None),
            'average_raw': self.mean(method=None),
            'iqr_samples': self.filtered_measurements(method=iqr),
            'iqr_mean': self.mean(method=iqr),
            'stddev_samples': self.filtered_measurements(method=std_dev),
            'stddev_mean': self.mean(method=std_dev),
        }
