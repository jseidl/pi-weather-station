import logging
import statistics

from abc import ABC, abstractmethod
from time import sleep
from datetime import datetime

from .const import (
    SENSOR_DEFAULT_UPDATE_INTERVAL,
    MEASUREMENTS_DEFAULT_POOL_SIZE,
    MEASUREMENTS_RETRY_MAX,
    MEASUREMENTS_RETRY_INTERVAL,
)

class SensorBase(ABC):

    _update_interval = SENSOR_DEFAULT_UPDATE_INTERVAL
    _pool_size = MEASUREMENTS_DEFAULT_POOL_SIZE

    logger = logging.getLogger(__name__)
    measurements = []
    name = __name__

    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin

    @property
    def update_interval(self):
        """ Returns polling interval in secs """
        return self._update_interval

    @abstractmethod
    def get_measurements(self):
        """ Returns measurements """
        pass

    def add_measurement(self, measurement):

        # Makeshift circular buffer
        self.measurements.append(measurement)

        if len(self.measurements) >= self._pool_size:
            self.measurements.pop(0)

    def max(self):
        return max(self.measurements)

    def mean(self):
        return statistics.mean(self.measurements)

class TickCounterSensor(SensorBase):

    ticks = 0
    timestamp = None

    def register_tick(self):
        self.ticks += 1
        self.logger.debug(f"Tick registered. Total ticks: {self.ticks}")

    def reset_counters(self):
        self.ticks = 0
        self.timestamp = datetime.utcnow()

class RetryableSensor(SensorBase):

    max_retries = MEASUREMENTS_RETRY_MAX
    retry_count = 0

    @abstractmethod
    def _read_sensor(self):
        """ Reads the sensor, might fail """
        pass

    def _retryable_read(self):

        self.retry_count = 0

        while self.retry_count <= self.max_retries:

            reading = self._read_sensor()

            if reading:
                return reading

            self.retry_count += 1
            self.logger.info(f"Sensor not ready, retrying in {self.max_retries} ({self.retry_count}/{self.max_retries})")
            sleep(self.max_retries)

        self.loger.error(f"Max retry attempts '{self.max_retries} reached with no valid data")
        return None