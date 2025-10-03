# -*- coding: utf-8 -*-

import socket
import traceback

class MayaClient():
  """
  An example script showing a TCP client connecting to Maya to send and receive
  the data.
  """
  PORT = 17344  # e.g. 20180=Maya 2018 (MEL), 20181=Maya 2018 (Python)
  BUFFER_SIZE = 4096

  def __init__(self):
    self.maya_socket = None
    self.maya_port = MayaClient.PORT

  def connect(self, port=-1):
    if port >= 0:
      self.maya_port = port

    try:
      self.maya_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.maya_socket.connect(("localhost", self.maya_port))
    except:
      traceback.print_exc()
      return False

    return True

  def disconnect(self):
    try:
      self.maya_socket.close()
    except:
      traceback.print_exc()
      return False

    return True

  def send(self, cmd):
    try:
      self.maya_socket.sendall(cmd.encode())
    except:
      traceback.print_exc()
      return False

    return self.recv()

  def recv(self):
    try:
      data = self.maya_socket.recv(MayaClient.BUFFER_SIZE)
    except:
      traceback.print_exc()
      return None

    return data.decode().replace('\x00', '')

  # ----------------------------------------------------------------------------
  # Commands
  # ----------------------------------------------------------------------------

  def echo(self, text):
    cmd = "eval(\"'{0}'\")".format(text)

    return self.send(cmd)

  def new_file(self):
    cmd = "cmds.file(new=True, force=True)"

    return self.send(cmd)

  def create_primitive(self, shape):
    cmd = ""
    if shape == "sphere":
      cmd += "cmds.polySphere()"
    elif shape == "cube":
      cmd += "cmds.polyCube()"
    else:
      print("Invalid Shape {0}".format(shape))
      return None

    result = self.send(cmd)
    return eval(result)

  def translate(self, node, translation):
    cmd = "cmds.setAttr('{0}.translate', {1}, {2}, {3})".format(node, *translation)

    return self.send(cmd)


if __name__ == '__main__':
  maya_client = MayaClient()
  if maya_client.connect():
    print("Connected Successfully")

    if maya_client.disconnect():
      print("Disconnected successfully")

  else:
    print("Failed to connect")
