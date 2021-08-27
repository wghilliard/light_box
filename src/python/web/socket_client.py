import socketio

sio = socketio.Client(logger=True, engineio_logger=True)


@sio.on("connect")
def connect():
    print("connected!")
    sio.emit("broadcast_test_show", "")
    # sio.emit(
    #     "broadcast_this_show",
    #     {
    #         "type": "solid",
    #         "effect": {"color": (255, 0, 0), "brightness": 0.5},
    #         "duration": 5,
    #     },
    # )

    sio.emit(
        "broadcast_this_show",
        {
            "type": "glow",
            "effect_data": {
                "fg": {
                    "color": [
                        255,
                        255,
                        255
                    ],
                    "radius": 4,
                    "brightness": 100
                },
                "bg": {
                    "color": [
                        255,
                        0,
                        0
                    ],
                    "brightness": 10
                }
            },
            "duration": 10
        }
    )


sio.connect("http://localhost:5000")
