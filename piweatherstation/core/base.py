import logging
import json
import statistics

from abc import ABC, abstractmethod
from time import sleep
from datetime import datetime

from multiprocessing import Process, Value, Manager

from piweatherstation.core.mqtt import MQTTClient
from piweatherstation.util.statistics import iqr, std_dev
from piweatherstation.const import (
    SENSOR_DEFAULT_UPDATE_INTERVAL,
    MEASUREMENTS_DEFAULT_POOL_SIZE,
    MEASUREMENTS_RETRY_MAX,
    MEASUREMENTS_RETRY_INTERVAL,
    MQTT_TOPIC_BASE,
    MQTT_WILL_TOPIC,
)

from piweatherstation.settings import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD
)
class SensorBase(Process):

    _update_interval = SENSOR_DEFAULT_UPDATE_INTERVAL
    last_run = None
    _pool_size = MEASUREMENTS_DEFAULT_POOL_SIZE

    logger = logging.getLogger(__name__)
    name = __name__

    def __init__(self):

        Process.__init__(self)

        # Connect to MQTT
        MQTT = MQTTClient()
        try:
            MQTT.connect(
                MQTT_HOST,
                username=MQTT_USERNAME,
                password=MQTT_PASSWORD,
                will_topic=MQTT_WILL_TOPIC
                )
            self.logger.info("Connected to MQTT server.")
        except Exception as e:
            self.logger.OGGER.error("Error connecting to MQTT server: %s", str(e))
            return E_ERROR

        self.mqtt_client = MQTT
        self._reset_sensor()
        self.setup()

    def setup(self):
        pass

    def run(self):
        while True:
            
            measurement = self.execute()

            if not measurement:
                continue

            self.logger.debug("Sensor: %s, Values: %s", self.name, measurement)
            # Publish to MQTT
            mqtt_topic = f"{MQTT_TOPIC_BASE}/{self.name}"
            self.mqtt_client.publish(mqtt_topic, json.dumps(measurement))

            # Loop
            self.mqtt_client.loop()

    def execute(self):

        current_timestamp = datetime.now()

        if self.last_run:
            time_diff = (current_timestamp-self.last_run).total_seconds()
            if time_diff < self.update_interval:
                self.logger.debug("Waiting for %d seconds since last run (%d)", self.update_interval, time_diff)
                return None

        self.last_run = datetime.now()

        return self.get_measurements()

    def _reset_sensor(self):
        self.measurements = list() #Array('d', self._pool_size)

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

    def filtered_measurements(self, method=iqr):
        if not method:
            return self.measurements

        return method(self.measurements)

    def last(self):
        return round(self.measurements[-1], 2)

    def max(self):

        filtered_measurements = self.filtered_measurements()

        if not filtered_measurements:
            if not self.measurements:
                return 0.0
            return self.last()

        return round(max(filtered_measurements), 2)

    def mean(self, method=iqr):

        filtered_measurements = self.filtered_measurements(method=method)

        if not filtered_measurements:
            if not self.measurements:
                return 0.0
            return self.last()

        if len(filtered_measurements) > 1:
            return round(statistics.mean(filtered_measurements), 2)

        return self.last()

class TickCounterSensor(SensorBase):

    _update_interval = 15

    ticks = Value('i')
    timestamp = None

    def __init__(self, ):
        super().__init__()
        self.ticks = Value('i')
        self.reset_counters()

    def register_tick(self):
        self.ticks.value += 1
        self.logger.debug(f"Tick registered. Total ticks: {self.ticks.value}")

    def reset_counters(self):
        self.ticks.value = 0
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

        self.logger.error(f"Max retry attempts '{self.max_retries} reached with no valid data")
        return None
