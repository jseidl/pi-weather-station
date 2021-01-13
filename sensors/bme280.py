import bme280
import smbus2

from .core.base import SensorBase
from .const import (
    DEFAULT_SMBUS_PORT,
    DEFAULT_SMBUS_ADDR
)

class BME280Sensor(SensorBase):


    bus = None

    def __init__(self, smbus_port=DEFAULT_SMBUS_PORT, smbus_addr=DEFAULT_SMBUS_ADDR):

        # Initialize SMBus
        self.smbus_port = smbus_port
        self.smbus_addr = smbus_addr

        # Initialize BME280
        self.bus = smbus2.SMBus(self.smbus_port)
        bme280.load_calibration_params(self.bus, self.smbus_addr)

    def get_measurements(self):

        if not self.bus:
            self.logger.error("SMBus bus not open.")
            return {}

        self.logger.debug("Reading BME280")
        bme280_data = bme280.sample(self.bus, self.smbus_addr)
        self.logger.debug(f"BME200 read. Data: {bme280_data}")

        measurements = {
            'humidity': bme280_data.humidity,
            'pressure': bme280_data.pressure
            'ambient_temperature': bme280_data.temperature
        }

        return measurements
