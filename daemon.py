import logging
import sys

from time import sleep

from piweatherstation.sensors.bme280 import BME280Sensor
from piweatherstation.sensors.bh1750 import BH1750Sensor
from piweatherstation.sensors.ds18B20 import DS18B20Sensor
from piweatherstation.sensors.windvane import WindVaneSensor
from piweatherstation.sensors.windspeed import WindSpeedSensor
from piweatherstation.sensors.rainfall import RainfallSensor
from piweatherstation.sensors.pms5003 import PMS5003Sensor

# Variables

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Constants
E_OK = 0
E_ERROR = 255

# Configuration

READ_INTERVAL = 30

AVAILABLE_SENSORS = [
    #DS18B20Sensor,
    RainfallSensor,
    BME280Sensor,
    BH1750Sensor,
    WindSpeedSensor,
    WindVaneSensor,
    PMS5003Sensor,
]

# Functions

def run():

    sensors = []

    # Initialize all sensors
    try:
        for sensor in AVAILABLE_SENSORS:
            sensors.append(sensor())
    except Exception as e:
        LOGGER.error("Error starting sensor: %s", str(e))
        #pass
        raise e
        return E_ERROR


    workers = []

    # Dispatch workers
    for sensor in sensors:
        #worker = Process(target=sensor.loop_forever, args=(MQTT,))
        #worker.daemon = True
        sensor.start()
        workers.append(sensor)

    # Loop
    try:
        while True:
            # Join workers
            for worker in workers:
                worker.join(timeout=0.5)

    except KeyboardInterrupt:
        LOGGER.info("Shutting down weather station")
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
        pass

    return E_OK

def read_all(sensors):

    for sensor in sensors:
        try:
            LOGGER.info("Reading sensor %s...", sensor.name)
            measurement = sensor.run()
            if measurement:
                #print(sensor.name, measurement)
                LOGGER.debug("Sensor: %s, Values: %s", sensor.name, measurement)
                # Publish to MQTT
                mqtt_topic = f"{MQTT_TOPIC_BASE}/{sensor.name}"
                MQTT.publish(mqtt_topic, json.dumps(measurement))
            MQTT.loop()
        except Exception as e:
            LOGGER.error("Error getting measurement for %s: %s", sensor.name, str(e))
            #pass
            raise e

if __name__ == "__main__":
    sys.exit(run())
