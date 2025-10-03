# -*- coding: utf-8 -*- #
import os
import sys

from PySide6.QtGui import QStandardItemModel, QStandardItem, QCloseEvent, QColor, QFont
from PySide6.QtCore import QObject, QThread, QSize, Signal, QModelIndex, Qt
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QLayout, QVBoxLayout,
                               QHBoxLayout, QSpacerItem, QTableView, QAbstractItemView,
                               QHeaderView, QSizePolicy)

try:
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget
  from scripts.ui.widgets_sub.SubWidgets import DialogWidget
  from scripts.ui.widgets_sub.SubWidgets import CheckBoxWidget
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget
  from scripts.ui.widgets_sub.OPCUASubWidgets import OPCUAVarsTreeView
except:
  # For the development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget
  from scripts.ui.widgets_sub.SubWidgets import DialogWidget
  from scripts.ui.widgets_sub.SubWidgets import CheckBoxWidget
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget
  from scripts.ui.widgets_sub.OPCUASubWidgets import OPCUAVarsTreeView


class VarConnectUiLogger(Logger):

  FILE_NAME = "ui_var_connect"
  LOGGER_NAME = "UIVarConnectLogger"


class VarConnectWidgetWorker(QObject):

  send_updated_tcp_data = Signal(dict)
  send_updated_opc_node_val = Signal(dict)

  def __init__(self):
    super(VarConnectWidgetWorker, self).__init__()

    # Clients
    self.tcp_client_sock_msg = None

    self.connected_variables = []

  def on_tcp_client_msg_recvd(self, tcp_msg=None):
    if 'SIM' not in tcp_msg['MSG_TYPE']:
      VarConnectUiLogger.info("Unknown TCP message type received")
      return

    self.data_pairs = {key: val for key, val in
                       [pair.split() for pair in tcp_msg['DATA'].split(",")]}

    if self.tcp_client_sock_msg is None:
      self.tcp_client_sock_msg = tcp_msg

    self.write_tcp_data_to_opc(revcd_tcp_msg=tcp_msg)

  def setup_connected_vars(self, vars_couplets=[]):
    VarConnectUiLogger.info(f"Receieved connected variables: {vars_couplets}")
    self.connected_variables = vars_couplets

  def write_tcp_data_to_opc(self, revcd_tcp_msg):
    # Parse TCP data
    try:
      self.data_pairs = {key: val for key, val in
                         [pair.split() for pair in revcd_tcp_msg['DATA'].split(",")]}
    except Exception:
      VarConnectUiLogger.exception("May be not a valid TCP Message:")
      return

    try:
      # Parse connected variables couplets & send data
      if len(self.connected_variables) > 0:
        [self.send_updated_opc_node_val.emit({"node_id": couplet['opc_var_node'], "nd_value": value})
         for key, value in self.data_pairs.items() for couplet in self.connected_variables
         if 'SIM' in couplet['tcp_var_name'].split(".")[1]
         if couplet['tcp_var_name'].split(".")[1] == key
         if revcd_tcp_msg['NAME'] == couplet['tcp_var_name'].split(".")[0][4:]]
    except Exception:
      VarConnectUiLogger.exception("Unable to write TCP data to OPC because:")

  def write_opc_data_to_tcp(self, opc_var={}):
    try:
      [self.data_pairs.update({key: round(opc_var['value'], 3)})
       for key in self.data_pairs.keys()
       for couplet in self.connected_variables
       if 'ACT' in couplet['tcp_var_name'].split(".")[1]
       if couplet['tcp_var_name'].split(".")[1] == key
       if couplet['opc_var_node'] == opc_var['node'].nodeid.to_string()]
    except Exception:
      VarConnectUiLogger.exception("Unable to update the data pairs because:")
    else:
      data_str = ", ".join(f"{key} {val}" for key, val in self.data_pairs.items())
      self.send_updated_tcp_data.emit(
        {
          "MSG_TYPE": self.tcp_client_sock_msg['MSG_TYPE'].replace('SIM', 'ACT'),
          "NAME": self.tcp_client_sock_msg['NAME'],
          "DATA": data_str,
        }
      )


class VarsConnectDialog(DialogWidget):

  def __init__(self, **kwargs) -> None:
    kwargs['title'] = 'Variables to be connected'
    super(VarsConnectDialog, self).__init__(**kwargs)

    # Setup the dialog
    self.resize(QSize(1200, 400))
    self.setObjectName(u"varsConnectDialog")

    # Create contents
    self._create_dialog_contents()

  def _create_dialog_contents(self) -> None:
    # Contents layout
    dlgContentsFrameVertLayout = QVBoxLayout(self.dlgContentsFrame)
    dlgContentsFrameVertLayout.setObjectName(u"dlgContentsFrameVertLayout")

    # Horizontal Layout
    dlgContentsFrameHorizLayout = QHBoxLayout()
    dlgContentsFrameHorizLayout.setObjectName(u"dlgContentsFrameHorizLayout")

    # Create sub layouts
    arte_vars_layout = self._create_artemotion_vars_layout()
    opcua_vars_layout = self._create_server_vars_layout()

    # Add widgets to layout & set margins
    dlgContentsFrameHorizLayout.addLayout(arte_vars_layout)
    dlgContentsFrameHorizLayout.addLayout(opcua_vars_layout)
    dlgContentsFrameHorizLayout.setContentsMargins(0, 0, 0, 0)
    dlgContentsFrameHorizLayout.setSpacing(10)

    # Button layout
    connSelBtnHorizLayout = QHBoxLayout()
    connSelBtnHorizLayout.setObjectName(u"connSelBtnHorizLayout")

    # Spacer
    connSelSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    # Pushbutton
    self.connectSelectedButton = PushButtonWidget(parent=self.dlgContentsFrame,
                                                  text=u"Connect Selected", type="round_button",
                                                  minsize=QSize(150, 25))
    self.connectSelectedButton.setObjectName(u"connectSelectedButton")

    # Add widgets to layout & set margin
    connSelBtnHorizLayout.addItem(connSelSpacer)
    connSelBtnHorizLayout.addWidget(self.connectSelectedButton)
    connSelBtnHorizLayout.addItem(connSelSpacer)
    connSelBtnHorizLayout.setContentsMargins(0, 0, 0, 0)
    connSelBtnHorizLayout.setSpacing(0)

    # Add widgets to layout & set margins
    dlgContentsFrameVertLayout.addLayout(dlgContentsFrameHorizLayout)
    dlgContentsFrameVertLayout.addLayout(connSelBtnHorizLayout)
    dlgContentsFrameVertLayout.setContentsMargins(10, 10, 10, 10)
    dlgContentsFrameVertLayout.setSpacing(10)

  def _create_artemotion_vars_layout(self) -> QLayout:
    # Create Layout
    arteVarsVertLayout = QVBoxLayout()
    arteVarsVertLayout.setObjectName(u"arteVarsVertLayout")

    # Sub Layout
    arteVarsUpperHorizLayout = QHBoxLayout()
    arteVarsUpperHorizLayout.setObjectName(u"arteVarsUpperHorizLayout")

    # Check box
    self.onlySelectCompChkBox = CheckBoxWidget(parent=self.dlgContentsFrame,
                                               text=u"Only selected Components",
                                               minsize=QSize(0, 15))
    self.onlySelectCompChkBox.setObjectName(u"onlySelectCompChkBox")

    # Add widgets to layout & set margin
    arteVarsUpperHorizLayout.addWidget(self.onlySelectCompChkBox)
    arteVarsUpperHorizLayout.setContentsMargins(0, 0, 0, 0)
    arteVarsUpperHorizLayout.setSpacing(5)

    # Sub Layout
    arteVarsLowerHorizLayout = QHBoxLayout()
    arteVarsLowerHorizLayout.setObjectName(u"arteVarsLowerHorizLayout")

    # Check Boxes
    self.compPropCheckBox = CheckBoxWidget(parent=self.dlgContentsFrame,
                                           text=u"Component Properties", minsize=QSize(0, 15))
    self.compPropCheckBox.setObjectName(u"compPropCheckBox")

    self.behavPropCheckBox = CheckBoxWidget(parent=self.dlgContentsFrame,
                                            text=u"Behavior Properties", minsize=QSize(0, 15))
    self.behavPropCheckBox.setObjectName(u"behavPropCheckBox")

    self.signalsCheckBox = CheckBoxWidget(parent=self.dlgContentsFrame, text=u"Signals",
                                          minsize=QSize(0, 15))
    self.signalsCheckBox.setObjectName(u"signalsCheckBox")

    self.signalMapsCheckBox = CheckBoxWidget(parent=self.dlgContentsFrame, text=u"Signal maps",
                                             minsize=QSize(0, 15))
    self.signalMapsCheckBox.setObjectName(u"signalMapsCheckBox")

    self.degOfFreedomCheckBox = CheckBoxWidget(parent=self.dlgContentsFrame,
                                               text=u"Degrees of Freedom", minsize=QSize(0, 15))
    self.degOfFreedomCheckBox.setObjectName(u"degOfFreedomCheckBox")

    # Add widgets to layout & set margin
    arteVarsLowerHorizLayout.addWidget(self.compPropCheckBox)
    arteVarsLowerHorizLayout.addWidget(self.behavPropCheckBox)
    arteVarsLowerHorizLayout.addWidget(self.signalsCheckBox)
    arteVarsLowerHorizLayout.addWidget(self.signalMapsCheckBox)
    arteVarsLowerHorizLayout.addWidget(self.degOfFreedomCheckBox)
    arteVarsLowerHorizLayout.setContentsMargins(0, 0, 0, 0)
    arteVarsLowerHorizLayout.setSpacing(5)

    # TreeView
    # To Do: Change the TreeView class as it is just for testing purpose
    self.arteVarsTreeView = OPCUAVarsTreeView(tree_name='arte_vars_tree',
                                              header_labels=['Structure', 'Parent', 'Variable',
                                                             'Type'],
                                              parent=self.dlgContentsFrame,
                                              settings=self._settings)
    self.arteVarsTreeView.setObjectName(u"arteVarsTreeView")

    # Add widgets to layout & set margin
    arteVarsVertLayout.addLayout(arteVarsUpperHorizLayout)
    arteVarsVertLayout.addLayout(arteVarsLowerHorizLayout)
    arteVarsVertLayout.addWidget(self.arteVarsTreeView)
    arteVarsVertLayout.setContentsMargins(0, 0, 0, 0)
    arteVarsVertLayout.setSpacing(10)

    return arteVarsVertLayout

  def _create_server_vars_layout(self) -> QLayout:
    # Create Layout
    serverVarsVertLayout = QVBoxLayout()
    serverVarsVertLayout.setObjectName(u"serverVarsVertLayout")

    # Spacer
    serverVarsSpacerItem = QSpacerItem(40, 15, QSizePolicy.Expanding, QSizePolicy.Minimum)

    # Selected Server Horizontal Layout
    selectedServerHorizLayout = QHBoxLayout()
    selectedServerHorizLayout.setObjectName(u"selectedServerHorizLayout")

    # Labels
    selectedServerInfoLabel = LabelWidget(parent=self.dlgContentsFrame, text=u"Selected Server:",
                                          type="sub_label")
    selectedServerInfoLabel.setObjectName(u"selectedServerInfoLabel")

    self.selectedServerLabel = LabelWidget(parent=self.dlgContentsFrame, type="data_label",
                                           minsize=QSize(0, 15))
    self.selectedServerLabel.setObjectName(u"selectedServerLabel")

    # Add widgets to layout & set margins
    selectedServerHorizLayout.addWidget(selectedServerInfoLabel)
    selectedServerHorizLayout.addWidget(self.selectedServerLabel)
    selectedServerHorizLayout.addItem(serverVarsSpacerItem)
    selectedServerHorizLayout.setContentsMargins(0, 0, 0, 0)
    selectedServerHorizLayout.setSpacing(5)

    # Variables Group Horizontal Layout
    varsGroupHorizLayout = QHBoxLayout()
    varsGroupHorizLayout.setObjectName(u"varsGroupHorizLayout")

    # Labels
    varsGroupInfoLabel = LabelWidget(parent=self.dlgContentsFrame, text=u"Variables Group:",
                                     type="sub_label")
    varsGroupInfoLabel.setObjectName(u"varsGroupInfoLabel")

    self.varsGroupLabel = LabelWidget(parent=self.dlgContentsFrame, type="data_label",
                                      minsize=QSize(0, 15))
    self.varsGroupLabel.setObjectName(u"varsGroupLabel")

    # Add widgets to layout & set margins
    varsGroupHorizLayout.addWidget(varsGroupInfoLabel)
    varsGroupHorizLayout.addWidget(self.varsGroupLabel)
    varsGroupHorizLayout.addItem(serverVarsSpacerItem)
    varsGroupHorizLayout.setContentsMargins(0, 0, 0, 0)
    varsGroupHorizLayout.setSpacing(5)

    # TreeView
    self.varsConnOPCUATreeView = OPCUAVarsTreeView(tree_name='vars_conn_opcua_tree',
                                                   header_labels=['Structure', 'Data Type',
                                                                  'Access', 'Desciption'],
                                                   parent=self.dlgContentsFrame,
                                                   settings=self._settings)
    self.varsConnOPCUATreeView.setObjectName(u"varsConnOPCUATreeView")

    # Add widgets to layout & set margins
    serverVarsVertLayout.addLayout(selectedServerHorizLayout)
    serverVarsVertLayout.addLayout(varsGroupHorizLayout)
    serverVarsVertLayout.addWidget(self.varsConnOPCUATreeView)
    serverVarsVertLayout.setContentsMargins(0, 0, 0, 0)
    serverVarsVertLayout.setSpacing(10)

    return serverVarsVertLayout


class VarConnectWidget(QWidget):

  publish_status_message = Signal(str)
  publish_connected_vars = Signal(list)
  publish_tcp_client_sock_msg = Signal(dict)
  publish_updated_tcp_client_sock_msg = Signal(dict)
  publish_opc_node_new_value = Signal(dict)
  publish_datachange_sub_request = Signal(dict)
  publish_datachange_unsub_request = Signal(dict)
  publish_opc_node_data_changed = Signal(dict)

  def __init__(self, window=None):
    super(VarConnectWidget, self).__init__(window)

    self._settings = None
    self.opc_var_node_id = None
    self.opc_var_to_connect = VarToConnectBuffer()
    self.tcp_var_to_connect = VarToConnectBuffer()
    self.table_view_connected_variables = []
    self.data_transfer_vars_couplets = []

    if window is not None:
      self.window = window

      # Get the application settings
      self._settings = self.window.settings
      self._read_settings()

    self.setObjectName(u"varConnectWidget")

    self.init_UI()

    # It helps to delete old/empty log files
    VarConnectUiLogger.remove_log_files()

  def _read_settings(self):
    if self.window is not None:
      self._settings = self.window.settings

  def _save_settings(self):
    pass

  def init_UI(self):
    # Create Layouts
    self._create_var_connect_bottom_ribbon()
    self._create_connected_var_table()
    self._create_main_layout()

    # Connections
    self._create_local_connect()

    # Workers & threads
    self._create_worker_thread()

  def _create_main_layout(self):
    self.varConnectMainLayout = QVBoxLayout(self)
    self.varConnectMainLayout.setObjectName(u"varConnectMainLayout")

    self.varConnectMainLayout.addWidget(self.varConnectedTableView)
    self.varConnectMainLayout.addLayout(self.varConnectRibbonLayout)
    self.varConnectMainLayout.setContentsMargins(0, 0, 0, 0)

  def _create_connected_var_table(self):
    # Connected variables table view
    self.varConnectedTableView = VarConnectTableView(settings=self._settings, parent=self)
    self.varConnectedTableView.setObjectName(u"varConnectedTableView")

  def _create_var_connect_bottom_ribbon(self):
    # Create a layout
    self.varConnectRibbonLayout = QHBoxLayout()
    self.varConnectRibbonLayout.setObjectName(u"varConnectRibbonLayout")

    # Connect variables
    self.varConnectPushButton = QPushButton(self)
    self.varConnectPushButton.setText(u"Connect")
    self.varConnectPushButton.setEnabled(False)
    self.varConnectPushButton.setObjectName(u"varConnectPushButton")

    self.varDisconnectPushButton = QPushButton(self)
    self.varDisconnectPushButton.setText(u"Disconnect")
    self.varDisconnectPushButton.setEnabled(False)
    self.varDisconnectPushButton.setObjectName(u"varDisconnectPushButton")

    # Add Widgets to layout
    self.varConnectRibbonLayout.addWidget(self.varConnectPushButton)
    self.varConnectRibbonLayout.addWidget(self.varDisconnectPushButton)
    self.varConnectRibbonLayout.setContentsMargins(0, 0, 0, 0)

  def _create_local_connect(self):
    # Pushbuttons
    self.varConnectPushButton.clicked.connect(
      self._on_vars_connect_request
    )
    self.varDisconnectPushButton.clicked.connect(
      lambda: self._on_vars_disconnect_request(
        self.varConnectedTableView.selectionModel().selectedRows()
      )
    )

    # Variables connected table view
    self.varConnectedTableView.clicked[QModelIndex].connect(
      self._on_table_view_item_clicked
    )
    self.varConnectedTableView.invalid_item_selected.connect(
      self._on_table_view_selection_cleared
    )
    self.varConnectedTableView.table_view_empty.connect(
      lambda: self.varDisconnectPushButton.setEnabled(False)
    )

  def _create_worker_thread(self):
    # Create the worker & thread
    self.var_connect_wdgt_thread = QThread(self)
    self.var_connect_wdgt_worker = VarConnectWidgetWorker()
    self.var_connect_wdgt_worker.moveToThread(self.var_connect_wdgt_thread)

    # Create connections
    self.publish_connected_vars.connect(self.var_connect_wdgt_worker.setup_connected_vars)
    self.publish_tcp_client_sock_msg.connect(
      self.var_connect_wdgt_worker.on_tcp_client_msg_recvd
    )
    self.publish_opc_node_data_changed.connect(
      self.var_connect_wdgt_worker.write_opc_data_to_tcp
    )

    self.var_connect_wdgt_worker.send_updated_tcp_data.connect(self._on_updated_tcp_data_recvd)
    self.var_connect_wdgt_worker.send_updated_opc_node_val.connect(self._on_new_opc_node_value_recvd)

    # Start the worker thread
    self.var_connect_wdgt_thread.start()

  def _on_vars_connect_request(self):
    # Check for duplicates
    for var_list in self.table_view_connected_variables:
      if self.opc_var_to_connect['Name'] in var_list:
        VarConnectUiLogger.info(f"{self.opc_var_to_connect['Name']} is already connected.")
        return
      if self.tcp_var_to_connect['Name'] in var_list:
        VarConnectUiLogger.info(f"{self.tcp_var_to_connect['Name']} is already connected.")
        return
    # Update the TableView
    self.table_view_connected_variables.append([self.opc_var_to_connect['Name'],
                                                self.opc_var_to_connect['Type'],
                                                self.opc_var_to_connect['Value'],
                                                self.tcp_var_to_connect['Name'],
                                                self.tcp_var_to_connect['Type'],
                                                self.tcp_var_to_connect['Value']])
    self.varConnectedTableView.add_item(self.opc_var_to_connect, self.tcp_var_to_connect)
    VarConnectUiLogger.info(f"Connected Variables are: {self.table_view_connected_variables}")
    # Send to the worker thread
    self.data_transfer_vars_couplets.append({'opc_var_name': self.opc_var_to_connect['Name'],
                                             'opc_var_node': self.opc_var_node_id,
                                             'tcp_var_name': self.tcp_var_to_connect['Name']})
    self.publish_connected_vars.emit(self.data_transfer_vars_couplets)
    self.publish_datachange_sub_request.emit({'name': self.opc_var_to_connect['Name'],
                                              'node_id': self.opc_var_node_id})

  def _on_vars_disconnect_request(self, indexes):
    # Update the TableView
    VarConnectUiLogger.info(f"Selected index: {indexes}")
    variable = indexes[0].data(Qt.DisplayRole)
    for i, sub_list in enumerate(self.table_view_connected_variables):
      if variable in sub_list:
        self.table_view_connected_variables.pop(i)
        break
    VarConnectUiLogger.info(f"Connected Variables are: {self.table_view_connected_variables}")
    self.varConnectedTableView.remove_row(indexes)
    # Send to the worker thread
    for i, sub_dict in enumerate(self.data_transfer_vars_couplets):
      if variable in sub_dict.values():
        self.data_transfer_vars_couplets.pop(i)
        self.publish_datachange_unsub_request.emit({'name': sub_dict['opc_var_name'],
                                                    'node_id': sub_dict['opc_var_node']})
        break
    self.publish_connected_vars.emit(self.data_transfer_vars_couplets)

  def _on_table_view_item_clicked(self, index):
    var = self.varConnectedTableView.data(index, VarConnectStandardItem.DATA_ROLE)
    VarConnectUiLogger.info(f"Item selected: {var}")
    self.varDisconnectPushButton.setEnabled(True)

  def _on_table_view_selection_cleared(self):
    VarConnectUiLogger.info("Selection cleared")
    self.varDisconnectPushButton.setEnabled(False)

  def _on_updated_tcp_data_recvd(self, tcp_msg={}):
    if 'MSG_TYPE' not in tcp_msg.keys():
      VarConnectUiLogger.info("Invalid TCP message received")
      return

    self.publish_updated_tcp_client_sock_msg.emit(tcp_msg)

  def _on_new_opc_node_value_recvd(self, upd_node_value={}):
    self.publish_opc_node_new_value.emit(upd_node_value)

  def on_opc_client_node_recv(self, node_data):
    self.opc_var_to_connect['Name'] = node_data['Name']
    self.opc_var_to_connect['Type'] = node_data['Type']
    self.opc_var_to_connect['Value'] = node_data['Value']
    self.opc_var_node_id = node_data['Node_Id']
    VarConnectUiLogger.info(f"OPC variable to be connected: {self.opc_var_to_connect}")
    if len(self.tcp_var_to_connect) > 0:
      self.varConnectPushButton.setEnabled(True)

  def on_opc_client_selection_clear(self):
    self.opc_var_to_connect.clear()
    VarConnectUiLogger.info(f"OPC variable to be connected: {self.opc_var_to_connect}")
    self.varConnectPushButton.setEnabled(False)

  def on_opc_client_node_data_changed_recvd(self, node_dc):
    if not isinstance(node_dc, dict):
      VarConnectUiLogger.warning("Invalid OPC node data changed received")
      return

    self.publish_opc_node_data_changed.emit(node_dc)

  def on_tcp_client_var_recv(self, tcp_var):
    VarConnectUiLogger.info(f"Received TCP Client var: {tcp_var}")
    self.tcp_var_to_connect['Name'] = tcp_var['Name']
    self.tcp_var_to_connect['Type'] = tcp_var['Type']
    self.tcp_var_to_connect['Value'] = tcp_var['Value']
    VarConnectUiLogger.info(f"TCP variable to be connected: {self.tcp_var_to_connect}")
    if len(self.opc_var_to_connect) > 0:
      self.varConnectPushButton.setEnabled(True)

  def on_tcp_client_selection_clear(self):
    self.tcp_var_to_connect.clear()
    VarConnectUiLogger.info(f"TCP variable to be connected: {self.tcp_var_to_connect}")
    self.varConnectPushButton.setEnabled(False)

  def on_tcp_sock_msg_recvd(self, tcp_sock_msg):
    if not isinstance(tcp_sock_msg, dict):
      VarConnectUiLogger.warning(f"Invalid TCP client socket message received")
      return

    self.publish_tcp_client_sock_msg.emit(tcp_sock_msg)

  def save_state(self):
    VarConnectUiLogger.info("Var Connect Widget exit.")
    self.varConnectedTableView.clear()
    try:
      if self.var_connect_wdgt_thread.isRunning():
        self.var_connect_wdgt_thread.quit()
        self.var_connect_wdgt_thread.wait()
    except Exception:
      VarConnectUiLogger.exception("Unable to close VarConnectWdgt thread because:")

  def closeEvent(self, event: QCloseEvent):
    self.save_state()
    return super(VarConnectWidget, self).closeEvent(event)


class VarToConnectBuffer(dict):

  def __init__(self, size=3):
    super(VarToConnectBuffer, self).__init__()

    self._max_size = size
    self._stack = []

  def __setitem__(self, name, value):
    if len(self._stack) >= self._max_size:
      self.__delitem__(self._stack[0])
      del self._stack[0]
    self._stack.append(name)
    return super(VarToConnectBuffer, self).__setitem__(name, value)

  def get(self, name, default=None, do_set=False):
    try:
      return super(VarToConnectBuffer, self).__getitem__(name)
    except KeyError:
      if default is not None:
        if do_set:
          self.__setitem__(name, default)
        return default
      else:
        raise

  def clear(self):
    self._stack.clear()
    return super(VarToConnectBuffer, self).clear()


class VarConnectTableView(QTableView):

  invalid_item_selected = Signal()
  table_view_empty = Signal()

  def __init__(self, settings, parent=None):
    super(VarConnectTableView, self).__init__(parent=parent)

    # Load the settings
    try:
      self._settings = settings
      state = self._settings.value("var_connect_table_state", None)
      if state is not None:
        self.horizontalHeader().restoreState()
    except Exception:
      VarConnectUiLogger.info("Working with default settings.")
      pass

    # Setup the Table View
    self.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.setSelectionMode(QAbstractItemView.SingleSelection)

    # Set the model
    self.model = VarConnectTableViewModel()
    self.model.clear()
    self.model.setObjectName(u"varConnectTableModel")
    self.model.setHorizontalHeaderLabels(['Name', 'Type', 'Value',
                                          'Value', 'Type', 'Name'])
    self.setModel(self.model)

    # Resize the table
    self.resizeColumnsToContents()
    self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

  def remove_row(self, indexes):
    for index in indexes:
      if not index.isValid():
        return
      self.model.removeRow(index.row())
    if self.model.rowCount() == 0:
      self.table_view_empty.emit()

  def save_state(self):
    self._settings.setValue("var_connect_table_state", self.horizontalHeader().saveState())

  def add_item(self, opc_data, tcp_data):
    self.model.add_item(opc_data, tcp_data)
    self.resizeColumnsToContents()
    self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

  def mousePressEvent(self, event):
    item = self.indexAt(event.pos())
    if not item.isValid():
      self.clearSelection()
      self.invalid_item_selected.emit()
    return super(VarConnectTableView, self).mousePressEvent(event)

  def data(self, index, role):
    return self.model.data(index, role)

  def clear(self):
    self.model.clear()


class VarConnectStandardItem(QStandardItem):

  DATA_ROLE = Qt.UserRole + 1

  def __init__(self, text='', font_size=8, set_bold=False, color=QColor(0, 0, 0)):
    super(VarConnectStandardItem, self).__init__()

    fnt = QFont('MS Shell Dlg 2', font_size)
    fnt.setBold(set_bold)

    self.setEditable(False)
    self.setForeground(color)
    self.setFont(fnt)

    self.setText(text)

  def setToolTip(self, toolTip):
    return super(VarConnectStandardItem, self).setToolTip(toolTip)

  def setData(self, value, role):
    return super(VarConnectStandardItem, self).setData(value, role=role)


class VarConnectTableViewModel(QStandardItemModel):

  def __init__(self):
    super(VarConnectTableViewModel, self).__init__()

    self.root_node = self.invisibleRootItem()

  def clear(self):
    # Remove all rows but not the header
    self.removeRows(0, self.rowCount())

  def add_item(self, opc_data=None, tcp_data=None):
    if not isinstance(opc_data, dict) and not isinstance(tcp_data, dict):
      return

    items = [VarConnectStandardItem(opc_data['Name']),
             VarConnectStandardItem(opc_data['Type']),
             VarConnectStandardItem(str(opc_data['Value'])),
             VarConnectStandardItem(str(tcp_data['Value'])),
             VarConnectStandardItem(tcp_data['Type']),
             VarConnectStandardItem(tcp_data['Name'])]
    for item in items:
      item.setData(opc_data['Name']+":"+tcp_data['Name'], VarConnectStandardItem.DATA_ROLE)
      item.setToolTip(item.text())
    self.root_node.appendRow(items)

  def update_data(self):
    pass


if __name__ == '__main__':
  """For the development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed QWidget
  vars_connect_widget = VarsConnectDialog()
  # Show the widget
  vars_connect_widget.show()
  # Execute the program
  sys.exit(app.exec())