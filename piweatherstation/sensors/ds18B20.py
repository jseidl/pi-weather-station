import glob

from piweatherstation.core.base import RetryableSensor
from piweatherstation.const import (
    ONEWIRE_BASEDIR,
)

DEVICE_FOLDER = glob.glob(ONEWIRE_BASEDIR + '28*')[0]
DEVICE_FILE = f"{DEVICE_FOLDER}/w1_slave"

class DS18B20Sensor(RetryableSensor):

    name = "soil_temperature"

    def _read_sensor(self):
        with open(DEVICE_FILE, 'r') as f:
            lines = f.readlines()

        if "YES" not in lines[0]:
            self.logger.info("Data not ready yet.")
            return None
        
        if "t=" not in lines[1]:
            self.logger.warn("Reading not present on file.")
            return None

        reading = lines[1].split('=')[1]

        return float(reading)

    def get_measurements(self):

        reading = self._retryable_read()

        if not reading:
            return {}

        temp_c = reading / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0

        return {
            'centigrades': temp_c,
            'fahrenheit': temp_f
        }


