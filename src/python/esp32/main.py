import time

import network
import json
from machine import Pin
from neopixel import NeoPixel

import usocketio.client

from show import glow, solid, test
from light_box import LightBox
from constants import (
    LIGHT_BOX_SIZE, MAIN_LOADED_LED,
    NETWORK_LED,
    RED,
    SHOW_STATUS_LED,
    WS_COUNTER_LED,
    WS_TEST_LED,
    YELLOW,
    BLUE,
    GREEN,
    sprint,
    DISPLAY_WIDTH,
    OFF,
)

print("[system] imports loaded")


def do_connect(display_func, secrets):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    retry = 5

    def off():
        for l_led_index in range(DISPLAY_WIDTH + 1):
            display_func(l_led_index * NETWORK_LED, OFF)

    off()
    if not wlan.isconnected():
        sprint("connecting to network...")
        wlan.connect(secrets["ssid"], secrets["password"])
        while not wlan.isconnected() and retry > 0:
            # turn all network lights off
            off()

            # turn on the corresponding try lights, range doesn't allow for 0 start when iterating, so +1
            for led_mult in range((retry % DISPLAY_WIDTH) + 1):
                # if NETWORK_LED == 5, and DISPLAY_WIDTH = 3, then 5, 10, 15 will be turned on
                display_func(led_mult * NETWORK_LED, YELLOW)

            time.sleep(1)
            retry -= 1
    sprint(
        "network config:" + ",".join(wlan.ifconfig()) + "retries left: " + str(retry)
    )

    off()
    return wlan.isconnected()


def get_secrets():
    with open("/secrets.json") as handle:
        return json.loads(handle.read())


def get_config():
    with open("/config.json") as handle:
        return json.loads(handle.read())


class Client:
    def __init__(self):
        pass


def ws_loop(config, light_box, display_func):
    # def update(count):
    #     if int(time.time()) % 2 == 0:
    #         sprint("count=" + str(count))
    #         display_func(WS_TEST, (count, 0, 10))

    sprint("connecting to control server @ " + config["server_address"] + "...")
    with usocketio.client.connect(
        "http://" + config["server_address"], config["namespace"], 10
    ) as sio:
        state = {"count": 0}

        def count_color():
            if state["count"] > 255:
                state["count"] = 1
            return state["count"], 0, 0

        display_func(WS_TEST_LED, YELLOW)

        @sio.on("run_test_show")
        def on_run_show(msg):
            state["count"] += 1
            display_func(SHOW_STATUS_LED, BLUE)
            try:
                run_this_show(light_box, display_func, {"type": "test"})
                display_func(SHOW_STATUS_LED, GREEN)
            except Exception as e:
                display_func(SHOW_STATUS_LED, RED)
                sprint("encountered error while running test: " + str(e))
            finally:
                display_func(WS_COUNTER_LED, count_color())

        @sio.on("run_this_show")
        def on_run_this_show(msg):
            sprint("running that show... %s" % msg['type'])
            state["count"] += 1
            display_func(SHOW_STATUS_LED, BLUE)
            try:
                run_this_show(light_box, display_func, msg)
                display_func(SHOW_STATUS_LED, GREEN)
            except Exception as e:
                display_func(SHOW_STATUS_LED, RED)
                sprint("encountered error while running test: " + str(e))
            finally:
                display_func(WS_COUNTER_LED, count_color())

        sprint("entering into event loop...")
        sio.run_forever()


shows = {"solid": solid, "test": test, "glow": glow}


def run_this_show(light_box, display_func, show_data):
    if "type" not in show_data:
        display_func(SHOW_STATUS_LED, RED)
        sprint("show_data has no type, cannot delegate to a handler...")

    show = shows.get(show_data["type"])

    if show is None:
        display_func(SHOW_STATUS_LED, RED)
        sprint("show_data type not registered, cannot delegate to a handler...")

    end_time = time.time() + show_data.get("duration", 0)
    # TODO - check duration time is reasonable??
    while end_time >= time.time():
        show(light_box, display_func, show_data["effect"])


def test_show(light_box, effect, duration):
    red_color_mod = 0
    blue_color_mod = 1
    index = 0

    end_time = time.time() + duration

    while time.time() <= end_time:
        light_box[index] = (red_color_mod, 0, blue_color_mod)
        light_box.write()

        if index == LIGHT_BOX_SIZE - 1:
            index = 0
            red_color_mod = min(red_color_mod + 5, 255)
            if red_color_mod % 3 == 0:
                blue_color_mod = min(blue_color_mod + 1, 200)
            light_box.fill((0, 0, 0))
            light_box.write()
        else:
            index += 1

        time.sleep(0.1)


def main():
    sprint("main running")
    # init
    pin = Pin(14, Pin.OUT)
    top_display = NeoPixel(pin, 32)

    def set_top_display(index, color):
        top_display[index] = color
        top_display.write()

    sprint("initializing LEDs")
    set_top_display(MAIN_LOADED_LED, GREEN)

    config = get_config()
    was_loaded = "not " if not config else ""
    sprint("config " + was_loaded + "loaded")

    secrets = get_secrets()
    was_loaded = "not " if not secrets else ""
    sprint("secrets " + was_loaded + "loaded")

    # network check
    sprint("checking network...")
    if config.get("wlan_on", False) is not False:  # handle True _and_ None
        is_connected = do_connect(set_top_display, secrets)
    else:  # handle just False
        is_connected = False
    set_top_display(NETWORK_LED, BLUE if is_connected else RED)
    sprint("network check successful...")

    light_box = LightBox.from_config(config)

    if config.get("wlan_on"):
        sprint("starting light box socket loop...")
        ws_loop(config, light_box, set_top_display)

    else:

        if config.get("run_shows", False) is True:
            for _ in range(10):
                run_this_show(light_box, set_top_display, {"type": "test"})

            light_box.wreset()
        else:
            light_box.wreset()


if __name__ == "__main__":
    main()
