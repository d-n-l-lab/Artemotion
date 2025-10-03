## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2021
##
##############################################################################################
##
import os
import sys
import posixpath

from typing import Dict

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QObject, QSettings, QThread, Signal, QModelIndex
from PySide6.QtWidgets import (QApplication, QWidget, QFrame, QSpacerItem, QVBoxLayout,
                               QSizePolicy)

from asyncua import ua
from asyncua.sync import SyncNode

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.comm.OPCClientNodeStream import OPCClientNodeStream
  from scripts.ui.widgets_sub.OPCUASubWidgets import OPCUAStandardItem
  from scripts.ui.widgets_sub.OPCUASubWidgets import ServerAddressDialog
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.comm.OPCClientNodeStream import OPCClientNodeStream
  from scripts.ui.widgets_sub.OPCUASubWidgets import OPCUAStandardItem
  from scripts.ui.widgets_sub.OPCUASubWidgets import ServerAddressDialog


class OPCClientUiLogger(Logger):

  FILE_NAME = "ui_opc_client"
  LOGGER_NAME = "UIOPCClientLogger"


class OPCClientWidgetWorker(QObject):

  opc_client_wdgt_worker_msg_sent = Signal(str)

  def __init__(self):
    super(OPCClientWidgetWorker, self).__init__()


class OPCClientWidget(QFrame):

  opc_client_connect = Signal(str)
  opc_client_disconnect = Signal()
  opc_client_uri_changed = Signal(str)
  opc_client_set_node_val = Signal(dict)
  opc_client_datachange_sub_req = Signal(dict)
  opc_client_datachange_unsub_req = Signal(dict)
  publish_selected_node = Signal(dict)
  publish_selection_clear = Signal()
  publish_datachange_notification = Signal(dict)
  publish_status_message = Signal(str)

  def __init__(self, parent: QWidget=None, settings: QSettings=None) -> None:
    super(OPCClientWidget, self).__init__(parent=parent)

    # Assign attributes to the frame
    self.setObjectName(u"opcClientWidget")
    self.setWindowTitle("OPC Client")
    if parent is None:
      self.resize(410, 487)
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self._opc_address_list = []
    self._opc_addr_list_max_cnt = 0

    self.serverAddDialog = None
    self.editConnectionsDialog = None

    self.server_protocol = None

    self._parent = parent
    # Get the application setting
    self._settings = settings
    if self._settings is not None:
      self._read_settings()

    self.init_UI()

    # Set OPC Client Widget default stylesheet
    self.set_stylesheet()

    # It helps to delete old/empty log files
    OPCClientUiLogger.remove_log_files()

  def init_UI(self) -> None:
    # Create main layout
    opcClientWdgtMainLayout = QVBoxLayout(self)
    opcClientWdgtMainLayout.setObjectName(u"opcClientWdgtMainLayout")

    # Create Layouts
    self._create_top_vertical_layout()
    verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
    self._create_stacked_widget()

    # Add widgets to the layout & set margins
    opcClientWdgtMainLayout.addLayout(self.opcUATopVertLayout)
    opcClientWdgtMainLayout.addItem(verticalSpacer)
    opcClientWdgtMainLayout.addWidget(self.opcUAStackedWidget)
    opcClientWdgtMainLayout.setContentsMargins(20, 10, 20, 10)
    opcClientWdgtMainLayout.setSpacing(10)

    # Connections
    self._create_local_connect()
    self._create_server_config_page_connects()

    # # Workers & threads
    # self._create_opc_wdgt_worker_thread()
    # self._create_opc_client_worker_thread()

    # Initialize stacked widget
    self._on_page_select_button_clicked()
    self._on_opcua_config_stckd_wdgt_page_chngd()

  def set_stylesheet(self, theme: str='default', qss: str='OPCClientWidget.qss') -> None:
    try:
      # Set the StyleSheet
      qss_file = PathManager.get_qss_path(logger=OPCClientUiLogger,
                                          qss_file=os.path.join(theme, qss))
      icons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.relpath(qss_file)))),
                                "icons", theme)
      with open(qss_file, 'r') as fh:
        style_sheet = fh.read()
        self.setStyleSheet(style_sheet.replace("<icons_path>",
                                              f"{icons_path}".replace(os.sep, posixpath.sep)))
    except FileNotFoundError:
      pass
    except Exception:
      self._logger("Unable to set stylesheet because:")

  def _read_settings(self) -> None:
    self._opc_address_list = self._settings.value(
      "opc_address_list", ["opc.tcp://localhost:4840",
                           "opc.tcp://localhost:4840/OPCUA/SimulationServer/"])
    self._opc_addr_list_max_cnt = int(self._settings.value("address_list_max_count", 10))

  def _create_opc_wdgt_worker_thread(self) -> None:
    # Create the Worker & Thread
    self.opc_wdgt_worker_thread = QThread(self)
    self.opc_wdgt_worker = OPCClientWidgetWorker()
    self.opc_wdgt_worker.moveToThread(self.opc_wdgt_worker_thread)

    # Create connections
    self.opc_wdgt_worker.opc_client_wdgt_worker_msg_sent.connect(self._on_status_message_received)

    # Start the thread
    self.opc_wdgt_worker_thread.start()

  def _create_opc_client_worker_thread(self) -> None:
    # Create the Worker & Thread
    self.opc_client_worker_thread = QThread(self)
    self.opc_client_worker = OPCClientNodeStream()
    self.opc_client_worker.moveToThread(self.opc_client_worker_thread)

    # Create connections
    self.opc_client_connect.connect(self.opc_client_worker.client_connect)
    self.opc_client_disconnect.connect(self.opc_client_worker.client_disconnect)
    self.opc_client_uri_changed.connect(self.opc_client_worker.load_security_settings)
    self.opc_client_set_node_val.connect(self.opc_client_worker.set_node_value)
    self.opc_client_datachange_sub_req.connect(self.opc_client_worker.sub_datachange)
    self.opc_client_datachange_unsub_req.connect(self.opc_client_worker.unsub_datachange)

    self.opc_client_worker.opc_client_msg_sent.connect(self._on_status_message_received)
    self.opc_client_worker.opc_client_connect_status.connect(self._on_connect_status_change)
    self.opc_client_worker.opc_client_publish_root_node.connect(self._on_client_root_node_publish)

    self.opc_client_worker.sub_handler.send_datachange_notification.connect(
      self._on_datachange_notification_recvd
    )

    # Start the thread
    self.opc_client_worker_thread.start()

  def _update_opc_address_list(self, uri: str) -> None:
    if uri == self._opc_address_list[0]:
      return

    if uri in self._opc_address_list:
      self._opc_address_list.remove(uri)
    self._opc_address_list.insert(0, uri)
    if len(self._opc_address_list) > self._opc_addr_list_max_cnt:
      self._opc_address_list.pop(-1)

  def _on_uri_changed(self, uri: str) -> None:
    if uri:
      self.opc_client_uri_changed.emit(uri)

  def _show_server_add_dialog(self) -> None:
    if self.serverAddDialog is None:
      self.serverAddDialog = ServerAddressDialog(parent=self)
      self.serverAddDialog.buttonBox.accepted.connect(
        lambda: self._on_server_addr_changed(self.serverAddDialog.serverAddrComboBox.lineEdit().text())
      )
      self.serverAddDialog.buttonBox.rejected.connect(
        lambda: self._on_server_addr_dlg_close()
      )
      self.serverAddDialog.dialog_closed.connect(
        self._on_server_addr_dlg_close
      )
      self.serverAddDialog.show()

  def _on_server_addr_changed(self, addr: str) -> None:
    if not isinstance(addr, str):
      OPCClientUiLogger.warning("Invalid server address format received")

    OPCClientUiLogger.info(f"New Server Address: {addr}")

    if addr.split("//")[-1] != '':
      if addr not in self._opc_address_list:
        self._opc_address_list.append(addr)
      self.uriComboBox.clear()
      self.uriComboBox.addItems(self._opc_address_list)
      self.opc_client_connect.emit(addr)
      self.opcClientConnPushButton.setChecked(True)
    self._on_server_addr_dlg_close()

  def _on_server_addr_dlg_close(self) -> None:
    if self.serverAddDialog is not None:
      self.serverAddDialog.close()
      self.serverAddDialog = None

  def _toggle_connect_button(self, checked: bool) -> None:
    uri = self.uriComboBox.currentText()
    if checked:
      self.opc_client_connect.emit(uri)
    else:
      self.opc_client_disconnect.emit()

  def _on_connect_status_change(self, state: str) -> None:
    if state == "Connected":
      self.opcClientConnPushButton.setText("Disconnect")
      self._update_opc_address_list(str(self.uriComboBox.currentText()))
    elif state == "Disconnected":
      self.opcClientConnPushButton.setText("Connect")

  def _on_client_root_node_publish(self, node: SyncNode=None) -> None:
    OPCClientUiLogger.info(f"Received root node as: {node}")
    if node is not None:
      self.opcClientNodesTreeView.set_root_node(node)
    else:
      self.opcClientNodesTreeView.clear()

  def _on_datachange_notification_recvd(self, notif: Dict) -> None:
    if not isinstance(notif, dict):
      OPCClientUiLogger.warning("Invalid datachange notification received")

    def _check_notif_validity(notif: Dict) -> bool:
      names = [elem['name'] for elem in self.opc_client_worker.nodes_to_subscribe]
      if notif['node'].read_display_name().Text in names:
        return False
      return True

    if _check_notif_validity(notif):
      self.publish_datachange_notification.emit(notif)

  def _on_tree_view_item_clicked(self, index: QModelIndex) -> None:
    node = self.opcClientNodesTreeView.data(index, OPCUAStandardItem.NODE_ROLE)
    OPCClientUiLogger.info(f"Item selected: {node}")
    if isinstance(node, SyncNode):
      if node.read_node_class() == ua.NodeClass.Variable:
        children = node.get_children(refs=ua.ObjectIds.HasChild)
        if len(children) > 0:
          OPCClientUiLogger.info("Select child nodes")
        else:
          name = node.read_display_name().Text
          node_id = node.nodeid
          variant_type = str(node.read_data_type_as_variant_type()).replace("VariantType.", "")
          value = node.read_value()
          OPCClientUiLogger.info(
            f"Fetched: {name}, {node_id.to_string()}, {variant_type}, {value}"
          )
          self.publish_selected_node.emit({"Name": name,
                                           "Node_Id": node_id.to_string(),
                                           "Type": variant_type,
                                           "Value": value})

  def _on_tree_view_selection_cleared(self) -> None:
    OPCClientUiLogger.info("Selection cleared")
    self.publish_selection_clear.emit()

  def _on_status_message_received(self, msg: str) -> None:
    if msg:
      self.publish_status_message.emit(msg)

  def on_opc_node_value_recvd(self, upd_node_val: Dict) -> None:
    if not isinstance(upd_node_val, dict):
      OPCClientUiLogger.warning("Invalid data format received to update value of the node")
      return

    self.opc_client_set_node_val.emit(upd_node_val)

  def on_datachange_sub_req_recvd(self, dc_sub_req: Dict) -> None:
    if not isinstance(dc_sub_req, dict):
      OPCClientUiLogger.warning("Invalid data format received to subscribe to data change")
      return

    if 'handler' not in dc_sub_req:
      dc_sub_req['handler'] = self.opc_client_worker.sub_handler

    self.opc_client_datachange_sub_req.emit(dc_sub_req)

  def on_datachange_unsub_req_recvd(self, dc_unsub_req: Dict):
    if not isinstance(dc_unsub_req, dict):
      OPCClientUiLogger.warning("Invalid data format received to unsubscribe from data change")

    self.opc_client_datachange_unsub_req.emit(dc_unsub_req)

  def save_state(self):
    OPCClientUiLogger.info("OPC Client Widget exit.")
    self.opc_client_disconnect.emit()
    self.uriComboBox.clear()
    self.opcClientNodesTreeView.clear()
    if self._settings is not None:
      self._settings.setValue("opc_address_list", self._opc_address_list)
    try:
      if self.opc_wdgt_worker_thread.isRunning():
        self.opc_wdgt_worker_thread.quit()
        self.opc_wdgt_worker_thread.wait()
      if self.opc_client_worker_thread.isRunning():
        self.opc_client_worker_thread.quit()
        self.opc_client_worker_thread.wait()
    except Exception:
      OPCClientUiLogger.exception("Unable to close OPC Widget Worker thread because:")

  def closeEvent(self, event: QCloseEvent):
    # self.save_state()
    return super().closeEvent(event)


if __name__ == '__main__':
  # For development purpose only
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed QWidget
  opc_client_widget = OPCClientWidget()
  # Set some required tags
  opc_client_widget._opc_address_list = ["opc.tcp://localhost:4840",
                                         "opc.tcp://localhost:4840/OPCUA/SimulationServer/"]
  opc_client_widget._opc_addr_list_max_cnt = 10
  # opc_client_widget.tcpClientVarModel.add_item({"DATA": "A1 -0.0, A2 -90.0000015612, A3 90.0000015612, A4 -0.0, A5 0.0, A6 -0.0", "MSG_TYPE": "AXES_DATA"})
  # Show the widget
  opc_client_widget.show()
  # execute the program
  sys.exit(app.exec())