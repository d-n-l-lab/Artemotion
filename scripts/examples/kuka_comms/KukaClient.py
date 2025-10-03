import os
import sys
import time
import queue
import random
import socket
import threading

from lxml import etree

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))))
  from scripts.settings.Logger import Logger


class KUKAUdpClientStream(Logger):
  """Simple client class emulating KUKA Robot"""

  FILE_NAME = "udp_client"
  LOGGER_NAME = "UDPClientLogger"

  FORMAT = 'ASCII'
  BUFF_SIZE = 4096
  TIMEOUT = 0.012
  HOST = '127.0.0.1'
  port = 49152  # Same as set in KUKA RSIConfig.xml
  if len(sys.argv) > 1:
    port = sys.argv[1]

  def __init__(self, host=HOST, port=port):
    super(KUKAUdpClientStream, self).__init__()

    self.host = host
    self.port = port

    self.addr = None

    self.send_to_server_str = self._get_send_str()

    self.recv_q = queue.Queue(maxsize=-1)

    self.threads = []
    self.exit_flag = threading.Event()
    self.msg_send_flag = threading.Event()
    self.cycle = 1
    self.weld_stat = 0
    self.wait_time = 0.0

    # It helps to delete old/empty log files
    self.remove_log_files()

    main_thread = threading.Thread(target=self.main_loop, daemon=False)
    main_thread.start()

  def close_task(self):
    self.system_running = False
    self.sock.close()
    for thread in self.threads:
      try:
        thread.join()
      except Exception:
        self.exception("Exception message:")

  def _get_send_str(self):
    try:
      kuka_file = os.path.join(os.path.abspath('configs'), 'fromKuka.xml')
      root = etree.parse(kuka_file).getroot()

      out_str = etree.tostring(root)
    except Exception:
      self.exception("Exception message:")
      return None

    return out_str

  def parse_data(self):
    self.info("[THREAD]: Start parse data")
    while self.system_running:
      if not self.recv_q.empty():
        data = self.recv_q.get()
        try:
          root = etree.fromstring(data)
          self.info(f"[KUKA]: Received from: {root.attrib.get('Type')}")

          # parse time stamp
          ipoc = root.find('IPOC').text
          self.info(f"[KUKA]: Time stamp is {ipoc}")

          # parse message from external application
          estr = root.find('EStr').text
          self.info(f"[KUKA]: Message received: {estr}")

          # # parse correction switch
          # try:
          #   corr_sw = root.find('CORRSWITCH').text
          # except Exception:
          #   corr_sw = "Unknown"
          #   pass
          # self.info(f"[KUKA]: Correction switch is: {corr_sw}")

          # # parse correction values
          # corr_format = 'XA1YA2ZA3AA4BA5CA6'
          # corr = root.find('Corr')
          # if corr_sw == "TRUE":
          #   cart_corr_vals = [float(corr.get("{}".format(corr_format[i:i+4]))) for i in range(0, len(corr_format), 4)]
          #   self.info(f"[KUKA]: Cartesian correction values are: {cart_corr_vals}")
          # elif corr_sw == "FALSE":
          #   axes_corr_vals = [float(corr.get("{}".format(corr_format[i:i+4]))) for i in range(0, len(corr_format), 4)]
          #   self.info(f"[KUKA]: Axes correction values are: {axes_corr_vals}")
          # else:
          #   corr_vals = [float(corr.get("{}".format(corr_format[i:i+3]))) for i in range(0, len(corr_format), 3)]
          #   self.info(f"[KUKA]: Correction values are: {corr_vals}")

          # # parse override
          # override = root.find('OVERRIDE').text
          # self.info(f"[KUKA]: Program override is: {override}")

          # # parse correction stop
          # stop = root.find('STOP').text
          # self.info(f"[KUKA]: Correction stop is: {stop}")

        except Exception:
          self.exception("Exception message:")
          pass
    self.info("[THREAD]: parse data ended")
    self.close_task()

  def _get_full_msg(self):
    # generate some random values to send
    # actual cartesian positions
    act_cart_x = round(random.uniform(-1000.00, 1000.00), 3)
    act_cart_y = round(random.uniform(-1000.00, 1000.00), 3)
    act_cart_z = round(random.uniform(-1000.00, 1000.00), 3)
    act_cart_a = round(random.uniform(-180.00, 180.00), 3)
    act_cart_b = round(random.uniform(-180.00, 180.00), 3)
    act_cart_c = round(random.uniform(-180.00, 180.00), 3)

    # setpoint cartesian positions
    set_cart_x = act_cart_x
    set_cart_y = act_cart_y
    set_cart_z = act_cart_z
    set_cart_a = act_cart_a
    set_cart_b = act_cart_b
    set_cart_c = act_cart_c

    # actual axes positions
    act_axes_a1 = round(random.uniform(-185.00, 185.00), 3)
    act_axes_a2 = round(random.uniform(-185.00, 65.00), 3)
    act_axes_a3 = round(random.uniform(-138.00, 175.00), 3)
    act_axes_a4 = round(random.uniform(-350.00, 350.00), 3)
    act_axes_a5 = round(random.uniform(-130.00, 130.00), 3)
    act_axes_a6 = round(random.uniform(-350.00, 350.00), 3)

    # setpoint axes positions
    set_axes_a1 = act_axes_a1
    set_axes_a2 = act_axes_a2
    set_axes_a3 = act_axes_a3
    set_axes_a4 = act_axes_a4
    set_axes_a5 = act_axes_a5
    set_axes_a6 = act_axes_a6

    delay = random.randint(1, 20)
    status = 2
    turn = 65
    override = 50
    modeop = 3
    wait_time = time.time()
    if (wait_time - self.wait_time) >= 1.0:
      self.weld_stat = random.randint(0, 2)
      self.wait_time = wait_time

    # actual base
    act_base_x = round(random.uniform(-1000.00, 1000.00), 3)
    act_base_y = round(random.uniform(-1000.00, 1000.00), 3)
    act_base_z = round(random.uniform(-1000.00, 1000.00), 3)
    act_base_a = round(random.uniform(-180.00, 180.00), 3)
    act_base_b = round(random.uniform(-180.00, 180.00), 3)
    act_base_c = round(random.uniform(-180.00, 180.00), 3)

    # actual tool
    act_tool_x = round(random.uniform(-1000.00, 1000.00), 3)
    act_tool_y = round(random.uniform(-1000.00, 1000.00), 3)
    act_tool_z = round(random.uniform(-1000.00, 1000.00), 3)
    act_tool_a = round(random.uniform(-180.00, 180.00), 3)
    act_tool_b = round(random.uniform(-180.00, 180.00), 3)
    act_tool_c = round(random.uniform(-180.00, 180.00), 3)

    ipoc = int(round(time.time() * 1000))

    try:
      out = self.send_to_server_str.decode().format(
              act_cart_x, act_cart_y, act_cart_c, act_cart_a, act_cart_b, act_cart_c,
              set_cart_x, set_cart_y, set_cart_c, set_cart_a, set_cart_b, set_cart_c,
              act_axes_a1, act_axes_a2, act_axes_a3, act_axes_a4, act_axes_a5, act_axes_a6,
              delay, status, turn, override, modeop,
              act_base_x, act_base_y, act_base_z, act_base_a, act_base_b, act_base_c,
              act_tool_x, act_tool_y, act_tool_z, act_tool_a, act_tool_b, act_tool_c,
              self.weld_stat, ipoc)
    except Exception:
      self.exception("Exception message:")
      out = None

    return out

  def client_send(self):
    self.info("[THREAD]: Start client_send")
    while self.system_running:
      payload = self._get_full_msg()
      time.sleep(self.TIMEOUT)

      try:
        self.sock.sendto(payload.encode(self.FORMAT), (self.host, self.port))
        self.info(f"Sent data {payload.encode(self.FORMAT)}.")
      except (ConnectionResetError, ConnectionAbortedError, OSError):
        self.exception("Exception message:")
        continue
    self.info("[THREAD]: client_send ended")
    self.close_task()

  def client_receive(self):
    self.info("[THREAD]: Start client_receive")
    while self.system_running:
      try:
        msg, self.addr = self.sock.recvfrom(self.BUFF_SIZE)
        self.info(f"Received message: {msg}")
        msg_str = msg.decode(self.FORMAT)

        # send data to file manager
        if '</Sen' in msg_str:
          self.recv_q.put(msg_str)
      except (ConnectionRefusedError, ConnectionAbortedError, OSError):
        self.exception("Exception message:")
        time.sleep(1)
    self.info("[THREAD]: client_receive ended")
    self.close_task()

  def _create_threads(self):
    parse_data_thread = threading.Thread(target=self.parse_data,
                                         daemon=True)
    client_send_thread = threading.Thread(target=self.client_send,
                                          daemon=True)
    client_receive_thread = threading.Thread(target=self.client_receive,
                                          daemon=True)
    parse_data_thread.start()
    client_send_thread.start()
    client_receive_thread.start()
    self.threads.append(parse_data_thread)
    self.threads.append(client_send_thread)
    self.threads.append(client_receive_thread)
    while self.system_running:
      self.info("Client main thread")
      time.sleep(1)

  def main_loop(self):
    while not self.exit_flag.wait(self.cycle):
      self.info("In the main thread.")
      try:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connected = True
        self.info("Socket created.")
      except Exception:
        connected = False
        self.exception("Exception message:")
      except KeyboardInterrupt:
        connected = False
        self.exception("Exception message:")
      else:
        # create threads
        if not connected:
          self.info("Closing connection.")
          self.sock.close()
        else:
          self.system_running = True
          self._create_threads()


if __name__ == '__main__':
  client = KUKAUdpClientStream()