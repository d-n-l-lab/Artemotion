# -*- coding: utf-8 -*- #
import time
from asyncua import ua
from asyncua.sync import Client


class SubscriptionHandler:
  """
  The SubscriptionHandler is used to handle the data that is received for the subscription.
  """
  def datachange_notification(self, node, val, data):
    """
    This method is called when the Client receives a data change message from the Server.
    """
    print(f"Subscribed node: {node}")
    print(f"Subscribed value: {val} with type: {type(val)}")
    print(f"Subscribed data: {data}")
    return node, val, data

  def event_notification(self, event):
    """
    This method is called for every event notification from the Server.
    """
    print(f"Subscribed event: {event.get_event_props_as_fields_dict()}")
    return event.get_event_props_as_fields_dict()

  def status_change_notification(self, status):
    """
    This method is called for every status change notification from the Server.
    """
    print(f"Subcribed status change: {status}")
    return status


if __name__ == '__main__':
  try:
    url = "opc.tcp://10.8.1.10:4840"
    client = Client(url)
    Handler = SubscriptionHandler()
    subscription = None

    # Client Connect
    client.connect()
  except Exception as exc:
    print(f"Unable to connect because: {exc}")
  else:
    try:
      print("Client connected")
      count = 0
      while True:
        print(f"Client not exchanging data: {count}")
        server_state = client.get_node("ns=0;i=2259")
        state = server_state.read_value()
        server_state_class = server_state.read_node_class()
        print(f"Server state: {state} with class: {server_state_class}")

        service_level = client.get_node("ns=0;i=2267")
        level = service_level.read_value()
        service_level_class = service_level.read_node_class()
        print(f"Service level: {level} with class: {service_level_class}")

        current_time = client.get_node("ns=0;i=2258")
        ctime = current_time.read_value()
        d_t = current_time.read_data_type_as_variant_type()
        current_time_class = current_time.read_node_class()
        print(f"Server time: {ctime} with class: {current_time_class}, with datatype: {str(d_t).replace('VariantType.', '')}")

        for i in range(6):
          axis_value = client.get_node(f"ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.ActualRobotCurrentAxisVals[{i}]")
          a_v = axis_value.read_value()
          d_t = axis_value.read_data_type_as_variant_type()
          axis_value_class = axis_value.read_node_class()
          print(f"Axis {i+1} value: {a_v} with class: {axis_value_class}, with datatype: {str(d_t).replace('VariantType.', '')}")
        count += 1
        time.sleep(1)
    except KeyboardInterrupt:
      print("Requesting disconnect")
      client.disconnect()