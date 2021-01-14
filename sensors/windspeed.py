import math
from gpiozero import MCP3008

from .core.base import RetryableSensor
from .const import (
    BOARD_VREF,
    MEASUREMENTS_RETRY_MAX,
    MEASUREMENTS_RETRY_INTERVAL,
)

VOLT_ANGLE_MAP = {
    0.4: 0.0,
    1.4: 22.5,
    1.2: 45.0,
    2.8: 67.5,
    2.7: 90.0,
    2.9: 112.5,
    2.2: 135.0,
    2.5: 157.5,
    1.8: 180.0,
    2.0: 202.5,
    0.7: 225.0,
    0.8: 247.5,
    0.1: 270.0,
    0.3: 292.5,
    0.2: 315.0,
    0.6: 337.5,
}

class WindSpeedSensor(RetryableSensor):

    name = "windspeed"

    def __init__(self, adc_channel=0):

        self.adc = MCP3008(channel=0)

    def _read_sensor(self):

        wind_angle = round(self.adc.value * BOARD_VREF, 1)

        if wind_angle not in VOLT_ANGLE_MAP.keys():
            return None

        return wind_angle

    def mean(self):

        sin_sum = 0.0
        cos_sum = 0.0
        average = 0.0

        for angle in self.measurements:
            r = math.radians(angle)
            sin_sum += math.sin(r)
            cos_sum += math.cos(r)

        total_measurements = float(len(self.measurements))

        s = sin_sum / total_measurements
        c = cos_sum / total_measurements
        arc = math.degrees(math.atan(s / c))
        
        if s > 0 and c > 0:
            average = arc
        elif c < 0:
            average = arc + 180
        elif s < 0 and c > 0:
            average = arc + 360

        return 0.0 if average == 360 else average

    def get_measurements(self):

        reading = self._retryable_read()
        wind_angle = VOLT_ANGLE_MAP[reading]
        self.add_measurement(wind_angle)

        return {
            'current': wind_angle,
            'average': self.mean()
        }