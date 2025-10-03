# -*- coding: utf-8 -*- #
import os
import sys
import time
import asyncio

from typing import Any, List, Dict, Tuple
from asyncua import ua, crypto
from asyncua.sync import Client, SyncNode
from asyncua.tools import endpoint_to_strings
from asyncua.common import ua_utils

from PySide6.QtCore import QObject, Signal

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings.Logger import Logger


class OPCClientLogger(Logger):

  FILE_NAME = "opc_client"
  LOGGER_NAME = "OPCClientLogger"


class SubscriptionHandler(QObject):
  """
  This class is used to handle the data received for the subscription.

  Signals:
    send_datachange_notification: Signal(dict)
      Signal emits whenever data of a node changes
    send_event_notification: Signal(dict)
      Signal emits to notify an event
    send_status_change_notification: Signal(dict)
      Signal emits to notify the change in the status of the server
  """
  send_datachange_notification = Signal(dict)
  send_event_notification = Signal(dict)
  send_status_change_notification = Signal(str)

  def datachange_notification(self, node: SyncNode, val: Any, data: Any) -> None:
    """
    This method is called when the Client receives a data change message from the Server.
    """

    self.send_datachange_notification.emit({"node": node, "value": val, "data": data})

  def event_notification(self, event: Any) -> None:
    """
    This method is called for every event notification from the Server.
    """

    self.send_event_notification.emit(event.get_event_props_as_fields_dict())

  def status_change_notification(self, status: Any) -> None:
    """
    This method is called for every status change notification from the Server.
    """

    self.send_status_change_notification.emit(str(status))


class OPCClientNodeStream(QObject):
  """
  Simple Client class to listen to OPC Server

  Keyword Arguments:
    settings: QSettings
      widget settings

  Constants:
    FORMAT: str
      utf-8 format of messages
    SUB_PERIOD: int
      Subscription period of a node

  Parameters:
    nodes_to_subscribe: list
      Nodes to subscribe to when the connection establishes

  Signals:
    opc_client_msg_sent: Signal(str)
      Signal to publish various event messages
    opc_client_connect_status: Signal(str)
      Signal to publish OPCUA client connection status with the Server
    opc_client_publish_root_node: Signal(SyncNode)
      Signal to publish the root node of the OPCUA server after connection established
  """

  # Constants
  FORMAT = "utf-8"
  SUB_PERIOD = 500

  # variables
  nodes_to_subscribe = [{"node_id": "ns=0;i=2258", "name": "CurrentTime"},
                        {"node_id": "ns=0;i=2259", "name": "State"},
                        {"node_id": "ns=0;i=2267", "name": "ServiceLevel"}]

  # Signals
  opc_client_msg_sent = Signal(str)
  opc_client_connect_status = Signal(str)
  opc_client_publish_root_node = Signal(SyncNode)

  def __init__(self, **kwargs) -> None:
    super(OPCClientNodeStream, self).__init__()

    # settings
    self._settings = kwargs.get('settings', None)

    self.client = None
    self.connected = False
    self.client_settings = None
    self._sub_datachange = None
    self._sub_event = None
    self._subs_dc = {}
    self._subs_ev = {}
    self._upd_node = {}
    self.sec_mode = None
    self.sec_policy = None
    self.cert_path = None
    self.private_key_path = None

    self.sub_handler = SubscriptionHandler()

    # It helps to delete old/empty log files
    OPCClientLogger.remove_log_files()

  def _reset(self) -> None:
    """
    Method to reset OPCUA client states after disconnect.
    """

    self.client = None
    self.connected = False
    self.client_settings = None
    self._sub_datachange = None
    self._sub_event = None
    self._subs_dc = {}
    self._subs_ev = {}
    self.opc_client_connect_status.emit("Disconnected")
    self.opc_client_publish_root_node.emit(None)

  def _subscribe_to_keep_alive(self) -> None:
    """
    Method to subscribe to some of the nodes of the server to keep the connection alive.
    """

    for node_desc in self.nodes_to_subscribe:
      node_desc |= {"handler": self.sub_handler}
      self.sub_datachange(dc_sub_req=node_desc)

  def _unsubscribe_from_keep_alive(self) -> None:
    """
    Method to unsubscribe from the keep alive nodes.
    """

    for node_desc in self.nodes_to_subscribe:
      self.unsub_datachange(dc_unsub_req=node_desc)

  def _retrieve_node_to_be_updated(self, node_id: Any) -> Tuple:
    """
    Method to retrieve the attributes of the node_id to be updated.

    Argument:
      nodeid: Any
        Node ID of a node

    Returns:
      node, vtype
        OPCUA node & variant type
    """

    try:
      return self._upd_node[node_id]['node'], self._upd_node[node_id]['vtype']
    except KeyError:
      self._upd_node[node_id] = {}
      self._upd_node[node_id]['node'] = self.get_node(node_id)
      self._upd_node[node_id]['vtype'] = self._upd_node[node_id]['node'].read_data_type_as_variant_type()

      return self._upd_node[node_id]['node'], self._upd_node[node_id]['vtype']

  def setup_certificate_path(self, cert_path: str) -> None:
    """
    Method to setup the certificate file path.

    Argument:
      cert_path: str
        Certificate file path
    """

    self.cert_path = cert_path

  def load_security_settings(self, uri: str) -> None:
    """
    Method to load the security settings as per the Server Address.

    Argument:
      uri: str
        Address of the OPCUA server
    """

    self.sec_mode = None
    self.sec_policy = None
    self.cert_path = None
    self.private_key_path = None

    try:
      self.client_settings = self._settings.value("security_settings", None)
    except:
      pass
    if self.client_settings is None:
      return
    if uri in self.client_settings:
      mode, policy, cert, key = self.client_settings[uri]
      self.sec_mode = mode
      self.sec_policy = policy
      self.cert_path = cert
      self.private_key_path = key
    OPCClientLogger.info(f"Loaded Client security settings: {self.client_settings}")
    self.opc_client_msg_sent.emit(f"Loaded Client security settings: {self.client_settings}")

  def save_security_settings(self, uri: str) -> None:
    """
    Method to save the security settings of the Server Address.

    Argument:
      uri: str
        Address of the OPCUA server
    """

    try:
      self.client_settings = self._settings.value("security_settings", None)
    except:
      pass
    if self.client_settings is None:
      self.client_settings = {}
    self.client_settings[uri] = [self.sec_mode,
                                 self.sec_policy,
                                 self.cert_path,
                                 self.private_key_path]
    OPCClientLogger.info(f"Saving Client security settings: {self.client_settings}")
    self.opc_client_msg_sent.emit(f"Saving Client security settings: {self.client_settings}")
    if self._settings is not None:
      self._settings.setValue("security_settings", self.client_settings)

  def client_connect(self, uri: str) -> None:
    """
    Method to connect OPCUA client to the server at uri.

    Argument:
      uri: str
        Address of the OPCUA server to connect to
    """

    try:
      self.client_disconnect()
      OPCClientLogger.info(f"Requesting connection with {uri}")
      self.opc_client_msg_sent.emit(f"Requesting connection with {uri}")
      self.client = Client(uri)
      if self.sec_mode is not None and self.sec_policy is not None:
        self.client.set_security(
          getattr(crypto.sec_policy, 'SecurityPolicy' + self.sec_policy),
          self.cert_path, self.private_key_path,
          mode=getattr(ua.MessageSecurityMode, self.sec_mode)
        )
      self.client.connect()
    except (asyncio.exceptions.CancelledError, asyncio.exceptions.TimeoutError):
      OPCClientLogger.warning(f"Unable to connect to {uri}, server not live or address wrong")
      self.opc_client_msg_sent.emit(f"Unable to connect to {uri}, server not live or address wrong")
      pass
    except Exception:
      OPCClientLogger.exception(f"Unable to connect to {uri} because:")
    else:
      try:
        self.connected = True
        self.client.load_data_type_definitions()
        self.save_security_settings(uri)
        self.opc_client_connect_status.emit("Connected")
        self.opc_client_publish_root_node.emit(self.client.nodes.root)
        OPCClientLogger.info(f"Established connection with {uri}")
        self.opc_client_msg_sent.emit(f"Established connection with {uri}")
        self._subscribe_to_keep_alive()
      except Exception:
        OPCClientLogger.exception("Unable to setup OPC client after connected because:")

  def client_disconnect(self) -> None:
    """
    Method to disconnect the client from the connected OPCUA server.
    """

    if self.connected:
      OPCClientLogger.info("Disconnecting from the server")
      self.opc_client_msg_sent.emit("Disconnecting from the server")
      self._unsubscribe_from_keep_alive()
      try:
        self.client.disconnect()
      except (asyncio.exceptions.CancelledError, asyncio.exceptions.TimeoutError):
        OPCClientLogger.warning("Unable to disconnect from server, may be server not live")
        self.opc_client_msg_sent.emit("Unable to disconnect from server, may be server not live")
        pass
      except Exception:
        OPCClientLogger.exception("Unable to disconnect from Server because:")
      else:
        OPCClientLogger.info("Disconnected from the server")
        self.opc_client_msg_sent.emit("Disconnected from the server")
        self._reset()

  def get_node(self, nodeid: Any) -> None:
    """
    Method to get OPCUA node based on nodeid provided.

    Argument:
      nodeid: Any
        Node ID of a node

    Returns:
      node: SyncNode
        Node of an OPCUA server
    """

    return self.client.get_node(nodeid)

  def get_node_attributes(self, node: SyncNode) -> Tuple[SyncNode, List[Any]]:
    """
    Method to get the attributes of the OPCUA node provided.

    Argument:
      node: SyncNode
        Node of an OPCUA server

    Returns:
      node, attribute_values: Tuple
        Node & node's attributes values
    """

    if not isinstance(node, SyncNode):
      node = self.get_node(node)
    attrs = node.read_attributes([ua.AttributeIds.DisplayName, ua.AttributeIds.BrowseName,
                                  ua.AttributeIds.NodeId])
    return node, [attr.Value.Value for attr in attrs]

  def set_node_value(self, upd_node_val: Dict) -> None:
    """
    Method to set the value of a node.

    Argument:
      upd_node_val: Dict
        node id & it's value to be set
    """

    OPCClientLogger.info(
      f"Received request to update {upd_node_val['node_id']} with value: {upd_node_val['nd_value']}")

    upd_node, v_type = self._retrieve_node_to_be_updated(upd_node_val['node_id'])
    # Check for correct node type
    if not isinstance(upd_node, SyncNode):
      OPCClientLogger.warning("Invalid node id type received")
      return

    # Check if the requested node is a variable
    if upd_node.read_node_class() != ua.NodeClass.Variable:
      OPCClientLogger.error("Cannot set a value: Node is not of a variable type.")
      return

    # Check for the value type
    if not isinstance(upd_node_val['nd_value'], str):
      OPCClientLogger.warning("Invalid node value type received")
      return

    # Check if the client is connected
    if self.client is None:
      OPCClientLogger.info(
        f"{upd_node_val['node_id']} value cannot be set, possibly no connection with the server"
      )
      return

    # Change value to accepted format
    try:
      upd_val = ua_utils.string_to_val(string=upd_node_val['nd_value'], vtype=v_type)
    except Exception:
      OPCClientLogger.exception("Unable to fetch node value because:")
      return

    # Write variable
    try:
      upd_node.write_value(ua.DataValue(ua.Variant(upd_val, v_type)))
    except Exception:
      OPCClientLogger.exception(f"Unable to set the value because:")

  def sub_datachange(self, dc_sub_req: Dict) -> None:
    """
    Method to subscribe to a given node for the datachange.

    Argument:
      dc_sub_req: Dict
        id & name of the node with subscription handler
    """

    OPCClientLogger.info(f"Received request to subscribe datachange for {dc_sub_req['name']}")
    handler = dc_sub_req['handler']
    sub_node = self.get_node(dc_sub_req['node_id'])
    if not isinstance(sub_node, SyncNode):
      OPCClientLogger.warning(f"Invalid node id type received")
      return

    if self.client is None:
      OPCClientLogger.info(
        f"{dc_sub_req['name']} cannot be subscribed for datachange, possibly no connection with the server"
      )
      return None

    if self._sub_datachange is None:
      self._sub_datachange = self.client.create_subscription(self.SUB_PERIOD, handler)

    try:
      handle = self._sub_datachange.subscribe_data_change(sub_node)
    except ConnectionError:
      OPCClientLogger.info(
        f"Unable to subscribe to datachange of {dc_sub_req['name']} because no connection with Server"
      )
      pass
    except Exception:
      OPCClientLogger.exception(f"Unable to subscribe to datachange of {dc_sub_req['name']} because:")
      return None
    else:
      OPCClientLogger.info(
        f"Created datachange subscription for node: {dc_sub_req['name']} with handler: {handler}"
      )
      self.opc_client_msg_sent.emit(
        f"Created datachange subscription for node: {dc_sub_req['name']} with handler: {handler}"
      )
      self._subs_dc[sub_node] = handle
      return handle

  def unsub_datachange(self, dc_unsub_req: Dict) -> None:
    """
    Method to unsubscribe a given node from the datachange subscription.

    Argument:
      dc_unsub_req: Dict
        id & name of the node
    """

    OPCClientLogger.info(f"Received request to unsubscribe datachange for {dc_unsub_req['name']}")
    unsub_node = self.get_node(dc_unsub_req['node_id'])
    if not isinstance(unsub_node, SyncNode):
      OPCClientLogger.warning(f"Invalid node id type received")
      return

    if self.client is None:
      OPCClientLogger.info(
        f"{dc_unsub_req['name']} cannot be unsubscribed for datachange, possibly no connection with the server"
      )
      return

    try:
      self._sub_datachange.unsubscribe(self._subs_dc[unsub_node])
    except ConnectionError:
      OPCClientLogger.info(
        f"Unable to unsubscribe datachange of {dc_unsub_req['name']} because no connection with Server"
      )
      pass
    except Exception:
      OPCClientLogger.exception(
        f"Unable to unsubscribe datachange of {dc_unsub_req['name']} because:"
      )
    else:
      OPCClientLogger.info(
        f"Unsubscribed datachange subscription for node: {dc_unsub_req['name']}"
      )
      self.opc_client_msg_sent.emit(
        f"Unsubscribed datachange subscription for node: {dc_unsub_req['name']}"
      )
      self._subs_dc.pop(unsub_node)

  def sub_events(self, node: SyncNode, handler: SubscriptionHandler) -> SubscriptionHandler:
    """
    Method to subscribe to the events of a node.

    Argument:
      node: SyncNode
        Node of an OPCUA server
      handler: SubscriptionHandler
        Subscription handler

    Returns:
      handle: SubscriptionHandler
        Subscription handle
    """

    if self._sub_event is None:
      self._sub_event = self.client.create_subscription(self.SUB_PERIOD, handler)
      OPCClientLogger.info(
        f"Created event subscription for node: {node} with handler: {handler}")
      self.opc_client_msg_sent.emit(
        f"Created event subscription for node: {node} with handler: {handler}")
    handle = self._sub_event.subscribe_events(node)
    self._subs_ev[node.nodeid] = handle
    return handle

  def unsub_events(self, node: SyncNode) -> None:
    """
    Method to unsubscribe from an event subscription of a node.
    """

    self._sub_event.unsubscribe(self._subs_ev[node.nodeid])
    OPCClientLogger.info(f"Unsubscribed event subscription for node: {node}")
    self.opc_client_msg_sent.emit(f"Unsubscribed event subscription for node: {node}")

  @staticmethod
  def get_children(node: SyncNode) -> Any:
    """
    Method to fetch the descriptions of the children of an OPCUA node.

    Argument:
      node: SyncNode
        Node of an OPCUA server

    Returns:
      descriptions: Any
        descriptions of the children of the given OPCUA node
    """

    descriptions = node.get_children_descriptions()
    descriptions.sort(key=lambda x: x.BrowseName)
    return descriptions

  @staticmethod
  def get_endpoints(uri: str) -> Any:
    """
    Method to get the OPCUA server's endpoints.

    Argument:
      uri: str
        Address of the OPCUA server

    Returns:
      endpoints: Any
        Endpoints of the OPCUA server
    """

    client = Client(uri, timeout=2)
    endpoints = client.connect_and_get_server_endpoints()
    for i, ep in enumerate(endpoints, start=1):
      OPCClientLogger.info(f"Endpoint: {i}")
      for (n, v) in endpoint_to_strings(ep):
        OPCClientLogger.info(f"{n}:{v}")
    return endpoints


if __name__ == '__main__':
  """For development purpose only"""
  opc_client = OPCClientNodeStream()
  OPCClientNodeStream().get_endpoints("opc.tcp://10.8.1.10:4840")
  opc_client.client_connect("opc.tcp://10.8.1.10:4840")
  node, attrs = opc_client.get_node_attributes(opc_client.client.nodes.root)
  OPCClientLogger.info(f"Node: {node}, attrs: {attrs}")
  OPCClientLogger.info(f"Display name: {attrs[0].Text}, type: {type(attrs[0])}")
  OPCClientLogger.info(f"Browse Name: {attrs[1].to_string()}, type: {type(attrs[1])}")
  OPCClientLogger.info(f"Node Id: {attrs[2].to_string()}, type: {type(attrs[2])}")
  opc_client.set_node_value({
      "node_id": "ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.SimRobotCurrentAxisVals",
      "nd_value": f"[0.6,0.5,0.4,0.3,0.2,0.1]"
    }
  )
  opc_client.set_node_value({
      "node_id": "ns=4;s=|var|CODESYS SoftMotion Win V3 x64.Application.OPC_Server_Global_Var.SimAxisValues",
      "nd_value": f"[-5.25,180.0,45.8,-90.56,25.25,-175.25,0.25,1.256,15.87,78.59,-102589.24,2578.015,1.1]"
    }
  )
  opc_client.client_disconnect()