# -*- coding: utf-8 -*-
import os
import sys
import json
import datetime
from collections import deque

from PySide6.QtCore import QObject, QTimer, QByteArray, Signal
from PySide6.QtNetwork import QTcpSocket, QHostAddress

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings.Logger import Logger


class TCPClientLogger(Logger):

  FILE_NAME = "tcp_client"
  LOGGER_NAME = "TCPClientLogger"


class TCPClientNodeStream(QObject):
  """Simple TCP Client class to listen to external Software"""

  # Constants
  FORMAT = "utf-8"
  HEADER_SIZE = 10
  DISCONNECT_MESSAGE = "DISCONNECT"
  SHUTDOWN_MESSAGE = "SHUTDOWN"
  IGNORE_MSGS = [DISCONNECT_MESSAGE, SHUTDOWN_MESSAGE, "REQUEST_IMMEDIATE_REPLY",
                 "CONNECTION_ESTABLISHED", "HEARTBEAT"]
  TIMEOUT = 120

  # Signals
  tcp_client_msg_sent = Signal(str)
  tcp_client_connect_status = Signal(str)
  tcp_client_sock_msg_rcv = Signal(dict)

  def __init__(self):
    super(TCPClientNodeStream, self).__init__()

    self.host = ''
    self.port = 0
    self.socket = None
    self.send_exec_time = 50 # in milliseconds

    self.system_running = False
    self.internal_reconnect = True

    self.send_q = deque()

    # Initialize client
    self._initialize()

    # It helps to delete old/empty log files
    TCPClientLogger.remove_log_files()

  def _initialize(self):
    try:
      # Setup timers
      self.send_timer = QTimer(self)
      self.query_source_timer = QTimer(self)
      self.query_source_timer.setSingleShot(True)

      # Setup socket
      self.socket = QTcpSocket(self)
      self.socket.setSocketOption(QTcpSocket.KeepAliveOption, 1)

      # Setup connections
      # self.socket.error.connect(self._on_error)
      self.send_timer.timeout.connect(self.client_send)
      self.socket.connected.connect(self._on_connected)
      self.socket.stateChanged.connect(self._on_state_change)
    except Exception:
      TCPClientLogger.exception("Unable to initiate the TCP client because:")

  def _on_connected(self):
    try:
      self.socket.readyRead.connect(self.client_receive)
      self.socket.disconnected.connect(self._on_disconnected)
      self.tcp_client_msg_sent.emit("Connection Established")
      TCPClientLogger.info("Connection Established")

      # Client send loop
      self.count = 1
      self.keep_alive_time = datetime.datetime.now()
      self.send_timer.start(self.send_exec_time)

      # Connection request
      payload = {
        "MSG_TYPE": "CONNECTION_REQUEST",
        "DATA": f"{datetime.datetime.now()}"
      }
      self.send_q.append(payload)

      # Query Source
      self.query_source_timer.singleShot(1000, self._query_source)
    except Exception:
      TCPClientLogger.exception("Unable to keep alive because:")

  def _on_disconnected(self):
    self.send_timer.stop()
    self.socket.disconnected.disconnect()
    self.socket.readyRead.disconnect()
    self.tcp_client_msg_sent.emit("Client disconnected")
    TCPClientLogger.info("Client disconnected")

    self.send_q.clear()

  def _on_error(self, error):
    TCPClientLogger.error(f"{error}: {self.socket.errorString()}")

  def _on_state_change(self, state):
    states = ['Unconnected', 'HostLookup', 'Connecting', 'Connected', 'Bound', 'Closing',
              'Listening']
    self.tcp_client_connect_status.emit(states[state])
    self.tcp_client_msg_sent.emit(f"TCP Client state changed to: {states[state]}")
    TCPClientLogger.info(f"TCP Client state changed to: {states[state]}")

  def _query_source(self):
    try:
      payload = {
        "MSG_TYPE": "SOURCE_REQUEST",
        "DATA": f"{datetime.datetime.now()}"
      }
      self.send_q.append(payload)
    except Exception:
      TCPClientLogger.exception("Unable to query source because:")

  def _get_full_msg(self, payload):
    if payload is None:
      return None

    try:
      json_str = json.dumps(payload)
      header = f"{len(json_str):10d}"
      return QByteArray(f"{header}{json_str}".encode(self.FORMAT))
    except Exception:
      TCPClientLogger.info("Unable to create full message because:")
      return None

  def set_client_address(self, addr=''):
    if ":" not in addr:
      TCPClientLogger.warning("Invalid client address")
      return

    # IP Address
    ip = addr.split(":")[0]
    def isIPv4(s):
      try: return str(int(s)) == s and 0 <= int(s) <= 255
      except: return False

    if ip.count(".") == 3 and all(isIPv4(i) for i in ip.split(".")):
      self.host = ip
    else:
      self.tcp_client_msg_sent.emit("Error: Invalid IP Address, please enter again.")

    # Port Number
    port = int(addr.split(":")[1])
    if port > 0 and port <= 65535:
      self.port = port
    else:
      self.tcp_client_msg_sent.emit("Error: Invalid port number, please enter again")
    TCPClientLogger.info(f"Host: {self.host}, Port: {self.port}")

  def client_connect(self):
    if self.socket.state() == QTcpSocket.UnconnectedState:
      try:
        self.tcp_client_msg_sent.emit(f"Requesting connection with the {self.host} at {self.port}")
        TCPClientLogger.info(f"Requesting connection with the {self.host} at {self.port}")
        self.socket.connectToHost(QHostAddress(self.host), self.port)
      except Exception:
        TCPClientLogger.info(f"Unable to connect to {self.host} at {self.port} because:")

  def client_disconnect(self):
    if self.socket:
      try:
        self.tcp_client_msg_sent.emit("Requesting disconnect from the host")
        TCPClientLogger.info("Requesting disconnect from the host")
        self.socket.disconnectFromHost()
      except Exception:
        TCPClientLogger.info(f"Unable to disconnect from {self.host} at {self.port} because:")

  def client_quit(self):
    if self.socket:
      self.socket.close()
      self.socket.deleteLater()

  def add_payload_to_send_queue(self, payload):
    if not isinstance(payload, dict):
      TCPClientLogger.warning("Invalid payload type received to send")
      return
    self.send_q.append(payload)

  def client_send(self):
    """Thread method for sending data to the server"""
    payload = None
    if self.socket.state() == QTcpSocket.ConnectedState:
      if len(self.send_q) > 0:
        try:
          self.keep_alive_time = datetime.datetime.now()
          payload = self.send_q.popleft()
        except Exception:
          TCPClientLogger.info("Unable to get data from send queue")

      # Send heartbeat to keep connection alive
      if (datetime.datetime.now() - self.keep_alive_time) >= datetime.timedelta(seconds=self.TIMEOUT):
        TCPClientLogger.info("Sending Heartbeat to prevent timeout")
        payload = {
          "MSG_TYPE": "HEARTBEAT",
          "DATA": str(self.count)
        }
        self.count += 1

      if payload is not None:
        try:
          msg_str = self._get_full_msg(payload)
          TCPClientLogger.info(f"Sending: {msg_str}")
          self.socket.write(msg_str)
        except Exception:
          TCPClientLogger.exception("Unable to send data because:")

  def client_receive(self):
    """Thread method to receive data from the server"""
    json_data = ""
    bytes_remaining = -1
    while self.socket.bytesAvailable():
      # Header
      if bytes_remaining <= 0:
        byte_array = self.socket.read(self.HEADER_SIZE)
        bytes_remaining, valid = byte_array.toInt()

        if not valid:
          bytes_remaining = -1
          TCPClientLogger.error("Invalid Header received")

          # Purge unknown data
          self.socket.readAll()
          return

      # Body
      if bytes_remaining > 0:
        byte_array = self.socket.read(bytes_remaining)
        bytes_remaining -= len(byte_array)
        json_data += byte_array.data().decode(self.FORMAT)

        if bytes_remaining == 0:
          bytes_remaining = -1

          try:
            TCPClientLogger.info(f"Received message: {json_data}")
            message = json.loads(json_data)
          except (json.decoder.JSONDecodeError):
            TCPClientLogger.exception("Cannot decode data because:")
          else:
            json_data = ""
            self.keep_alive_time = datetime.datetime.now()
            # Publish incoming message
            if message['MSG_TYPE'] not in self.IGNORE_MSGS:
              self.tcp_client_sock_msg_rcv.emit(message)
            if 'MSG_TYPE' in message:
              # Check for specific MSG_TYPE and take action
              [msg_type, msg_data] = [message['MSG_TYPE'], message['DATA']]
              if msg_type == self.DISCONNECT_MESSAGE:
                TCPClientLogger.info("Disconnect request received from Server")
                self.client_disconnect()
              if msg_type == 'REQUEST_IMMEDIATE_REPLY':
                TCPClientLogger.info("Immediate reply request received from Server")
                self.send_q.append(
                  {"MSG_TYPE": "REQUEST_IMMEDIATE_RESPONSE",
                   "DATA": str(datetime.datetime())}
                )


if __name__ == '__main__':
  """For development purpose only"""
  client = TCPClientNodeStream()