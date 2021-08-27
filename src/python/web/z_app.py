from flask import Flask
from flask_socketio import SocketIO

import time
import logging

# from logging.config import dictConfig
#
# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://flask.logging.wsgi_errors_stream',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'DEBUG',
#         'handlers': ['wsgi']
#     }
# })

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.logger.setLevel(logging.ERROR)

sio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")


@sio.on("connect")
def connect(sid, environ):
    print("connect ", sid)
    sio.emit("message", f"howdy-{time.time()}")


@sio.on("ping")
def my_message(sid, data):
    print("pong ", data)
    sio.emit("message", f"howdy-{time.time()}")


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect ", sid)


@sio.on_error()  # Handles the default namespace
def error_handler(e):
    print(e)


if __name__ == "__main__":
    sio.run(app, host="0.0.0.0")
