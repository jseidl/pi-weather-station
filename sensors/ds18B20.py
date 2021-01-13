import glob

from time import sleep

from .core.base import SensorBase
from .const import (
    ONEWIRE_BASEDIR,
    MEASUREMENTS_RETRY_MAX,
    MEASUREMENTS_RETRY_INTERVAL,
)

DEVICE_FOLDER = glob.glob(ONEWIRE_BASEDIR + '28*')[0]
DEVICE_FILE = f"{DEVICE_FOLDER}/w1_slave"

class DS18B20Sensor(SensorBase):

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

    def _read_temperature(self):

        retry_count = 0

        while retry_count <= MEASUREMENTS_RETRY_MAX:

            reading = self._read_sensor()

            if reading:
                return reading

            retry_count += 1
            self.logger.info(f"Sensor not ready, retrying in {MEASUREMENTS_RETRY_INTERVAL} ({retry_count}/{MEASUREMENTS_RETRY_MAX})")
            sleep(MEASUREMENTS_RETRY_INTERVAL)

        self.loger.error(f"Max retry attempts '{MEASUREMENTS_RETRY_MAX} reached with no valid data")
        return None

    def get_measurements(self):

        reading = self._read_temperature()

        if not reading:
            return {}

        temp_c = reading / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0

        return {
            'centigrades': temp_c,
            'fahrenheit': temp_f
        }


