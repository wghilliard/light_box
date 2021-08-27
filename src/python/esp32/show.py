import time
from constants import sprint
import json

from constants import OFF


def fade(light_box, display_func, effect_data):
    """
    This show lights up the entire LightBox with
    - either IN or OUT
    - a color at a specified brightness [RBG, 1-100]

    :param light_box:
    :param display_func:
    :param effect_data:
    :return:
    """
    if effect_data is None or effect_data == dict():
        with open("test_data.json") as handle:
            effect_data = json.loads(handle.read())["fade"]

    fade_in = effect_data["fade_in"]
    color = effect_data["color"]
    rate = int(effect_data["rate"])
    limit = int(255 * effect_data["limit"] / 100)

    top = max(*color)
    bottom = tuple(int(ch / top) for ch in color)

    light_box.fill(OFF)

    if fade_in is True:

        def update(prev):
            return tuple(min(int(ch * rate), 255) for ch in prev)

        current = bottom
        stop = limit

        def is_done(cur, sto):
            return max(*current) >= sto

    else:  # Fade out

        def update(prev):
            return tuple(min(int(ch / rate), 255) for ch in prev)

        current = color
        stop = bottom

        def is_done(cur, sto):
            return max(*current) <= sto

    while not is_done(current, stop):
        current = update(current)
        light_box.fill(current)
        light_box.write()
        light_box.sleep(0.2)


def glow(light_box, display_func, effect_data):
    """
    This show lights up the entire LightBox with
    - the background color at a specified brightness [RBG, 1-100]
    - a given position with plus radius with a foreground color at a specified brightness [RBG, int, 1-100]
    - for one second and then returns

    example_effect_data = {
        "fg": {
            "color": (255, 255, 255),
            "radius": 4,
            "brightness": 100
        },
        "bg": {
            "color" : (255, 0, 0),
            "brightness": 10
        }
    }

    :param light_box:
    :param display_func:
    :param effect_data:
    :return:
    """
    if effect_data is None or effect_data == dict():
        with open("test_data.json") as handle:
            effect_data = json.loads(handle.read())["glow"]

    bg = effect_data["bg"]
    fg = effect_data["fg"]

    light_box.fill(tuple(int(ch * bg["brightness"]) for ch in bg["color"]))

    adjusted_fg_color = tuple(int(ch * fg["brightness"]) for ch in fg["color"])
    fg_pos = fg["position"]
    radius = fg["radius"]
    decay = fg.get("decay", 0.2)
    l_light_box = len(light_box)
    if fg["radius"] > radius:
        for edge, offset in enumerate(
            range(min(fg_pos + 1, l_light_box), min(fg_pos + radius + 1, l_light_box))
        ):
            light_box[offset] = tuple(
                int(ch * (1 - decay * edge)) for ch in adjusted_fg_color
            )

    for edge, offset in enumerate(reversed(range(max(fg_pos - radius, 0), fg_pos))):
        light_box[offset] = tuple(
            int(ch * (1 - decay * edge)) for ch in adjusted_fg_color
        )

    light_box.write()

    time.sleep(1)


def solid(light_box, display_func, effect_data):
    """
    This show lights up the entire LightBox for one second and then returns.
    :param light_box:
    :param display_func:
    :param effect_data:
    :return:
    """
    light_box.driver.fill(effect_data["color"])
    light_box.write()

    time.sleep(1)


def test(light_box, display_fun, effect_data):
    """

    :param light_box:
    :param display_fun:
    :param effect_data:
    :return:
    """
    sprint("loading default show")
    with open("default_show.json") as handle:
        show_vals = json.loads(handle.read())

    effect = show_vals["effect"]
    color = tuple(effect["color"])
    width = int(effect["width"])
    decay = float(effect["decay"])
    l_light_box = len(light_box)

    def send_vals(index):
        indices = set()
        light_box.reset()
        if effect["centered"]:
            pos = index
            indices.add(pos)
            light_box[pos] = color

            for edge, offset in enumerate(
                range(min(index + 1, l_light_box), min(pos + width + 1, l_light_box))
            ):
                light_box[offset] = tuple(int(ch * (1 - decay * edge)) for ch in color)
                sprint(
                    "forward offset="
                    + str(offset)
                    + ", color="
                    + str(light_box[offset])
                )
                # light_box[offset] = color
                indices.add(offset)

                # light_box[offset: pos] = (0, 0, 0)

            for edge, offset in enumerate(reversed(range(max(pos - width, 0), pos))):
                light_box[offset] = tuple(int(ch * (1 - decay * edge)) for ch in color)
                sprint(
                    "reverse offset="
                    + str(offset)
                    + ", color="
                    + str(light_box[offset])
                )
                # light_box[offset] = color
                indices.add(offset)

                # light_box[pos: offset] = (0, 0, 0)

        else:
            pass  # not sure

        light_box.write()
        sprint("written_indices=" + str(sorted(indices)))

    for i in range(len(light_box)):
        sprint("pos=" + str(i))
        send_vals(i)
        time.sleep(float(effect["delay"]))

    light_box.wreset()
