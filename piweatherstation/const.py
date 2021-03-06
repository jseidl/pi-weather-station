BOARD_VREF = 3.3

SENSOR_DEFAULT_UPDATE_INTERVAL = 30

# SMBus
DEFAULT_SMBUS_PORT = 1
DEFAULT_SMBUS_ADDR = 0x76

# 1-Wire
ONEWIRE_BASEDIR = '/sys/bus/w1/devices/'

# Measurements Retry
MEASUREMENTS_RETRY_MAX = 5
MEASUREMENTS_RETRY_INTERVAL = 0.25

# Measurements pool
MEASUREMENTS_DEFAULT_POOL_SIZE = 20

# MQTT 
MQTT_TOPIC_BASE = "weatherstation/sensors"
MQTT_WILL_TOPIC = f"weatherstation/status"
