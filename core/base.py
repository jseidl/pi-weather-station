import logging

from abc import ABC, abstractmethod

from .const import (
    DEFAULT_POLLING_INTERVAL
)

class SensorBase(ABC):

    polling_interval = DEFAULT_POLLING_INTERVAL
    logger = logging.getLogger(__name__)

    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin

    @property
    def polling_interval(self):
        """ Returns polling interval in secs """
        return self._polling_interval

    @abstractmethod
    def get_measurements(self):
        """ Returns measurements """
        pass
