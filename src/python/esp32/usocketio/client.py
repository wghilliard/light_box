"""
Micropython Socket.IO client.
"""

import logging
import ure as re
import ujson as json
import usocket as socket
from ucollections import namedtuple

from .protocol import *
from .transport import SocketIO

LOGGER = logging.getLogger(__name__)

URL_RE = re.compile(r"http://([A-Za-z0-9\-\.]+)(?:\:([0-9]+))?(/.+)?")
URI = namedtuple("URI", ("hostname", "port", "path"))


def urlparse(uri):
    """Parse http:// URLs"""
    match = URL_RE.match(uri)
    if match:
        return URI(match.group(1), int(match.group(2)), match.group(3))


def _connect_http(hostname, port, path):
    """Stage 1 do the HTTP connection to get our SID"""
    try:
        sock = socket.socket()
        addr = socket.getaddrinfo(hostname, port)
        sock.connect(addr[0][4])

        def send_header(header, *args):
            # print(str(header), *args)

            sock.write(header % args + "\r\n")

        send_header(b"GET %s HTTP/1.1", path)
        send_header(b"Host: %s:%s", hostname, port)
        send_header(b"")

        header = sock.readline()[:-2]
        assert header == b"HTTP/1.1 200 OK", header

        length = None

        while header:
            header = sock.readline()[:-2]
            if not header:
                break

            header, value = header.split(b": ")
            header = header.lower()
            if header == b"content-type":
                assert value == b"application/octet-stream"
            elif header == b"content-length":
                length = int(value)

        assert length

        data = sock.read(length)
        return decode_payload(data)

    finally:
        sock.close()


def connect(uri, namespace, timeout=1):
    """Connect to a socket IO server."""
    uri = urlparse(uri)

    assert uri

    path = uri.path or "/" + "socket.io/?EIO=3"

    # Start a HTTP connection, which will give us an SID to use to upgrade
    # the websockets connection
    packets = _connect_http(uri.hostname, uri.port, path)
    # The first packet should open the connection,
    # following packets might be initialisation messages for us
    packet_type, params = next(packets)

    assert packet_type == PACKET_OPEN
    params = json.loads(params)
    # print("Websocket parameters = %s" % params)

    assert "websocket" in params["upgrades"]

    sid = params["sid"]
    path += "&sid={}".format(sid)

    # print("Connecting to websocket SID %s" % sid)

    # Start a websocket and send a probe on it
    ws_uri = "ws://{hostname}:{port}{path}&transport=websocket".format(
        hostname=uri.hostname, port=uri.port, path=path, namespace=namespace
    )

    # print("ws_uri=" + ws_uri)

    socketio = SocketIO(ws_uri, timeout=timeout, **params)

    # handle rest of the packets once we're in the main loop
    @socketio.on("connection")
    def on_connect(data):
        for packet_type, data in packets:
            # print("connection packet={0} type={1}".format(packet_type, data))
            socketio._handle_packet(packet_type, data)

    socketio._send_packet(PACKET_PING, "probe")

    # Send a follow-up poll
    _connect_http(uri.hostname, uri.port, path + "&transport=polling")

    # We should receive an answer to our probe
    packet = socketio._recv()
    assert packet == (PACKET_PONG, "probe")

    # Upgrade the connection
    socketio._send_packet(PACKET_UPGRADE)
    packet = socketio._recv()
    # print("upgrade packet resp=" + str(packet))
    assert packet == (PACKET_NOOP, "")

    return socketio
