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

from typing import Any, Dict, Union

from PySide6.QtGui import (QCloseEvent, QMouseEvent, QStandardItemModel, QStandardItem, QColor,
                           QFont)
from PySide6.QtCore import (QObject, QSettings, QSize, QThread, QPersistentModelIndex, QModelIndex,
                            Signal, Qt)
from PySide6.QtWidgets import (QApplication, QGroupBox, QWidget, QFrame, QStackedWidget, QSizePolicy,
                               QSpacerItem, QLayout, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QLabel, QTreeView, QAbstractItemView)

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.settings.DataFilesManager import DataFilesManager
  from scripts.comm.TCPClientNodeStream import TCPClientNodeStream
except:
  # For the development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.settings.DataFilesManager import DataFilesManager
  from scripts.comm.TCPClientNodeStream import TCPClientNodeStream


class TCPClientUiLogger(Logger):

  FILE_NAME = "ui_tcp_client"
  LOGGER_NAME = "UITCPClientLogger"


class TCPClientWidgetWorker(QObject):

  tcp_client_msg_sent = Signal(str)

  def __init__(self):
    super(TCPClientWidgetWorker, self).__init__()


class TCPClientWidget(QFrame):

  # Constants
  TREE_VIEW_MSGS = ['SOURCE', 'SIM_ROB_DATA', 'SIM_CAM_DATA']

  # Signals for TCP Client Worker
  tcp_client_host_address = Signal(str)
  tcp_client_port_number = Signal(int)
  tcp_client_connect = Signal()
  tcp_client_disconnect = Signal()
  tcp_client_quit = Signal()

  # Signals for other purposes
  publish_selected_var = Signal(dict)
  publish_selection_clear = Signal()
  publish_status_message = Signal(str)
  publish_tcp_client_sock_msg = Signal(dict)
  tcp_client_cache_recvd_data = Signal(dict)
  tcp_client_updated_sock_msg = Signal(dict)

  def __init__(self, parent: QWidget=None, settings: QSettings=None) -> None:
    super(TCPClientWidget, self).__init__(parent=parent)

    self._parent = parent
    self._settings = settings

    # Assign attributes of the frame
    self.setObjectName(u"tcpClientWidget")
    self.setWindowTitle(u"TCP Client")
    if self._parent is None:
      self.resize(410, 487)
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Get the application settings
    if self._settings is not None:
      self._read_settings()

    self.init_UI()

    # Set TCP Client Widget default stylesheet
    self.set_stylesheet()

    # It helps to delete old/empty log files
    TCPClientUiLogger.remove_log_files()

  def init_UI(self):
    # Create main layout
    tcpClientMainLayout = QVBoxLayout(self)
    tcpClientMainLayout.setObjectName(u"tcpClientMainLayout")

    # Create Layouts
    self._create_top_vertical_layout()
    verticalSpacer = QSpacerItem(25, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
    self._create_stacked_widget()

    # Add widgets to the layout & set margins
    tcpClientMainLayout.addLayout(self.tcpConfigTopVertLayout)
    tcpClientMainLayout.addItem(verticalSpacer)
    tcpClientMainLayout.addWidget(self.tcpConfigStackedWidget)
    tcpClientMainLayout.setContentsMargins(20, 10, 20, 10)
    tcpClientMainLayout.setSpacing(10)

    # Connections
    self._create_local_connect()

    # Workers & threads
    self._create_tcp_widget_worker_thread()
    self._create_tcp_client_worker_thread()
    self._create_data_files_manage_worker_thread()

  def set_stylesheet(self, theme: str='default', qss: str='TCPClientWidget.qss') -> None:
    try:
      # Set the StyleSheet
      qss_file = PathManager.get_qss_path(logger=TCPClientUiLogger,
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
    pass

  def _create_stacked_widget_ctrls_btns_layout(self) -> QLayout:
    # Create layout
    stackedWdgtBtnsHorizLayout = QHBoxLayout()
    stackedWdgtBtnsHorizLayout.setObjectName(u"stackedWdgtBtnsHorizLayout")

    # Pushbuttons
    dummy1PushButton = TCPConfigWdgtButton(parent=self, minsize=QSize(0, 25))
    dummy1PushButton.setEnabled(False)
    dummy1PushButton.setObjectName(u"dummy1PushButton")

    dummy2PushButton = TCPConfigWdgtButton(parent=self, minsize=QSize(0, 25))
    dummy2PushButton.setEnabled(False)
    dummy2PushButton.setObjectName(u"dummy2PushButton")

    # Add widgets to horizontal layout & set margins
    stackedWdgtBtnsHorizLayout.addWidget(dummy1PushButton)
    stackedWdgtBtnsHorizLayout.addWidget(dummy2PushButton)
    stackedWdgtBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    stackedWdgtBtnsHorizLayout.setSpacing(0)

    return stackedWdgtBtnsHorizLayout

  def _create_top_vertical_layout(self) -> None:
    # Create top layout
    self.tcpConfigTopVertLayout = QVBoxLayout()
    self.tcpConfigTopVertLayout.setObjectName(u"tcpConfigTopVertLayout")

    # Create title label
    tcpConfigTitleLabel = TCPConfigWdtLabel(parent=self, text=u"TCP/IP Configuration",
                                            minsize=QSize(0, 20), align=Qt.AlignCenter)
    tcpConfigTitleLabel.setObjectName(u"tcpConfigTitleLabel")

    # Create connection Horizontal Layout
    connectionsHorizLayout = QHBoxLayout()
    connectionsHorizLayout.setObjectName(u"connectionsHorizLayout")

    # Create TCP Client Address Horizontal Layout
    tcpClientAddrHorizLayout = QHBoxLayout()
    tcpClientAddrHorizLayout.setObjectName(u"tcpClientAddrHorizLayout")

    # TCP Client Address LineEdit
    self.tcpClientAddrLineEdit = TCPConfigLineEdit(parent=self, ph_text=u"ip address:port number",
                                                   minsize=QSize(0, 20))
    self.tcpClientAddrLineEdit.setObjectName(u"tcpClientAddrLineEdit")

    # Ping Button
    self.pingPushButton = TCPConfigWdgtButton(parent=self, text=u"Ping", minsize=QSize(50, 20))
    self.pingPushButton.setObjectName(u"pingPushButton")

    # Add widgets to layout & set margins
    tcpClientAddrHorizLayout.addWidget(self.tcpClientAddrLineEdit)
    tcpClientAddrHorizLayout.addWidget(self.pingPushButton)
    tcpClientAddrHorizLayout.setContentsMargins(0, 0, 0, 0)
    tcpClientAddrHorizLayout.setSpacing(0)

    # Create TCP Client Connect Horizontal Layout
    tcpClientConnectHorizLayout = QHBoxLayout()
    tcpClientConnectHorizLayout.setObjectName(u"tcpClientConnectHorizLayout")

    # Connect Status Label
    self.connectStatusLED = TCPConfigWdtLabel(parent=self, type="dummy_label", minsize=QSize(10, 0),
                                              maxsize=QSize(10, 10))
    self.connectStatusLED.setObjectName(u"connectStatusLED")

    # Connect Push Button
    self.connectPushButton = TCPConfigWdgtButton(parent=self, text=u"Connect", minsize=QSize(90, 20))
    self.connectPushButton.setCheckable(True)
    self.connectPushButton.setObjectName(u"connectPushButton")

    # Add widgets to layout & set margins
    tcpClientConnectHorizLayout.addWidget(self.connectStatusLED)
    tcpClientConnectHorizLayout.addWidget(self.connectPushButton)
    tcpClientConnectHorizLayout.setContentsMargins(0, 0, 0, 0)
    tcpClientConnectHorizLayout.setSpacing(5)

    # Stacked widget buttons layout
    btnsHorizLayout = self._create_stacked_widget_ctrls_btns_layout()

    # Add widgets to layout & set margins
    connectionsHorizLayout.addLayout(tcpClientAddrHorizLayout)
    connectionsHorizLayout.addLayout(tcpClientConnectHorizLayout)
    connectionsHorizLayout.setContentsMargins(0, 0, 0, 0)
    connectionsHorizLayout.setSpacing(15)

    # Add widgets to layout & set margins
    self.tcpConfigTopVertLayout.addWidget(tcpConfigTitleLabel)
    self.tcpConfigTopVertLayout.addLayout(connectionsHorizLayout)
    self.tcpConfigTopVertLayout.addLayout(btnsHorizLayout)
    self.tcpConfigTopVertLayout.setContentsMargins(0, 0, 0, 0)
    self.tcpConfigTopVertLayout.setSpacing(20)

  def _create_stacked_widget(self) -> None:
    # Create stacked widget
    self.tcpConfigStackedWidget = QStackedWidget(self)
    self.tcpConfigStackedWidget.setObjectName(u"tcpConfigStackedWidget")

    # Create pages
    self.tcpConfigPage = TCPClientConfigPage()

    # Add Pages
    self.tcpConfigStackedWidget.addWidget(self.tcpConfigPage)

  def _create_local_connect(self) -> None:
    # Pushbuttons
    self.connectPushButton.clicked.connect(self._toggle_connect_button)

    # Line Edits
    self.tcpClientAddrLineEdit.editingFinished.connect(
      lambda: self.tcp_client_host_address.emit(str(self.tcpClientAddrLineEdit.text()))
    )

    # TCP Client tree view
    self.tcpConfigPage.treeView.clicked[QModelIndex].connect(
      self.on_tree_view_item_clicked
    )
    self.tcpConfigPage.treeView.invalid_item_selected.connect(
      self.on_tree_view_selection_cleared
    )

  def _create_tcp_widget_worker_thread(self) -> None:
    # Create the Worker & thread
    self.tcp_wdgt_worker_thread = QThread(self)
    self.tcp_wdgt_worker = TCPClientWidgetWorker()
    self.tcp_wdgt_worker.moveToThread(self.tcp_wdgt_worker_thread)

    # Create connections
    self.tcp_wdgt_worker.tcp_client_msg_sent.connect(self._on_status_message_received)

    # Start the worker thread
    self.tcp_wdgt_worker_thread.start()

  def _create_tcp_client_worker_thread(self) -> None:
    # Create the worker & thread
    self.tcp_client_worker_thread = QThread(self)
    self.tcp_client_worker = TCPClientNodeStream()
    self.tcp_client_worker.moveToThread(self.tcp_client_worker_thread)

    # Create connections
    self.tcp_client_host_address.connect(self.tcp_client_worker.set_client_address)
    self.tcp_client_connect.connect(self.tcp_client_worker.client_connect)
    self.tcp_client_disconnect.connect(self.tcp_client_worker.client_disconnect)
    self.tcp_client_quit.connect(self.tcp_client_worker.client_quit)
    self.tcp_client_updated_sock_msg.connect(self.tcp_client_worker.add_payload_to_send_queue)

    self.tcp_client_worker.tcp_client_msg_sent.connect(self._on_status_message_received)
    self.tcp_client_worker.tcp_client_connect_status.connect(self._on_tcp_client_connect_state_change)
    self.tcp_client_worker.tcp_client_sock_msg_rcv.connect(self._on_tcp_client_sock_msg_recv)

    # Start the worker thread
    self.tcp_client_worker_thread.start()

  def _create_data_files_manage_worker_thread(self) -> None:
    # Create thread and the worker
    self.data_files_manage_worker_thread = QThread(self)
    self.data_files_manage_worker = DataFilesManager(data_source='maya')
    self.data_files_manage_worker.moveToThread(self.data_files_manage_worker_thread)

    # Create connections
    self.tcp_client_cache_recvd_data.connect(self.data_files_manage_worker.write_data_to_file)

    # Start the worker thread
    self.data_files_manage_worker_thread.start()

  def _toggle_connect_button(self, checked: bool) -> None:
    if checked:
      self.tcp_client_connect.emit()
    else:
      self.tcp_client_disconnect.emit()

  def _on_tcp_client_connect_state_change(self, state: str) -> None:
    if state == 'Connected':
      self.tcpConfigPage.treeView.clear()
      self.connectStatusLED.setEnabled(True)
      self.connectPushButton.setText("Disconnect")
    elif state == 'Unconnected':
      self.connectStatusLED.setEnabled(False)
      self.connectPushButton.setText("Connect")

  def _on_tcp_client_sock_msg_recv(self, msg_dict: Dict) -> None:
    if msg_dict['MSG_TYPE'] in self.TREE_VIEW_MSGS:
      self.tcpConfigPage.treeView.update_items(msg_dict)
    self.publish_tcp_client_sock_msg.emit(msg_dict)
    if msg_dict['MSG_TYPE'] in self.TREE_VIEW_MSGS[1:]:
      self.tcp_client_cache_recvd_data.emit(msg_dict)

  def _on_status_message_received(self, msg: str) -> None:
    if msg:
      # self.tcpClientStatusBar.showMessage(msg, 5000)
      self.publish_status_message.emit(msg)

  def on_tree_view_item_clicked(self, index: QModelIndex) -> None:
    var = self.tcpConfigPage.treeView.data(index, TCPClientStandardItem.DATA_ROLE)
    TCPClientUiLogger.info(f"Fetched: {var}")
    var_name = var.split(": ")[0]
    var_dt = 'Float'
    var_value = var.split(": ")[1]
    self.publish_selected_var.emit({"Name": var_name, "Type": var_dt, "Value": var_value})

  def on_tree_view_selection_cleared(self):
    TCPClientUiLogger.info("Selection cleared")
    self.publish_selection_clear.emit()

  def on_updated_tcp_data_recvd(self, tcp_msg: Dict={}) -> None:
    TCPClientUiLogger.info(f"Updated TCP message: {tcp_msg}")
    self.tcp_client_updated_sock_msg.emit(tcp_msg)

  def save_state(self):
    TCPClientUiLogger.info(f"TCP Client Widget Exit.")
    self.tcpClientAddrLineEdit.clear()
    self.tcpConfigPage.treeView.clear()
    try:
      # Widget Worker
      if self.tcp_wdgt_worker_thread.isRunning():
        self.tcp_wdgt_worker_thread.quit()
        self.tcp_wdgt_worker_thread.wait()
      # Client Worker
      if self.tcp_client_worker_thread.isRunning():
        self.tcp_client_disconnect.emit()
        self.tcp_client_quit.emit()
        self.tcp_client_worker_thread.quit()
        self.tcp_client_worker_thread.wait()
      # Data files manage Worker
      if self.data_files_manage_worker_thread.isRunning():
        self.data_files_manage_worker_thread.quit()
        self.data_files_manage_worker_thread.wait()
    except Exception:
      TCPClientUiLogger.exception("Unable to close TCP Widget Worker thread because:")

  def closeEvent(self, event: QCloseEvent):
    self.save_state()
    return super().closeEvent(event)


class TCPClientConfigPage(QFrame):

  def __init__(self, parent: QWidget=None, settings: QSettings=None) -> None:
    super(TCPClientConfigPage, self).__init__(parent=parent)

    # Setup the page
    self.setObjectName(u"tcpClientConfigPage")
    if parent is None:
      self.resize(QSize(375, 382))

    self._settings = settings

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    tcpClientConfigVerticalLayout = QVBoxLayout(self)
    tcpClientConfigVerticalLayout.setObjectName(u"tcpClientConfigVerticalLayout")

    # Create layouts & widgets
    self._create_conn_config_group_box()

    # Add widgets to layout & set margins
    tcpClientConfigVerticalLayout.addWidget(self.connConfigGroupBox)
    tcpClientConfigVerticalLayout.setContentsMargins(15, 0, 15, 0)
    tcpClientConfigVerticalLayout.setSpacing(30)

  def _create_conn_config_group_box(self) -> None:
    # Create group box
    self.connConfigGroupBox = QGroupBox(parent=self, title=u"Connectivity Configuration")
    self.connConfigGroupBox.setObjectName(u"connConfigGroupBox")

    # Create layout
    connConfigVerticalLayout = QVBoxLayout(self.connConfigGroupBox)
    connConfigVerticalLayout.setObjectName(u"connConfigVerticalLayout")

    # Create TreeView
    self.treeView = TCPClientTreeView(parent=self.connConfigGroupBox,
                                      settings=self._settings)
    self.treeView.setObjectName(u"connectivityVarsTreeView")

    # Add widgets to layout & set margins
    connConfigVerticalLayout.addWidget(self.treeView)
    connConfigVerticalLayout.setContentsMargins(10, 15, 0, 0)
    connConfigVerticalLayout.setSpacing(6)

    return connConfigVerticalLayout


class TCPClientTreeView(QTreeView):

  invalid_item_selected = Signal()

  def __init__(self, parent: QWidget=None, settings: QSettings=None) -> None:
    super(TCPClientTreeView, self).__init__(parent=parent)

    # Load the settings
    try:
      self._settings = settings
      state = self._settings.value("tcp_tree_state", None)
      if state is not None:
        self.header().restoreState(state)
    except Exception:
      TCPClientUiLogger.info("Working with default settings.")
      pass

    # Setup the Tree View
    self.setAlternatingRowColors(True)
    self.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.setSelectionMode(QAbstractItemView.SingleSelection)

    self.model = TCPClientTreeViewModel()
    self.model.clear()
    self.model.setHorizontalHeaderLabels(['Variable', 'Value'])
    self.setModel(self.model)

  def add_items(self, msg: Dict=None) -> None:
    self.model.add_items(msg)
    self.expandToDepth(0)

  def update_items(self, msg: Dict=None) -> None:
    self.model.update_items(msg)
    self.expandToDepth(0)

  def save_state(self) -> None:
    self._settings.setValue("tcp_tree_state", self.header().saveState())

  def mousePressEvent(self, event: QMouseEvent) -> None:
    item = self.indexAt(event.position().toPoint())
    if not item.isValid():
      self.clearSelection()
      self.invalid_item_selected.emit()
    return super(TCPClientTreeView, self).mousePressEvent(event)

  def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> Any:
    return self.model.data(index, role)

  def clear(self) -> None:
    self.model.clear()


class TCPClientStandardItem(QStandardItem):

  DATA_ROLE = Qt.UserRole + 1

  def __init__(self, text: str='', font_size: int=8, set_bold: bool=False,
               color: QColor=QColor(0, 0, 0)):
    super(TCPClientStandardItem, self).__init__()

    fnt = QFont('MS Shell Dlg 2', font_size)
    fnt.setBold(set_bold)

    self.setEditable(False)
    self.setForeground(color)
    self.setFont(fnt)
    self.setText(text)

  def setToolTip(self, toolTip: str) -> None:
    return super(TCPClientStandardItem, self).setToolTip(toolTip)

  def setData(self, value: Any, role: int) -> None:
    return super(TCPClientStandardItem, self).setData(value, role=role)


class TCPClientTreeViewModel(QStandardItemModel):

  def __init__(self):
    super(TCPClientTreeViewModel, self).__init__()

    self.var_name = None
    self.root_node = self.invisibleRootItem()

  def clear(self) -> None:
    self.removeRows(0, self.rowCount())

  def add_items(self, msg: Union[Dict, None]=None) -> None:
    columns = [TCPClientStandardItem(self.var_name), TCPClientStandardItem(msg['DATA'])]
    for col in columns:
      col.setData(str(msg), TCPClientStandardItem.DATA_ROLE)
      col.setToolTip(str(msg))
    if ',' in msg['DATA']:
      data = [pair.split(" ") for pair in msg['DATA'].split(", ")]
      children = [[TCPClientStandardItem(item) for item in pair.split(" ")]
                  for pair in msg['DATA'].split(", ")]
      for i in range(len(children)):
        for item in children[i]:
          item.setData(self.var_name + "." + data[i][0] + ": " + data[i][1],
                       TCPClientStandardItem.DATA_ROLE)
          item.setToolTip(self.var_name + "." + data[i][0])
        columns[0].appendRow(children[i])
    self.root_node.appendRow(columns)

  def update_items(self, msg: Union[Dict, None]=None) -> None:
    if 'NAME' in msg.keys():
      self.var_name = msg['MSG_TYPE'].split('_')[1] + "_" + msg['NAME']
    else:
      self.var_name = msg['MSG_TYPE']
    var_item = self.findItems(self.var_name)
    if len(var_item) > 0 and len(var_item) < 2:
      var_item[0].setData(str(msg), TCPClientStandardItem.DATA_ROLE)
      val_item = self.itemFromIndex(self.index(var_item[0].row(), 1, QModelIndex()))
      val_item.setData(str(msg), TCPClientStandardItem.DATA_ROLE)
      val_item.setText(msg['DATA'])
      if var_item[0].hasChildren():
        if ',' in msg['DATA']:
          data = [pair.split(" ") for pair in msg['DATA'].split(", ")]
        for row in range(var_item[0].rowCount()):
          child_val_item = var_item[0].child(row, 1)
          child_val_item.setText(data[row][1])
          # child_val_item.setData(data[row][1], TCPClientStandardItem.DATA_ROLE)
    else:
      # Add the variable and value if not found
      self.add_items(msg)


class TCPConfigWdtLabel(QLabel):

  def __init__(self, parent: QWidget=None, text: str='', type: str='', minsize: QSize=None,
               maxsize: QSize=None, align: Qt.AlignmentFlag=None) -> None:
    super(TCPConfigWdtLabel, self).__init__(parent=parent)

    self.setText(text)
    if type == 'dummy_label':
      self.setEnabled(False)
    self.setProperty("type", type)
    if minsize is not None:
      self.setMinimumSize(minsize)
    if maxsize is not None:
      self.setMaximumSize(maxsize)
    if align is not None:
      self.setAlignment(align)

  def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
    return super(TCPConfigWdtLabel, self).mouseReleaseEvent(ev)


class TCPConfigLineEdit(QLineEdit):

  def __init__(self, parent: QWidget=None, ph_text: str='', type: str='', minsize: QSize=None) -> None:
    super(TCPConfigLineEdit, self).__init__(parent=parent)

    if type == 'dummy_line_edit':
      self.setEnabled(False)
    self.setProperty("type", type)
    if minsize is not None:
      self.setMinimumSize(minsize)
    self.setPlaceholderText(ph_text)
    self.setAlignment(Qt.AlignCenter)
    self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))

  def mousePressEvent(self, ev: QMouseEvent) -> None:
    return super(TCPConfigLineEdit, self).mousePressEvent(ev)


class TCPConfigWdgtButton(QPushButton):

  def __init__(self, parent: QWidget=None, text: str='', type: str='', minsize: QSize=None,
               maxsize: QSize=None) -> None:
    super(TCPConfigWdgtButton, self).__init__(parent=parent)

    self.setText(text)
    if type:
      self.setProperty("type", type)
    if minsize is not None:
      self.setMinimumSize(minsize)
    if maxsize is not None:
      self.setMaximumSize(maxsize)

  def mousePressEvent(self, e: QMouseEvent) -> None:
    return super(TCPConfigWdgtButton, self).mousePressEvent(e)


if __name__ == '__main__':
  # For development purpose only
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed QWidget
  tcp_client_widget = TCPClientWidget()
  # Show the widget
  tcp_client_widget.show()
  # execute the program
  sys.exit(app.exec())