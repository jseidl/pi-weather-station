import bme280
import smbus2

from piweatherstation.core.base import SensorBase
from piweatherstation.const import (
    DEFAULT_SMBUS_PORT,
    DEFAULT_SMBUS_ADDR
)

class BME280Sensor(SensorBase):

    name = "ambient"
    bus = None

    def setup(self):

        # Initialize SMBus
        self.smbus_port = DEFAULT_SMBUS_PORT
        self.smbus_addr = DEFAULT_SMBUS_ADDR

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

        temp_f = (bme280_data.temperature * 9/5) + 32

        measurements = {
            'humidity': round(bme280_data.humidity, 2),
            'pressure': round(bme280_data.pressure, 2),
            'ambient_temperature': round(temp_f, 2)
        }

        return measurements
