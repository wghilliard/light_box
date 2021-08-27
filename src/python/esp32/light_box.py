from machine import Pin
from neopixel import NeoPixel

from constants import DISPLAY_PIN, DISPLAY_SIZE, LIGHT_BOX_SIZE, LIGHT_BOX_PIN


class LightBox:
    def __init__(self, driver, size):
        self.driver = driver
        self.size = size

    @classmethod
    def from_config(cls, config):
        if config.get("local_debug", False) is True:
            light_box_pin = Pin(DISPLAY_PIN, Pin.OUT)
            light_box_driver = NeoPixel(light_box_pin, DISPLAY_SIZE)
            light_box_size = DISPLAY_SIZE
        else:
            light_box_pin = Pin(LIGHT_BOX_PIN, Pin.OUT)
            light_box_driver = NeoPixel(light_box_pin, LIGHT_BOX_SIZE)
            light_box_size = LIGHT_BOX_SIZE

        return LightBox(light_box_driver, light_box_size)

    def __len__(self):
        return self.size

    def __setitem__(self, key, value):
        self.driver[key] = value

    def __getitem__(self, item):
        return self.driver[item]

    def write(self):
        self.driver.write()

    def reset(self):
        self.driver.fill((0, 0, 0))

    def wreset(self):
        self.driver.fill((0, 0, 0))
        self.write()

    def fill(self, color):
        return self.driver.fill(color)

    def __setslice__(self, i, j, sequence):
        self.driver[i:j] = sequence
