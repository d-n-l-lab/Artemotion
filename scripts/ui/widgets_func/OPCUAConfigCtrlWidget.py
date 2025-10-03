## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the OPCUA Configuration Widget.
##
##############################################################################################
##
import os
import sys
import copy
import json
import posixpath

from typing import Any, Dict, List

from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtCore import QSize, QItemSelection, QThread, Signal, Qt
from PySide6.QtWidgets import (QApplication, QGroupBox, QFrame, QStackedWidget, QLayout,
                               QFormLayout, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy,
                               QFileDialog)

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.comm.OPCClientNodeStream import OPCClientNodeStream
  from scripts.ui.widgets_func.VarConnectWidget import VarsConnectDialog
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget, LineEditWidget, PushButtonWidget
  from scripts.ui.widgets_sub.OPCUASubWidgets import (OPCUAStandardItem, OPCUAVarsTreeView,
                                                      OPCUASubsTableView, OPCUAAttrsTableView,
                                                      OPCUAConfigTreeView, EditConnectionDialog)
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.comm.OPCClientNodeStream import OPCClientNodeStream
  from scripts.ui.widgets_func.VarConnectWidget import VarsConnectDialog
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget, LineEditWidget, PushButtonWidget
  from scripts.ui.widgets_sub.OPCUASubWidgets import (OPCUAStandardItem, OPCUAVarsTreeView,
                                                      OPCUASubsTableView, OPCUAAttrsTableView,
                                                      OPCUAConfigTreeView, EditConnectionDialog)


class OPCUAConfigUILogger(Logger):

  FILE_NAME = "ui_opcua_config_ctrl"
  LOGGER_NAME = "UIOPCUAConfigCtrl"


class OPCUAConfigController:

  """
  Class to manage OPCUA Configuration widget functionality

  Keyword Arguments:
    parent : QWidget
      parent widget
    logger : Logger
      Logger class

  Parameter:
    server_desc: str
      description of OPCUA server properties
  """

  server_desc = '{"name": "Server", "type": "server", \
                  "children": [{"name": "ArteMotion to Server", \
                                "type": "data_out_direction", \
                                "children": []}, \
                               {"name": "Server to ArteMotion", \
                                "type": "data_in_direction", \
                                "children": []}]}'

  def __init__(self, **kwargs) -> None:
    super(OPCUAConfigController, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    # OPC Addresses
    self.opc_addr_list = []
    self.opc_addr_list_max_cnt = 10

    # Connection status
    self.server_connected = False

    # Protocol
    self.server_protocol = None

    # icons path
    self.icons_path = str()

    # Timeouts
    self.browse_timeout = 0.0
    self.read_write_timeout = 0.0
    self.subscription_timeout = 0.0

  @staticmethod
  def _is_float(value) -> bool:
    try:
      float(value)
      return True
    except ValueError:
      return False

  def read_settings(self) -> None:
    """
    Method responsible to read the Widget settings. It should be derived in sub class.
    """

    pass

  def update_opc_address_list(self, uri: str) -> None:
    """
    Method to manage the OPCUA server addresses.

    Arguments:
      uri (str): Server Address
    """

    if not uri:
      return

    if "opc.tcp://" not in uri:
      uri = "opc.tcp://" + uri
    if ":4840" not in uri:
      uri += ":4840"

    if len(self.opc_addr_list) > 0:
      if uri == self.opc_addr_list[0]:
        return

    if uri in self.opc_addr_list:
      self.opc_addr_list.remove(uri)
    self.opc_addr_list.insert(0, uri)
    if len(self.opc_addr_list) > self.opc_addr_list_max_cnt:
      self.opc_addr_list.pop(-1)

  def on_server_addr_changed(self, addr: str) -> None:
    """
    Method to update the OPCUA address list in the event of Server address changed.
    It should be derived in sub class.

    Arguments:
      addr (str): Server Address string.
    """

    if not isinstance(addr, str):
      self._logger.warning("Invalid server address format received")

    self._logger.info(f"New Server Address: {addr}")

    if addr.split("//")[-1] != '':
      if addr not in self.opc_addr_list:
        self.opc_addr_list.append(addr)

  def get_server_details(self) -> Dict:
    """
    Method to return the required OPCUA server description as a Dict.
    """

    return json.loads(self.server_desc)

  def update_server_details(self, **kwargs) -> Dict:
    """
    Method to update the server details and return the updated details.

    Keyword Arguments:
      server_desc: dict
        server description
      server_name: str
        name of OPCUA server
    """

    details = copy.deepcopy(kwargs.get('server_desc', json.loads(self.server_desc)))
    server_name = kwargs.get("server_name", "Server")
    if server_name != "Server":
      details['name'] = server_name
      details['children'][0]['name'] = f'ArteMotion to {server_name}'
      details['children'][1]['name'] = f'{server_name} to ArteMotion'

    return details

  def update_server_conn_status(self, connected: bool) -> None:
    """
    Method to update the server connected status.

    Argument:
      connected: bool
        Server connected status
    """

    self.server_connected = connected

  def update_browse_timeout(self, timeout: str) -> None:
    """
    Method to update the browse timeout.

    Argument:
      timeout: str
        Timeout of browse of the node
    """

    if not OPCUAConfigController._is_float(value=timeout):
      self._logger.warning("Invalid timeout value received")
      return

    self.browse_timeout = float(timeout)

  def update_read_write_timeout(self, timeout: str) -> None:
    """
    Method to update the read/write timeout of a node.

    Argument:
      timeout: str
        Timeout of read/write of a value of the node
    """

    if not OPCUAConfigController._is_float(value=timeout):
      self._logger.warning("Invalid timeout value received")
      return

    self.read_write_timeout = float(timeout)

  def update_subscription_timeout(self, timeout: str) -> None:
    """
    Method to update the subscription timeout of a node.

    Argument:
      timeout: str
        Timeout of subscription of the node
    """

    if not OPCUAConfigController._is_float(value=timeout):
      self._logger.warning("Invalid timeout value received")
      return

    self.subscription_timeout = float(timeout)

  def validate_certificate_file_path(self, cert_file_path: str) -> bool:
    """
    Method to validate the certificate file path.

    Argument:
      cert_file_path: str
        Absolute path of the certificate file

    Returns:
      valid: bool
        Certificate file path is valid or not
    """

    valid = True
    if not os.path.exists(cert_file_path):
      self._logger.warning(f"{cert_file_path} does not exist!!!")
      valid = False
    if os.path.splitext(cert_file_path)[1] != ".cert":
      self._logger.warning(f"Invalid {cert_file_path} selected, select correct file format!!!")
      valid = False

    return valid


class OPCUAConfigCtrlWidget(OPCUAConfigController, QFrame):

  """
  Class to manage the main OPCUA Configuration Widget derived from OPCUAConfigController &
  QFrame classes.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      widget settings
    logger: Logger)
      logger class

  Constants:
    CERT_FILE_FILTERS: str
      Filter for the browsable files

  Signals:
    opc_client_connect: Signal(str)
      Signal to request connection with the OPC server
    opc_client_disconnect: Signal
      Signal to request disconnect with the OPC server
    opc_client_cert_path: Signal(str)
      Signal to setup the certificate path
    opc_client_uri_changed: Signal(str)
      Signal emits when server address changes
    opc_client_set_node_val: Signal(dict)
      Signal emits when the value of the node to be changed
    opc_client_browse_timeout: Signal(float)
      Signal emits the timeout period to browse a node
    opc_client_read_write_timeout: Signal(float)
      Signal emits the timeout period of read/write from/to a node
    opc_client_subscription_timeout: Signal(float)
      Signal emits the timeout period of subscription of a node
    opc_client_datachange_sub_req: Signal(dict)
      Signal emits when the node is subscribed for datachange
    opc_client_datachange_unsub_req: Signal(dict)
      Signal emits when the node is unsubscribed from datachange
    publish_selected_node: Signal(dict)
      Signal emits to publish the selected node in the TreeView
    publish_selection_clear: Signal()
      Signal emits when the selection is cleared in the TreeView
    publish_datachange_notification: Signal(dict)
      Signal emits when the datachange of the node happens
    publish_status_message: Signal(str)
      Signal emits when the OPCUA status changes
  """

  # Constants
  CERT_FILE_FILTERS = "cert File (*.cert);; All Files (*.*)"

  # Signals
  opc_client_connect = Signal(str)
  opc_client_disconnect = Signal()
  opc_client_cert_path = Signal(str)
  opc_client_uri_changed = Signal(str)
  opc_client_set_node_val = Signal(dict)
  opc_client_browse_timeout = Signal(float)
  opc_client_read_write_timeout = Signal(float)
  opc_client_subscription_timeout = Signal(float)
  opc_client_datachange_sub_req = Signal(dict)
  opc_client_datachange_unsub_req = Signal(dict)
  publish_selected_node = Signal(dict)
  publish_selection_clear = Signal()
  publish_datachange_notification = Signal(dict)
  publish_status_message = Signal(str)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    kwargs['logger'] = OPCUAConfigUILogger
    super(OPCUAConfigCtrlWidget, self).__init__(**kwargs)

    # Assign attributes to the frame
    self.setObjectName(u"opcUAConfigCtrlWidget")
    self.setWindowTitle(u"OPC UA Config")
    if self._parent is None:
      self.resize(410, 487)
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self.varsConnectDialog = None
    self.connectedVarsDialog = None
    self.editConnectionsDialog = None

    # Get the application setting
    self._settings = kwargs.get('settings', None)
    if self._settings is not None:
      self.read_settings()

    self.init_UI()

    # Set OPC Client Widget default stylesheet
    self.set_stylesheet()

    # It helps to delete old/empty log files
    OPCUAConfigUILogger.remove_log_files()

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create main layout
    opcUAConfigCtrlWdgtMainLayout = QVBoxLayout(self)
    opcUAConfigCtrlWdgtMainLayout.setObjectName(u"opcClientWdgtMainLayout")

    # Create Layouts
    self._create_top_vertical_layout()
    verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
    self._create_stacked_widget()

    # Add widgets to the layout & set margins
    opcUAConfigCtrlWdgtMainLayout.addLayout(self.opcUATopVertLayout)
    opcUAConfigCtrlWdgtMainLayout.addItem(verticalSpacer)
    opcUAConfigCtrlWdgtMainLayout.addWidget(self.opcUAStackedWidget)
    opcUAConfigCtrlWdgtMainLayout.setContentsMargins(20, 10, 20, 10)
    opcUAConfigCtrlWdgtMainLayout.setSpacing(10)

    # Connections
    self._create_local_connect()
    self._create_server_config_page_connects()

    # Workers & threads
    self._create_opc_client_worker_thread()

    # Initialize stacked widget
    self._on_page_select_button_clicked()
    self._on_opcua_config_stckd_wdgt_page_chngd()

  def set_stylesheet(self, theme: str='default', qss: str='OPCUAConfigCtrlWidget.qss') -> None:
    """
    Method to activate the style sheet on the UI elements.
    """

    try:
      # Set the StyleSheet
      qss_file = PathManager.get_qss_path(logger=OPCUAConfigUILogger,
                                          qss_file=os.path.join(theme, qss))
      self.icons_path = os.path.join(
        os.path.dirname(
          os.path.dirname(os.path.dirname(os.path.relpath(qss_file)))
        ),
        "icons", theme
      )
      with open(qss_file, 'r') as fh:
        style_sheet = fh.read()
        self.setStyleSheet(
          style_sheet.replace("<icons_path>", f"{self.icons_path}".replace(os.sep, posixpath.sep))
        )
    except FileNotFoundError:
      pass
    except Exception:
      self._logger("Unable to set stylesheet because:")

  def read_settings(self) -> None:
    """
    Method responsible to read the Widget settings. Derived from the parent class & extended
    to assign various required parameters.
    """

    self.opc_addr_list = self._settings.value("opc_address_list",
                                              ["opc.tcp://localhost:4840",
                                               "opc.tcp://localhost:4840/OPCUA/SimulationServer/"])
    self.opc_addr_list_max_cnt = self._settings.value("address_list_max_count", 10)

  def _create_stacked_wdgt_ctrl_btns_layout(self) -> QLayout:
    """
    Method to create a layout to manage the selection buttons of the stacked widget.
    """

    # Create buttons layout
    stackedWdgtsBtnsHorizLayout = QHBoxLayout()
    stackedWdgtsBtnsHorizLayout.setObjectName(u"stackedWdgtsBtnsHorizLayout")

    # Create buttons
    self.serverPageSelectButton = PushButtonWidget(parent=self, logger=self._logger,
                                                   text=u"Server", type="left_button",
                                                   minsize=QSize(0, 20))
    self.serverPageSelectButton.setObjectName(u"serverPageSelectButton")

    self.variablesPageSelectButton = PushButtonWidget(parent=self, logger=self._logger,
                                                      text=u"Variable", type="page_sel_btn",
                                                      minsize=QSize(0, 20))
    self.variablesPageSelectButton.setObjectName(u"variablesPageSelectButton")

    self.impExpPageSelectButton = PushButtonWidget(parent=self, logger=self._logger,
                                                   text=u"Import/Export", type="right_button",
                                                   minsize=QSize(0, 20))
    self.impExpPageSelectButton.setObjectName(u"impExpPageSelectButton")

    # Add widgets to layout & set margins
    stackedWdgtsBtnsHorizLayout.addWidget(self.serverPageSelectButton)
    stackedWdgtsBtnsHorizLayout.addWidget(self.variablesPageSelectButton)
    stackedWdgtsBtnsHorizLayout.addWidget(self.impExpPageSelectButton)
    stackedWdgtsBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    stackedWdgtsBtnsHorizLayout.setSpacing(0)

    return stackedWdgtsBtnsHorizLayout

  def _create_top_vertical_layout(self) -> None:
    """
    Method to create top vertical layout to manage Title label & selection buttons layout.
    """

    # Create top layout
    self.opcUATopVertLayout = QVBoxLayout()
    self.opcUATopVertLayout.setObjectName(u"opcUATopVertLayout")

    # Create title label
    opcUAConfigTitleLabel = LabelWidget(parent=self, logger=self._logger,
                                        text=u"OPC UA Configuration", minsize=QSize(0, 20),
                                        align=Qt.AlignCenter)
    opcUAConfigTitleLabel.setObjectName(u"opcUAConfigTitleLabel")

    btnsHorizLayout = self._create_stacked_wdgt_ctrl_btns_layout()

    # Add widgets to layout & set margins
    self.opcUATopVertLayout.addWidget(opcUAConfigTitleLabel)
    self.opcUATopVertLayout.addLayout(btnsHorizLayout)
    self.opcUATopVertLayout.setContentsMargins(0, 0, 0, 0)
    self.opcUATopVertLayout.setSpacing(15)

  def _create_stacked_widget(self) -> None:
    """
    Main method to create stacked widget with required pages.
    """

    # Create stacked widget
    self.opcUAStackedWidget = QStackedWidget(self)
    self.opcUAStackedWidget.setObjectName(u"opcUAStackedWidget")

    # Create pages
    self.serverConfigPage = ServerConfigPage(logger=OPCUAConfigUILogger)
    self.variablesConfigPage = VariablesConfigPage(logger=OPCUAConfigUILogger)
    self.importExportConfigPage = ImportExportConfigPage(logger=OPCUAConfigUILogger)

    # Add Pages
    self.opcUAStackedWidget.addWidget(self.serverConfigPage)
    self.opcUAStackedWidget.addWidget(self.variablesConfigPage)
    self.opcUAStackedWidget.addWidget(self.importExportConfigPage)

  def _create_local_connect(self) -> None:
    """
    Method to create connections of signals of the local widgets to the respective slots.
    """

    # Pushbuttons
    self.serverPageSelectButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=0)
    )
    self.variablesPageSelectButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=1)
    )
    self.impExpPageSelectButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=2)
    )

    # Stacked Widget
    self.opcUAStackedWidget.currentChanged.connect(
      self._on_opcua_config_stckd_wdgt_page_chngd
    )

  def _create_server_config_page_connects(self):
    """
    Method to create connections of widgets on Server configuration page to the respective
    slots.
    """

    # PushButtons
    self.serverConfigPage.addServerButton.clicked.connect(
      self._on_add_server_btn_clicked
    )
    self.serverConfigPage.removeServerButton.clicked.connect(
      self._on_remove_server_btn_clicked
    )
    self.serverConfigPage.serverReconnectButton.clicked.connect(
      lambda: self._on_server_connect_req_recvd(True)
    )
    self.serverConfigPage.serverDisconnectButton.clicked.connect(
      lambda: self.opc_client_disconnect.emit()
    )
    self.serverConfigPage.editConnectionButton.clicked.connect(
      self._show_edit_connections_dialog
    )

    # TreeView
    self.serverConfigPage.opcUAConfigTreeView.invalid_item_selected.connect(
      self._on_conn_vars_tree_view_sel_cleared
    )
    self.serverConfigPage.opcUAConfigTreeView.show_server_variables.connect(
      self._show_server_variables
    )
    self.serverConfigPage.opcUAConfigTreeView.remove_server.connect(
      self._on_remove_server_btn_clicked
    )
    self.serverConfigPage.opcUAConfigTreeView.show_connected_variables.connect(
      self._show_connected_variables_dialog
    )
    self.serverConfigPage.opcUAConfigTreeView.add_variables_pairs.connect(
      self._show_add_variables_dialog
    )
    self.serverConfigPage.opcUAConfigTreeView.remove_data_flow_group.connect(
      self._remove_data_flow_group
    )
    self.serverConfigPage.opcUAConfigTreeView.selectionModel().selectionChanged.connect(
      self._on_conn_vars_tree_view_sel_changed
    )
    self.serverConfigPage.opcUAConfigTreeView.opcUAConfigDelegate.connect_btn_clicked.connect(
      self._on_server_connect_req_recvd
    )
    self.serverConfigPage.opcUAConfigTreeView.opcUAConfigDelegate.in_dir_enable_btn_clicked.connect(
      self._on_in_dir_data_enable_req_recvd
    )
    self.serverConfigPage.opcUAConfigTreeView.opcUAConfigDelegate.out_dir_enable_btn_clicked.connect(
      self._on_out_dir_data_enable_req_recvd
    )

    # LineEdits
    self.serverConfigPage.serverNameLineEdit.editingFinished.connect(
      lambda: self._on_server_name_changed(self.serverConfigPage.serverNameLineEdit.text())
    )
    self.serverConfigPage.browseTimeOutLineEdit.editingFinished.connect(
      lambda: self.update_browse_timeout(self.serverConfigPage.browseTimeOutLineEdit.text())
    )
    self.serverConfigPage.readWriteTimeOutLineEdit.editingFinished.connect(
      lambda: self.update_read_write_timeout(
        self.serverConfigPage.readWriteTimeOutLineEdit.text()
      )
    )
    self.serverConfigPage.subscriptionTimeOutLineEdit.editingFinished.connect(
      lambda: self.update_subscription_timeout(
        self.serverConfigPage.subscriptionTimeOutLineEdit.text()
      )
    )

  def _create_opc_client_worker_thread(self) -> None:
    """
    Method to create OPCUA worker thread to manage the connection with the server.
    """

    # Create the Worker & Thread
    self.opc_client_worker_thread = QThread(self)
    self.opc_client_worker = OPCClientNodeStream(settings=self._settings)
    self.opc_client_worker.moveToThread(self.opc_client_worker_thread)

    # Create connections
    self.opc_client_connect.connect(self.opc_client_worker.client_connect)
    self.opc_client_disconnect.connect(self.opc_client_worker.client_disconnect)
    self.opc_client_cert_path.connect(self.opc_client_worker.setup_certificate_path)
    self.opc_client_uri_changed.connect(self.opc_client_worker.load_security_settings)
    self.opc_client_set_node_val.connect(self.opc_client_worker.set_node_value)
    self.opc_client_datachange_sub_req.connect(self.opc_client_worker.sub_datachange)
    self.opc_client_datachange_unsub_req.connect(self.opc_client_worker.unsub_datachange)

    self.opc_client_worker.opc_client_msg_sent.connect(
      lambda msg: self.publish_status_message.emit(msg)
    )
    self.opc_client_worker.opc_client_connect_status.connect(self._on_connect_status_change)
    self.opc_client_worker.opc_client_publish_root_node.connect(self._on_client_root_node_publish)

    # Start the thread
    self.opc_client_worker_thread.start()

  def _on_page_select_button_clicked(self, idx: int=0) -> None:
    """
    Method to process the event when selection button clicked.

    Argument:
      idx: int
        index of the page to be made active
    """

    self.opcUAStackedWidget.setCurrentIndex(idx)

  def _on_opcua_config_stckd_wdgt_page_chngd(self, idx: int=0) -> None:
    """
    Method to process the event when the page of stacked widget changes.

    Argument:
      idx: int
        index of the page to be made active
    """

    if not isinstance(idx, int):
      OPCUAConfigUILogger.warning("Invalid index type received")
      return

    if idx == 0:
      self.serverPageSelectButton.setEnabled(False)
      self.variablesPageSelectButton.setEnabled(True)
      self.impExpPageSelectButton.setEnabled(True)
    elif idx == 1:
      self.serverPageSelectButton.setEnabled(True)
      self.variablesPageSelectButton.setEnabled(False)
      self.impExpPageSelectButton.setEnabled(True)
    elif idx == 2:
      self.serverPageSelectButton.setEnabled(True)
      self.variablesPageSelectButton.setEnabled(True)
      self.impExpPageSelectButton.setEnabled(False)

  def _on_add_server_btn_clicked(self):
    """
    Method to process the event when the add server button pressed.
    """

    if self.server_protocol is None:
      OPCUAConfigUILogger.warning("No protocol selected.")
      return

    self.serverConfigPage.opcUAConfigTreeView.add_items(self.get_server_details(),
                                                        self.server_protocol)

  def _on_remove_server_btn_clicked(self) -> None:
    """
    Method to process the event when the remove server button pressed.
    """

    indexes = self.serverConfigPage.opcUAConfigTreeView.selectedIndexes()
    if len(indexes) == 0:
      OPCUAConfigUILogger.warning(f"No server selected to remove")
      return

    if not indexes[0].isValid():
      return

    try:
      item = json.loads(
        self.serverConfigPage.opcUAConfigTreeView.data(indexes[0], OPCUAStandardItem.DATA_ROLE)
      )
      if item['type'] == 'server':
        self.serverConfigPage.opcUAConfigTreeView.model.removeRow(indexes[0].row(),
                                                                  indexes[0].parent())
    except Exception:
      OPCUAConfigUILogger.exception("Unable to remove the server because:")

  def _on_conn_vars_tree_view_sel_changed(self, selected: QItemSelection,
                                          deselected: QItemSelection) -> None:
    """
    Method to process the event when the item selection changes in the TreeView.

    Arguments:
      selected: QItemSelection
        Item selected in the TreeView.
      deselected: QItemSelection
        Item deselected in the TreeView.
    """

    if selected.data() is None or not selected.data().isValid():
      return

    try:
      indexes = selected.indexes()
      sel_item = json.loads(
        self.serverConfigPage.opcUAConfigTreeView.data(indexes[0], OPCUAStandardItem.DATA_ROLE)
      )
      if sel_item['type'] == 'protocol':
        self.serverConfigPage.addServerButton.setEnabled(True)
        self.serverConfigPage.removeServerButton.setEnabled(False)
        self.serverConfigPage.serverReconnectButton.setEnabled(False)
        self.serverConfigPage.serverDisconnectButton.setEnabled(False)
        self.server_protocol = self.serverConfigPage.opcUAConfigTreeView.model.itemFromIndex(
                                indexes[0]
                               )
      elif sel_item['type'] == 'server':
        self.serverConfigPage.addServerButton.setEnabled(False)
        self.serverConfigPage.removeServerButton.setEnabled(True)
        self.serverConfigPage.serverReconnectButton.setEnabled((not self.server_connected))
        self.serverConfigPage.serverDisconnectButton.setEnabled(self.server_connected)
      else:
        self.serverConfigPage.addServerButton.setEnabled(False)
        self.serverConfigPage.removeServerButton.setEnabled(False)
        self.serverConfigPage.serverReconnectButton.setEnabled(False)
        self.serverConfigPage.serverDisconnectButton.setEnabled(False)
    except Exception:
      OPCUAConfigUILogger.exception("Unable to get the item data because:")

  def _on_conn_vars_tree_view_sel_cleared(self) -> None:
    """
    Method to process an event when an invalid item is selected in the TreeView.
    """

    self.server_protocol = None
    self.serverConfigPage.addServerButton.setEnabled(False)
    self.serverConfigPage.removeServerButton.setEnabled(False)

  def _on_server_connect_req_recvd(self, connect: bool):
    """
    Method to process the event when the connect/disconnect server button pressed.

    Arguments:
      connect: bool
        checked/unchecked state of the button.
    """

    if len(self.opc_addr_list) == 0:
      OPCUAConfigUILogger.warning(
        "No server address to connect to, please provide with the server address!!!"
      )
      return

    if connect:
      self.opc_client_connect.emit(self.opc_addr_list[0])
    else:
      self.opc_client_disconnect.emit()

  def _on_in_dir_data_enable_req_recvd(self, checked: bool):
    """
    Method to process the event when the data in flow button pressed.

    Arguments:
      checked: bool
        checked/unchecked state of the button.
    """

    OPCUAConfigUILogger.info(f"Inward data exchange request received with data: {checked}")

  def _on_out_dir_data_enable_req_recvd(self, checked: bool):
    """
    Method to process the event when the data out flow button pressed.

    Arguments:
      checked: bool
        checked/unchecked state of the button.
    """

    OPCUAConfigUILogger.info(f"Outward data exchange request received with data: {checked}")

  def _create_edit_connections_dialog_connects(self) -> None:
    """
    Method to create the connections of the signals of Edit Connections Dialog to the
    respective slots.
    """

    self.editConnectionsDialog.dialog_closed.connect(self._on_edit_connections_dlg_close)
    self.editConnectionsDialog.opcua_server_address.connect(self.update_opc_address_list)
    self.editConnectionsDialog.browse_certificate_file.connect(self._on_browse_cert_bttn_clicked)

  def _show_edit_connections_dialog(self):
    """
    Method to process the event when the Edit Connections button pressed.
    """

    if self.editConnectionsDialog is None:
      self.editConnectionsDialog = EditConnectionDialog(parent=self,
                                                        settings=self._settings,
                                                        logger=OPCUAConfigUILogger)
      self._create_edit_connections_dialog_connects()
      self.editConnectionsDialog.show()

  def _on_edit_connections_dlg_close(self) -> None:
    """
    Method to process the event when the Edit Connections Dialog closes.
    """

    if self.editConnectionsDialog is not None:
      self.editConnectionsDialog.dialog_closed.disconnect()
      self.editConnectionsDialog.close()
      self.editConnectionsDialog = None

  def _show_server_variables(self) -> None:
    """
    Method to process the event when the Show Variables option selected.
    """
    self._on_page_select_button_clicked(idx=1)

  def _show_connected_variables_dialog(self) -> None:
    """
    Method to process the event to show Connected Variables dialog.
    """

    OPCUAConfigUILogger.info(f"Show variables request received.")
    # if self.connectedVarsDialog is None:
    #   self.connectedVarsDialog = VarsConnectDialog(parent=self)
    #   self.connectedVarsDialog.dialog_closed.connect(self._on_connected_variables_dlg_close)
    #   self.connectedVarsDialog.show()

  def _on_connected_variables_dlg_close(self) -> None:
    """
    Method to process the event when the Connected Variables Dialog closes.
    """

    pass
    # if self.connectedVarsDialog is not None:
    #   self.connectedVarsDialog.close()
    #   self.connectedVarsDialog = None

  def _show_add_variables_dialog(self) -> None:
    """
    Method to process the event to show Add Variables dialog.
    """

    OPCUAConfigUILogger.info(f"Add variables request received.")
    if self.varsConnectDialog is None:
      self.varsConnectDialog = VarsConnectDialog(parent=self, settings=self._settings)
      self.varsConnectDialog.dialog_closed.connect(self._on_add_variables_dlg_close)
      self.varsConnectDialog.show()

  def _on_add_variables_dlg_close(self) -> None:
    """
    Method to process the event when the Add Variables Dialog closes.
    """

    if self.varsConnectDialog is not None:
      self.varsConnectDialog.close()
      self.varsConnectDialog = None

  def _remove_data_flow_group(self) -> None:
    """
    Method to process the event when the removal of data flow variables group requested.
    """

    indexes = self.serverConfigPage.opcUAConfigTreeView.selectedIndexes()
    if len(indexes) == 0:
      OPCUAConfigUILogger.warning(f"No data flow group selected to remove")
      return

    if not indexes[0].isValid():
      return

    try:
      item = json.loads(
        self.serverConfigPage.opcUAConfigTreeView.data(indexes[0], OPCUAStandardItem.DATA_ROLE)
      )
      if item['type'] == 'data_in_direction' or item['type'] == 'data_out_direction':
        self.serverConfigPage.opcUAConfigTreeView.model.removeRow(
          indexes[0].row(), indexes[0].parent()
        )
    except Exception:
      OPCUAConfigUILogger.exception("Unable to remove the data flow group because:")

  def _on_connect_status_change(self, status: str) -> None:
    """
    Method to process the events when the OPCUA client's connection status change.

    Argument:
      status: str
        connection status
    """

    if status == "Connected":
      super(OPCUAConfigCtrlWidget, self).update_server_conn_status(True)
      self.serverConfigPage.opcUAConfigTreeView.opcUAConfigDelegate.connectButton.setIcon(
        QIcon(os.path.join(self.icons_path, "power_on.svg"))
      )
      self.serverConfigPage.opcUAConfigTreeView.opcUAConfigDelegate.connectButton.setToolTip(
        "Disconnect"
      )
    elif status == "Disconnected":
      super(OPCUAConfigCtrlWidget, self).update_server_conn_status(False)
      self.serverConfigPage.opcUAConfigTreeView.opcUAConfigDelegate.connectButton.setIcon(
        QIcon(os.path.join(self.icons_path, "power_off.svg"))
      )
      self.serverConfigPage.opcUAConfigTreeView.opcUAConfigDelegate.connectButton.setToolTip(
        "Connect"
      )
    self.serverConfigPage.serverConnStatusLabel.setText(str(self.server_connected))
    self.serverConfigPage.serverReconnectButton.setEnabled((not self.server_connected))
    self.serverConfigPage.serverDisconnectButton.setEnabled(self.server_connected)

  def _on_client_root_node_publish(self, node: Any=None) -> None:
    """
    Method to process the event when the root node is published.

    node: Any
      OPCUA server root node
    """

    if node is not None:
      self.variablesConfigPage.opcUAVarsTreeView.set_root_node(node)
    else:
      self.variablesConfigPage.opcUAVarsTreeView.clear()

  def _on_server_name_changed(self, server_name: str) -> None:
    """
    Method to process the event when a new server name received.

    Argument:
      server_name: str
        Name of OPCUA server
    """

    indexes = self.serverConfigPage.opcUAConfigTreeView.selectedIndexes()
    if len(indexes) == 0:
      OPCUAConfigUILogger.warning(f"No server selected to update")
      return

    if not indexes[0].isValid():
      return

    try:
      old_item = json.loads(
        self.serverConfigPage.opcUAConfigTreeView.data(indexes[0], OPCUAStandardItem.DATA_ROLE)
      )
      if old_item['type'] == 'server':
        if server_name != '':
          upd_item = self.update_server_details(server_desc=old_item, server_name=server_name)
          self.serverConfigPage.opcUAConfigTreeView.update_items(
            item=old_item,
            upd_item=upd_item,
            parent=self.server_protocol
          )
    except Exception:
      OPCUAConfigUILogger.exception("Unable to remove the server because:")

  def _on_browse_cert_bttn_clicked(self) -> None:
    """
    Method to process the events when the browse certificate button clicked.
    """

    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    cert_file_path, _ = QFileDialog.getOpenFileName(self, "Open certificate file", "",
                                                  self.CERT_FILE_FILTERS,
                                                  options=options)
    if cert_file_path:
      if self.editConnectionsDialog is not None:
        self.editConnectionsDialog.usrPrivateKeyLineEdit.setText(
          f"{os.path.basename(cert_file_path)}"
        )
      if self.validate_certificate_file_path(cert_file_path=cert_file_path):
        self.opc_client_cert_path.emit(cert_file_path)

  def update_opc_address_list(self, uri: str) -> None:
    """
    Method to manage the OPCUA server addresses.

    Arguments:
      uri (str): Server Address
    """

    super(OPCUAConfigCtrlWidget, self).update_opc_address_list(uri)
    if len(self.opc_addr_list) > 0:
      self.serverConfigPage.serverAddrDispLabel.setText(self.opc_addr_list[0])

  def update_browse_timeout(self, timeout: str) -> None:
    """
    Method to update the browse timeout.

    Argument:
      timeout: str
        Timeout of browse of the node
    """

    super(OPCUAConfigCtrlWidget, self).update_browse_timeout(timeout)
    self.opc_client_browse_timeout.emit(self.browse_timeout)

  def update_read_write_timeout(self, timeout: str) -> None:
    """
    Method to update the read/write timeout of a node.

    Argument:
      timeout: str
        Timeout of read/write of a value of the node
    """

    super(OPCUAConfigCtrlWidget, self).update_read_write_timeout(timeout)
    self.opc_client_read_write_timeout.emit(self.read_write_timeout)

  def update_subscription_timeout(self, timeout: str) -> None:
    """
    Method to update the subscription timeout of a node.

    Argument:
      timeout: str
        Timeout of subscription of the node
    """

    super(OPCUAConfigCtrlWidget, self).update_subscription_timeout(timeout)
    self.opc_client_subscription_timeout.emit(self.subscription_timeout)

  def on_animation_data_point_recvd(self, anim_point: List) -> None:
    """
    Method to process the event when animation data point received.

    Argument:
      anim_point: List
        List of animation data points containing axes position values of a robot.
    """

    # To Do: Remove this method when a more concrete solution is developed, this is for testing
    # only for now.

    if len(anim_point) < 6:
      OPCUAConfigUILogger.warning("Insufficient animation data to be processed")
      return

    if self.serverConfigPage.serverConnStatusLabel.text() == "True":
      self.opc_client_set_node_val.emit(
        {
          "node_id": "ns=4;s=|var|CODESYS Control for Linux SL.Application.GVL_Motion.SimAxisValues",
          "nd_value": f"{anim_point}"
        }
      )

  def save_state(self):
    """
    Method to save the widget state and perform cleanup before closing.
    """

    try:
      if self.opc_client_worker_thread.isRunning():
        self.opc_client_worker_thread.quit()
        self.opc_client_worker_thread.wait()
    except Exception:
      OPCUAConfigUILogger.exception("Unable to close OPC client worker thread because:")

  def closeEvent(self, event: QCloseEvent):
    """
    Method called on Close Event.
    """

    self.save_state()
    return super(OPCUAConfigCtrlWidget, self).closeEvent(event)


class ServerConfigPage(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(ServerConfigPage, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"serverConfigPage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    serverConfigPageVertLayout = QVBoxLayout(self)
    serverConfigPageVertLayout.setObjectName(u"serverConfigPageVertLayout")

    # Create group boxes
    self._create_conn_config_group_box()
    self._create_server_prop_group_box()

    # Add widgets to layout & set margins
    serverConfigPageVertLayout.addWidget(self.connConfigGroupBox)
    serverConfigPageVertLayout.addWidget(self.serverPropGroupBox)
    serverConfigPageVertLayout.setContentsMargins(15, 0, 15, 0)
    serverConfigPageVertLayout.setSpacing(30)

  def _create_conn_config_group_box(self) -> None:
    # Create group box
    self.connConfigGroupBox = QGroupBox(parent=self, title=u"Connectivity Configuration")
    self.connConfigGroupBox.setObjectName(u"connConfigGroupBox")

    # Create layout
    connConfigVerticalLayout = QVBoxLayout(self.connConfigGroupBox)
    connConfigVerticalLayout.setObjectName(u"connConfigVerticalLayout")

    # Create add/remove buttons layout
    serverBtnsHorizLayout = QHBoxLayout()
    serverBtnsHorizLayout.setObjectName(u"serverBtnsHorizLayout")

    # Create Pushbuttons
    self.addServerButton = PushButtonWidget(parent=self.connConfigGroupBox, logger=self._logger,
                                            text=u"Add Server", type="left_button",
                                            minsize=QSize(0, 20))
    self.addServerButton.setEnabled(False)
    self.addServerButton.setObjectName(u"addServerButton")

    self.removeServerButton = PushButtonWidget(parent=self.connConfigGroupBox,
                                               logger=self._logger, text=u"Remove Server",
                                               type="right_button", minsize=QSize(0, 20))
    self.removeServerButton.setEnabled(False)
    self.removeServerButton.setObjectName(u"removeServerButton")

    # Add widgets to layout & set margins
    serverBtnsHorizLayout.addWidget(self.addServerButton)
    serverBtnsHorizLayout.addWidget(self.removeServerButton)
    serverBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    serverBtnsHorizLayout.setSpacing(0)

    # Create TreeView
    self.opcUAConfigTreeView = OPCUAConfigTreeView(parent=self.connConfigGroupBox,
                                                   logger=self._logger)
    self.opcUAConfigTreeView.setObjectName(u"opcUAConfigTreeView")

    # Create reconnect/disconnect buttons layout
    serverConnReConnHorizLayout = QHBoxLayout()
    serverConnReConnHorizLayout.setObjectName(u"serverConnReConnHorizLayout")

    # Create Pushbuttons
    self.serverReconnectButton = PushButtonWidget(parent=self.connConfigGroupBox,
                                                  logger=self._logger, text=u"Reconnect",
                                                  type="left_button", minsize=QSize(0, 20))
    self.serverReconnectButton.setEnabled(False)
    self.serverReconnectButton.setObjectName(u"serverReconnectButton")

    self.serverDisconnectButton = PushButtonWidget(parent=self.connConfigGroupBox,
                                                   logger=self._logger, text=u"Disconnect",
                                                   type="right_button", minsize=QSize(0, 20))
    self.serverDisconnectButton.setEnabled(False)
    self.serverDisconnectButton.setObjectName(u"serverDisconnectButton")

    # Add widgets to layout & set margins
    serverConnReConnHorizLayout.addWidget(self.serverReconnectButton)
    serverConnReConnHorizLayout.addWidget(self.serverDisconnectButton)
    serverConnReConnHorizLayout.setContentsMargins(0, 0, 0, 0)
    serverConnReConnHorizLayout.setSpacing(0)

    # Add widgets to layout & set margins
    connConfigVerticalLayout.addLayout(serverBtnsHorizLayout)
    connConfigVerticalLayout.addWidget(self.opcUAConfigTreeView)
    connConfigVerticalLayout.addLayout(serverConnReConnHorizLayout)
    connConfigVerticalLayout.setContentsMargins(10, 15, 0, 0)
    connConfigVerticalLayout.setSpacing(6)

  def _create_server_prop_group_box(self) -> None:
    # Create group box
    self.serverPropGroupBox = QGroupBox(parent=self, title=u"Server Properties")
    self.serverPropGroupBox.setObjectName(u"serverPropGroupBox")

    # Create layout
    serverPropertiesFormLayout = QFormLayout(self.serverPropGroupBox)
    serverPropertiesFormLayout.setObjectName(u"serverPropertiesFormLayout")

    # Server Name Label
    serverNameLabel = LabelWidget(parent=self.serverPropGroupBox, logger=self._logger,
                                  text=u"Name", type="sub_label")
    serverNameLabel.setObjectName(u"serverNameLabel")

    # Server Connected Label
    serverConnectedLabel = LabelWidget(parent=self.serverPropGroupBox, logger=self._logger,
                                       text=u"Connected", type="sub_label")
    serverConnectedLabel.setObjectName(u"serverConnectedLabel")

    # Server Connect Status Label
    self.serverConnStatusLabel = LabelWidget(parent=self.serverPropGroupBox,
                                             logger=self._logger, text=u"False",
                                             type="data_label", minsize=QSize(0, 20),
                                             align=Qt.AlignCenter)
    self.serverConnStatusLabel.setObjectName(u"serverConnStatusLabel")

    # Server Connected Label
    serverAddrLabel = LabelWidget(parent=self.serverPropGroupBox, logger=self._logger,
                                  text=u"Server Address", type="sub_label")
    serverAddrLabel.setObjectName(u"serverAddrLabel")

    # Server Connect Status Label
    self.serverAddrDispLabel = LabelWidget(parent=self.serverPropGroupBox, logger=self._logger,
                                           text=u"opc.tcp://localhost:4840",
                                           type="data_label", minsize=QSize(0, 20),
                                           align=Qt.AlignCenter)
    self.serverAddrDispLabel.setObjectName(u"serverAddrDispLabel")

    # Browse TimeOut Label
    browseTimeoutLabel = LabelWidget(parent=self.serverPropGroupBox, logger=self._logger,
                                     text=u"Browse Timeout", type="sub_label")
    browseTimeoutLabel.setObjectName(u"browseTimeoutLabel")

    # Read/Write TimeOut Label
    readWriteTimeoutLabel = LabelWidget(parent=self.serverPropGroupBox, logger=self._logger,
                                        text=u"Read/Write Timeout", type="sub_label")
    readWriteTimeoutLabel.setObjectName(u"readWriteTimeoutLabel")

    # Subscription TimeOut Label
    subscriptionTimeoutLabel = LabelWidget(parent=self.serverPropGroupBox, logger=self._logger,
                                           text=u"Subscription Timeout", type="sub_label")
    subscriptionTimeoutLabel.setObjectName(u"subscriptionTimeoutLabel")

    # Server Name LineEdit
    self.serverNameLineEdit = LineEditWidget(parent=self.serverPropGroupBox, logger=self._logger,
                                             ph_text=u"server name", type="data",
                                             minsize=QSize(0, 20))
    self.serverNameLineEdit.setObjectName(u"serverNameLineEdit")

    # Browse TimeOut LineEdit
    self.browseTimeOutLineEdit = LineEditWidget(parent=self.serverPropGroupBox,
                                                logger=self._logger, ph_text=u"browse timeout",
                                                type="data", minsize=QSize(0, 20))
    self.browseTimeOutLineEdit.setObjectName(u"browseTimeOutLineEdit")

    # Read/Write TimeOut LineEdit
    self.readWriteTimeOutLineEdit = LineEditWidget(parent=self.serverPropGroupBox,
                                                   logger=self._logger,
                                                   ph_text=u"read/write timeout",
                                                   type="data", minsize=QSize(0, 20))
    self.readWriteTimeOutLineEdit.setObjectName(u"readWriteTimeOutLineEdit")

    # Subscription TimeOut LineEdit
    self.subscriptionTimeOutLineEdit = LineEditWidget(parent=self.serverPropGroupBox,
                                                      logger=self._logger,
                                                      ph_text=u"subscription timeout",
                                                      type="data", minsize=QSize(0, 20))
    self.subscriptionTimeOutLineEdit.setObjectName(u"subscriptionTimeOutLineEdit")

    # Edit Connection Pushbutton
    self.editConnectionButton = PushButtonWidget(parent=self.serverPropGroupBox,
                                                 logger=self._logger, text=u"Edit Connection",
                                                 type="round_button", minsize=QSize(0, 20))
    self.editConnectionButton.setObjectName(u"editConnectionButton")

    # Add widgets to layout & set margins
    serverPropertiesFormLayout.setWidget(0, QFormLayout.LabelRole, serverNameLabel)
    serverPropertiesFormLayout.setWidget(0, QFormLayout.FieldRole, self.serverNameLineEdit)
    serverPropertiesFormLayout.setWidget(1, QFormLayout.LabelRole, serverConnectedLabel)
    serverPropertiesFormLayout.setWidget(1, QFormLayout.FieldRole, self.serverConnStatusLabel)
    serverPropertiesFormLayout.setWidget(2, QFormLayout.LabelRole, serverAddrLabel)
    serverPropertiesFormLayout.setWidget(2, QFormLayout.FieldRole, self.serverAddrDispLabel)
    serverPropertiesFormLayout.setWidget(3, QFormLayout.SpanningRole, self.editConnectionButton)
    serverPropertiesFormLayout.setWidget(4, QFormLayout.LabelRole, browseTimeoutLabel)
    serverPropertiesFormLayout.setWidget(4, QFormLayout.FieldRole, self.browseTimeOutLineEdit)
    serverPropertiesFormLayout.setWidget(5, QFormLayout.LabelRole, readWriteTimeoutLabel)
    serverPropertiesFormLayout.setWidget(5, QFormLayout.FieldRole, self.readWriteTimeOutLineEdit)
    serverPropertiesFormLayout.setWidget(6, QFormLayout.LabelRole, subscriptionTimeoutLabel)
    serverPropertiesFormLayout.setWidget(6, QFormLayout.FieldRole, self.subscriptionTimeOutLineEdit)
    serverPropertiesFormLayout.setContentsMargins(10, 15, 0, 0)
    serverPropertiesFormLayout.setHorizontalSpacing(6)
    serverPropertiesFormLayout.setVerticalSpacing(6)

    return serverPropertiesFormLayout


class VariablesConfigPage(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(VariablesConfigPage, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"variablesConfigPage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    variablesConfigWidget = QVBoxLayout(self)
    variablesConfigWidget.setObjectName(u"variablesConfigWidget")

    # Create group boxes
    self._create_variables_group_box()
    self._create_attrs_subs_group_box()

    # Add widgets to layout & set margins
    variablesConfigWidget.addWidget(self.variablesGroupBox)
    variablesConfigWidget.addWidget(self.attrsSubsGroupBox)
    variablesConfigWidget.setContentsMargins(15, 0, 15, 0)
    variablesConfigWidget.setSpacing(30)

    # Connections
    self._create_local_connections()

    # Initialize stacked widget
    self._on_attrs_subs_stckd_wdgt_page_chngd()

  def _create_variables_group_box(self):
    # Create group box
    self.variablesGroupBox = QGroupBox(parent=self, title=u"Variables")
    self.variablesGroupBox.setObjectName(u"variablesGroupBox")

    # Create layout
    variablesVerticalLayout = QVBoxLayout(self.variablesGroupBox)
    variablesVerticalLayout.setObjectName(u"variablesVerticalLayout")

    # Create refresh buttons layout
    varsBtnsHorizLayout = QHBoxLayout()
    varsBtnsHorizLayout.setObjectName(u"varsBtnsHorizLayout")

    # Create Pushbuttons
    self.reloadVarsButton = PushButtonWidget(parent=self.variablesGroupBox, logger=self._logger,
                                             text=u"Reload", type="round_button",
                                             minsize=QSize(0, 20))
    self.reloadVarsButton.setObjectName(u"reloadVarsButton")

    # Add widgets to layout & set margins
    varsBtnsHorizLayout.addWidget(self.reloadVarsButton)
    varsBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    varsBtnsHorizLayout.setSpacing(0)

    # Create TreeView
    self.opcUAVarsTreeView = OPCUAVarsTreeView(tree_name='opcua_vars_tree',
                                               header_labels=['DisplayName', 'BrowseName',
                                                              'NodeId'],
                                               parent=self.variablesGroupBox,
                                               logger=self._logger)
    self.opcUAVarsTreeView.setObjectName(u"opcUAVarsTreeView")

    # Add widgets to layout & set margins
    variablesVerticalLayout.addLayout(varsBtnsHorizLayout)
    variablesVerticalLayout.addWidget(self.opcUAVarsTreeView)
    variablesVerticalLayout.setContentsMargins(10, 15, 0, 0)
    variablesVerticalLayout.setSpacing(6)

  def _create_attributes_table_page(self):
    # Create page
    self.attributesTablePage = QFrame(parent=self.attrsSubsGroupBox)
    self.attributesTablePage.setObjectName(u"attributesTablePage")

    # Create widget layout
    attributesPageVertLayout = QVBoxLayout(self.attributesTablePage)
    attributesPageVertLayout.setObjectName(u"attributesPageVertLayout")

    # Create attributes table
    self.opcUAAttrsTable = OPCUAAttrsTableView(parent=self.attributesTablePage,
                                               logger=self._logger)
    self.opcUAAttrsTable.setObjectName(u"opcUAAttrsTable")

    # Add widgets to layout & set margins
    attributesPageVertLayout.addWidget(self.opcUAAttrsTable)
    attributesPageVertLayout.setContentsMargins(0, 0, 0, 0)
    attributesPageVertLayout.setSpacing(0)

  def _create_subscription_table_page(self):
    # Create page
    self.subscriptionsTablePage = QFrame(parent=self.attrsSubsGroupBox)
    self.subscriptionsTablePage.setObjectName(u"subscriptionsTablePage")

    # Create widget layout
    attributesPageVertLayout = QVBoxLayout(self.subscriptionsTablePage)
    attributesPageVertLayout.setObjectName(u"attributesPageVertLayout")

    # Create attributes table
    self.opcUASubsTable = OPCUASubsTableView(parent=self.subscriptionsTablePage,
                                             logger=self._logger)
    self.opcUASubsTable.setObjectName(u"opcUASubsTable")

    # Add widgets to layout & set margins
    attributesPageVertLayout.addWidget(self.opcUASubsTable)
    attributesPageVertLayout.setContentsMargins(0, 0, 0, 0)
    attributesPageVertLayout.setSpacing(0)

  def _create_attrs_subs_group_box(self):
    # Create group box
    self.attrsSubsGroupBox = QGroupBox(parent=self, title=u"Attributes/Subscriptions")
    self.attrsSubsGroupBox.setObjectName(u"attrsSubsGroupBox")

    # Create layout
    attrsSubsVerticalLayout = QVBoxLayout(self.attrsSubsGroupBox)
    attrsSubsVerticalLayout.setObjectName(u"attrsSubsVerticalLayout")

    # Create attributes/subscriptions buttons layout
    attrsSubsBtnsHorizLayout = QHBoxLayout()
    attrsSubsBtnsHorizLayout.setObjectName(u"attrsSubsBtnsHorizLayout")

    # Create Pushbuttons
    self.attrsSelectButton = PushButtonWidget(parent=self.attrsSubsGroupBox, logger=self._logger,
                                              text=u"Attributes", type="left_button",
                                              minsize=QSize(0, 20))
    self.attrsSelectButton.setObjectName(u"attrsSelectButton")

    self.subsSelectButton = PushButtonWidget(parent=self.attrsSubsGroupBox, logger=self._logger,
                                             text=u"Subscriptions", type="right_button",
                                             minsize=QSize(0, 20))
    self.subsSelectButton.setObjectName(u"subsSelectButton")

    # Create stacked widget
    self.attrsSubsStackedWidget = QStackedWidget(self.attrsSubsGroupBox)
    self.attrsSubsStackedWidget.setObjectName(u"attrsSubsStackedWidget")

    # Create pages
    self._create_attributes_table_page()
    self._create_subscription_table_page()

    # Add Pages
    self.attrsSubsStackedWidget.addWidget(self.attributesTablePage)
    self.attrsSubsStackedWidget.addWidget(self.subscriptionsTablePage)

    # Add widgets to layout & set margins
    attrsSubsBtnsHorizLayout.addWidget(self.attrsSelectButton)
    attrsSubsBtnsHorizLayout.addWidget(self.subsSelectButton)
    attrsSubsBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    attrsSubsBtnsHorizLayout.setSpacing(0)

    # Add widgets to layout & set margins
    attrsSubsVerticalLayout.addLayout(attrsSubsBtnsHorizLayout)
    attrsSubsVerticalLayout.addWidget(self.attrsSubsStackedWidget)
    attrsSubsVerticalLayout.setContentsMargins(10, 15, 0, 0)
    attrsSubsVerticalLayout.setSpacing(6)

  def _create_local_connections(self):
    # PushButtons
    self.attrsSelectButton.clicked.connect(lambda: self._on_page_select_button_clicked(idx=0))
    self.subsSelectButton.clicked.connect(lambda: self._on_page_select_button_clicked(idx=1))

    # Stacked widget
    self.attrsSubsStackedWidget.currentChanged.connect(self._on_attrs_subs_stckd_wdgt_page_chngd)

  def _on_page_select_button_clicked(self, idx: int=0) -> None:
    self.attrsSubsStackedWidget.setCurrentIndex(idx)

  def _on_attrs_subs_stckd_wdgt_page_chngd(self, idx: int=0) -> None:
    if not isinstance(idx, int):
      OPCUAConfigUILogger.warning("Invalid index type received")
      return

    if idx == 0:
      self.attrsSelectButton.setEnabled(False)
      self.subsSelectButton.setEnabled(True)
    elif idx == 1:
      self.attrsSelectButton.setEnabled(True)
      self.subsSelectButton.setEnabled(False)


class ImportExportConfigPage(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(ImportExportConfigPage, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"importExportConfigPage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    importExportConfigWidget = QVBoxLayout(self)
    importExportConfigWidget.setObjectName(u"importExportConfigWidget")

    # Add widgets to layout & set margins
    importExportConfigWidget.setContentsMargins(15, 0, 15, 0)
    importExportConfigWidget.setSpacing(30)


if __name__ == '__main__':
  # For development purpose only
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  app.setAttribute(Qt.AA_UseHighDpiPixmaps)
  # Create an instance of subclassed QWidget
  opc_ua_config_widget = OPCUAConfigCtrlWidget()
# Show the widget
  opc_ua_config_widget.show()
  # execute the program
  sys.exit(app.exec())