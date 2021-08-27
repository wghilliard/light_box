import json
import time

import eventlet
import socketio

SHOW_ROOM = "shows"

sio = socketio.Server(logger=True, engineio_logger=True)
app = socketio.WSGIApp(sio)

with open("../default_show.json") as handle:
    default_show = json.loads(handle.read())


@sio.on("connect")
def connect(sid, environ):
    print("connect ", sid)
    # sio.emit("l_message", f"howdy-{time.time()}", to=sid)
    # sio.enter_room(sid, SHOW_ROOM)

    # print(sio.rooms(sid))


@sio.on("l_ping")
def my_message(sid, data):
    print("ping ", data)
    sio.emit("l_pong", f"pong-{time.time()}", to=sid)


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect ", sid)
    # sio.leave_room(sid, SHOW_ROOM)


@sio.on("broadcast_test_show")
def send_default_show(sid, data):
    sio.emit("run_test_show", "")


@sio.on("broadcast_this_show")
def send_this_show(sid, data):
    sio.emit("run_this_show", data)


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("", 5000)), app)
