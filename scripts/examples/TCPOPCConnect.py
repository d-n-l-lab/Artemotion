# -*- coding: utf-8 -*- #
import os
import sys
import threading

try:
  from scripts.settings.Logger import Logger
  from scripts.comm.TCPClientNodeStream import TCPClientNodeStream
  from scripts.comm.OPCClientNodeStream import OPCClientNodeStream
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings.Logger import Logger
  from scripts.comm.TCPClientNodeStream import TCPClientNodeStream
  from scripts.comm.OPCClientNodeStream import OPCClientNodeStream


class TCPOPCConnectLogger(Logger):

  FILE_NAME = "tcp_opc_connect"
  LOGGER_NAME = "TCPOPCConnectLogger"


class TCPOPCConnect:

  OPC_VAR_NODEID = ["ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.SimRobotCurrentAxisVals[0]",
                    "ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.SimRobotCurrentAxisVals[1]",
                    "ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.SimRobotCurrentAxisVals[2]",
                    "ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.SimRobotCurrentAxisVals[3]",
                    "ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.SimRobotCurrentAxisVals[4]",
                    "ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.SimRobotCurrentAxisVals[5]"]

  def __init__(self):
    self._system_running = True
    self._axes_values = {}
    self._last_axes_values = {'A1': 0.0, 'A2': 0.0, 'A3': 0.0, 'A4': 0.0, 'A5': 0.0, 'A6': 0.0}
    self.tcp_client = TCPClientNodeStream(host='127.0.0.1', port=17344)
    self.opcua_client = OPCClientNodeStream()
    try:
      self.opcua_client.connect("opc.tcp://localhost:4840")
    except Exception as exc:
      self._system_running = False
      TCPOPCConnectLogger.exception(f"OPC Client not connected.")
      return

    self.tcp_thread = threading.Thread(target=self.tcp_client.main_loop, daemon=False)
    self.tcp_thread.start()

  def send_axes_val_to_opc(self, var_id, val):
    TCPOPCConnectLogger.info(f"Sending {val} to {var_id}")
    self.opcua_client.set_node_value(var_id, val)

  def get_tcp_values(self):
    if self.tcp_client.recv_q.not_empty:
      tcp_data = self.tcp_client.recv_q.get()
      TCPOPCConnectLogger.info(f"From TCP Client: {tcp_data}")
      if tcp_data['MSG_TYPE'] == 'AXES_DATA':
        self._axes_values = {key: float(val) for key, val in [pair.split() for pair in tcp_data['DATA'].split(",")]}
        TCPOPCConnectLogger.info(f"Retrieved axes values: {self._axes_values}")

  def main_loop(self):
    TCPOPCConnectLogger.info("TCPOPCConnect Main loop started")
    while self._system_running:
      self.get_tcp_values()
      if self._axes_values and self.opcua_client._connected: # OPC Client is connected
        for i, axis in enumerate(self._axes_values):
          if self._axes_values[axis] != self._last_axes_values[axis]:
            self.send_axes_val_to_opc(self.OPC_VAR_NODEID[i], self._axes_values[axis])
          self._last_axes_values[axis] = self._axes_values[axis]


if __name__ == '__main__':
  # For development purpose only
  tcp_opc_connect = TCPOPCConnect()
  main_thread = threading.Thread(target=tcp_opc_connect.main_loop, daemon=False)
  main_thread.start()
  main_thread.join()