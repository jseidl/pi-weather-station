import logging
import paho.mqtt.client as mqtt

from abc import ABC, abstractmethod

class MQTTClient(ABC):

    client = None
    qos = 1
    will_topic = None

    logger = logging.getLogger(__name__)

    def __init__(self):

        self.client = mqtt.Client()
        self.will_topic = None

    def connect(self, host, port=1883, username=None, password=None, keepalive=60, will_topic="status"):

        if username:
            self.client.username_pw_set(username, password)

        self.client.connect(host, port, keepalive)
        self.client.loop_misc()

        # Set MQTT LWT
        self.set_will(will_topic)

        # Publish state
        self.publish(will_topic, "online")

    def set_will(self, topic, qos=1, retain=True):

        self.will_topic = topic
        self.client.will_set(self.will_topic, "offline", qos, retain)

    def publish(self, topic, value):

        self.logger.info("Publishing MQTT message to topic '%s': %s", topic, value)
        self.client.publish(topic, value, qos=self.qos)
        self.client.loop_write()

    def loop(self):

        # Publish online every loop so HA doesn't forgets about him
        self.publish(self.will_topic, "online")

        # MQTT Loop
        self.client.loop(timeout=1.0)
