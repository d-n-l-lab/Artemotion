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
import json

from typing import Any, Dict, List, Union

from PySide6.QtGui import (QPainter, QAction, QStandardItemModel, QMouseEvent, QCloseEvent)
from PySide6.QtCore import (QObject, QSettings, QSize, QAbstractItemModel, QPersistentModelIndex,
                            QModelIndex, QPoint, QMimeData, Signal, Qt)
from PySide6.QtWidgets import (QApplication, QFrame, QWidget, QLabel, QDialog, QDialogButtonBox,
                               QCheckBox, QComboBox, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QGroupBox, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem,
                               QHeaderView, QMenu, QSpacerItem, QSizePolicy)

from asyncua import ua
from asyncua.sync import SyncNode, new_node

try:
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget
  from scripts.ui.widgets_sub.SubWidgets import StandardItem
  from scripts.ui.widgets_sub.SubWidgets import LineEditWidget
  from scripts.ui.widgets_sub.SubWidgets import TreeViewWidget
  from scripts.ui.widgets_sub.SubWidgets import TableViewWidget
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget
  from scripts.ui.widgets_sub.SubWidgets import StandardItem
  from scripts.ui.widgets_sub.SubWidgets import LineEditWidget
  from scripts.ui.widgets_sub.SubWidgets import TreeViewWidget
  from scripts.ui.widgets_sub.SubWidgets import TableViewWidget
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget


class OPCUASubUILogger(Logger):

  FILE_NAME = "ui_opcua_sub"
  LOGGER_NAME = "UIOPCUASub"


class EditConnectionDialog(QDialog):

  """
  Class to manage the Edit Connection settings.

  Keyword Argument:
    parent: QWidget
      parent widget
    settings: QSettings
      widget settings

  Parameter:
    dialog_state: int
      state of the dialog widget

  Signals:
    dialog_closed: Signal
      Signal emits when dialog closed
    opcua_server_address: Signal(str)
      Signal emits when OPCUA server address changes
    use_secure_endpoint: Signal(bool)
      Signal emits when secure endpoint requested
    discovery_server_address: Signal(str)
      Signal emits when the discovery server address changes
    browse_certificate_file: Signal()
      Signal emits when browse requests for certificate file received
    certificate_password: Signal(str)
      Signal emits certificate password
    save_certificate_password: Signal(bool)
      Signal emits to request save certificate password
    username: Signal(str)
      Signal emits username
    password: Signal(str)
      Signal emits password
    save_password: Signal(bool)
      Signal emits request to save password
    test_connection: Signal()
      Signal emits to test the connection with the server
  """

  # variables
  dialog_state = 0

  # Signals
  # dialog
  dialog_closed = Signal()
  # server addresses
  opcua_server_address = Signal(str)
  use_secure_endpoint = Signal(bool)
  discovery_server_address = Signal(str)
  # certificate
  browse_certificate_file = Signal()
  certificate_password = Signal(str)
  save_certificate_password = Signal(bool)
  # username & password
  username = Signal(str)
  password = Signal(str)
  save_password = Signal(bool)
  # test connection
  test_connection = Signal()

  def __init__(self, **kwargs) -> None:
    super(EditConnectionDialog, self).__init__(parent=kwargs.get('parent', None))

    # Setup the dialog
    self.setWindowTitle(u"Edit Connection")
    self.setObjectName(u"editConnectionDialog")
    self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
    if kwargs.get('parent', None) is None:
      self.resize(QSize(312, 412))

    # settings
    self._settings = kwargs.get('settings', None)

    self._init_dialog()

    # Move dialog
    def move_dialog(event: QMouseEvent):
      # Move dialog on left click
      if event.buttons() == Qt.LeftButton:
        self.move(self.pos() + event.globalPosition().toPoint() - self.current_pos)
        self.current_pos = event.globalPosition().toPoint()
        event.accept()

    # Set top frame
    self.dlgTitleFrame.mouseMoveEvent = move_dialog

  def _init_dialog(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create Vertical Layout
    editConnectionDlgVertLayout = QVBoxLayout(self)
    editConnectionDlgVertLayout.setObjectName(u"editConnectionDlgVertLayout")

    # Title bar
    self._create_title_bar()

    # Create contents layout
    dlgContentsLayout = QVBoxLayout()
    dlgContentsLayout.setObjectName(u"dlgContentsLayout")

    # Create group boxes
    self._create_connections_group_box()
    self._create_find_servers_group_box()
    self._create_authentication_group_box()
    self._create_buttons_group_box()

    # Add widgets to layout & set margins
    dlgContentsLayout.addWidget(self.connectionsGroupBox)
    dlgContentsLayout.addWidget(self.findServersGroupBox)
    dlgContentsLayout.addWidget(self.authenticationGroupBox)
    dlgContentsLayout.addWidget(self.buttonsGroupBox)
    dlgContentsLayout.setContentsMargins(10, 10, 10, 10)
    dlgContentsLayout.setSpacing(10)

    # Add widgets to layout & set margins
    editConnectionDlgVertLayout.addWidget(self.dlgTitleFrame)
    editConnectionDlgVertLayout.addLayout(dlgContentsLayout)
    editConnectionDlgVertLayout.setContentsMargins(0, 0, 0, 0)
    editConnectionDlgVertLayout.setSpacing(0)

    # Create connections
    self._create_local_connect()

  def _create_title_bar(self) -> None:
    """
    Method to create a title bar frame of the dialog widget.
    """

    # Create dialog title frame
    self.dlgTitleFrame = QFrame(self)
    self.dlgTitleFrame.setObjectName(u"dlgTitleFrame")
    self.dlgTitleFrame.setMaximumSize(QSize(16777215, 30))
    self.dlgTitleFrame.setFrameStyle(QFrame.NoFrame | QFrame.Plain)

    # Title frame layout
    dlgTitleFrameHorizLayout = QHBoxLayout(self.dlgTitleFrame)
    dlgTitleFrameHorizLayout.setObjectName(u"dlgTitleFrameHorizLayout")

    # Spacer
    dlgTitleHorizSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    # Title label
    dlgTitleLabel = LabelWidget(parent=self.dlgTitleFrame, logger=OPCUASubUILogger,
                                text=u"Edit Connections", type="title_label")
    dlgTitleLabel.setObjectName(u"dlgTitleLabel")

    # Minimize button
    self.dlgMinimizeButton = PushButtonWidget(parent=self.dlgTitleFrame, logger=OPCUASubUILogger,
                                              maxsize=QSize(50, 30))
    self.dlgMinimizeButton.setToolTip(u"Minimize")
    self.dlgMinimizeButton.setObjectName(u"dlgMinimizeButton")

    # Minimize button
    self.dlgCloseButton = PushButtonWidget(parent=self.dlgTitleFrame, logger=OPCUASubUILogger,
                                           maxsize=QSize(50, 30))
    self.dlgCloseButton.setToolTip(u"Close")
    self.dlgCloseButton.setObjectName(u"dlgCloseButton")

    # Add widgets to layout & set margins
    dlgTitleFrameHorizLayout.addWidget(dlgTitleLabel)
    dlgTitleFrameHorizLayout.addItem(dlgTitleHorizSpacer)
    dlgTitleFrameHorizLayout.addWidget(self.dlgMinimizeButton)
    dlgTitleFrameHorizLayout.addWidget(self.dlgCloseButton)
    dlgTitleFrameHorizLayout.setContentsMargins(0, 0, 0, 0)
    dlgTitleFrameHorizLayout.setSpacing(0)

  def _create_connections_group_box(self) -> None:
    """
    Method to create a connection group box managing various widgets in a layout.
    """

    # Create group box
    self.connectionsGroupBox = QGroupBox(parent=self, title=u"Connections")
    self.connectionsGroupBox.setObjectName(u"connectionsGroupBox")

    # Create connections form layout
    connectionsFormLayout = QFormLayout(self.connectionsGroupBox)
    connectionsFormLayout.setObjectName(u"connectionsFormLayout")

    # Labels
    serverAddrLabel = LabelWidget(parent=self.connectionsGroupBox, logger=OPCUASubUILogger,
                                  text=u"Server Address", type="sub_label")
    serverAddrLabel.setObjectName(u"serverAddrLabel")

    secureEndpointLabel = LabelWidget(parent=self.connectionsGroupBox, logger=OPCUASubUILogger,
                                      text=u"Use Secure Endpoint", type="sub_label")
    secureEndpointLabel.setObjectName(u"secureEndpointLabel")

    # LineEdits
    self.serverAddrLineEdit = LineEditWidget(parent=self.connectionsGroupBox, logger=OPCUASubUILogger,
                                             ph_text=u"server address", type="data",
                                             minsize=QSize(0, 20))
    self.serverAddrLineEdit.setObjectName(u"serverAddrLineEdit")

    # CheckBox
    self.secureEndpointCheckBox = QCheckBox(parent=self.connectionsGroupBox)
    self.secureEndpointCheckBox.setObjectName(u"secureEndpointCheckBox")
    self.secureEndpointCheckBox.setLayoutDirection(Qt.LeftToRight)

    # Add widgets to layout & set margins
    connectionsFormLayout.setWidget(0, QFormLayout.LabelRole, serverAddrLabel)
    connectionsFormLayout.setWidget(0, QFormLayout.FieldRole, self.serverAddrLineEdit)
    connectionsFormLayout.setWidget(1, QFormLayout.LabelRole, secureEndpointLabel)
    connectionsFormLayout.setWidget(1, QFormLayout.FieldRole, self.secureEndpointCheckBox)
    connectionsFormLayout.setContentsMargins(10, 15, 0, 0)
    connectionsFormLayout.setHorizontalSpacing(6)
    connectionsFormLayout.setVerticalSpacing(6)

  def _create_find_servers_group_box(self) -> None:
    """
    Method to create a find servers group box managing various widgets in a layout.
    """

    # Create group box
    self.findServersGroupBox = QGroupBox(parent=self, title=u"Find Servers")
    self.findServersGroupBox.setObjectName(u"findServersGroupBox")

    # Create find servers form layout
    findServersFormLayout = QFormLayout(self.findServersGroupBox)
    findServersFormLayout.setObjectName(u"findServersFormLayout")

    # Labels
    discoveryServerLabel = LabelWidget(parent=self.findServersGroupBox, logger=OPCUASubUILogger,
                                       text=u"Discovery Server", type="sub_label")
    discoveryServerLabel.setObjectName(u"discoveryServerLabel")

    self.discoveredServerLabel = LabelWidget(parent=self.findServersGroupBox,
                                             logger=OPCUASubUILogger, text=u"Discovered Servers",
                                             type="data_label", minsize=QSize(0, 20),
                                             align=Qt.AlignCenter)
    self.discoveredServerLabel.setObjectName(u"discoveredServerLabel")

    self.discoveryServiceLabel = LabelWidget(parent=self.findServersGroupBox,
                                             logger=OPCUASubUILogger,
                                             text=u"Couldn't access discovery Service",
                                             type="data_label", minsize=QSize(0, 20),
                                             align=Qt.AlignCenter)
    self.discoveryServiceLabel.setObjectName(u"discoveryServiceLabel")

    # LineEdits
    self.discoveryServerLineEdit = LineEditWidget(parent=self.findServersGroupBox,
                                                  logger=OPCUASubUILogger,
                                                  ph_text=u"server address", type="data",
                                                  minsize=QSize(0, 20))
    self.discoveryServerLineEdit.setObjectName(u"discoveryServerLineEdit")

    # Add widgets to layout & set margins
    findServersFormLayout.setWidget(0, QFormLayout.LabelRole, discoveryServerLabel)
    findServersFormLayout.setWidget(0, QFormLayout.FieldRole, self.discoveryServerLineEdit)
    findServersFormLayout.setWidget(1, QFormLayout.SpanningRole, self.discoveredServerLabel)
    findServersFormLayout.setWidget(2, QFormLayout.SpanningRole, self.discoveryServiceLabel)
    findServersFormLayout.setContentsMargins(10, 15, 0, 0)
    findServersFormLayout.setHorizontalSpacing(6)
    findServersFormLayout.setVerticalSpacing(6)

  def _create_certificate_group_box(self) -> None:
    """
    Method to create a certificate group box managing various widgets in a layout.
    """

    # Create group box
    self.certicateGroupBox = QGroupBox(parent=self.authenticationGroupBox, title=u"Certificate")
    self.certicateGroupBox.setCheckable(True)
    self.certicateGroupBox.setChecked(False)
    self.certicateGroupBox.setObjectName(u"certicateGroupBox")

    # Create connections form layout
    certificateFormLayout = QFormLayout(self.certicateGroupBox)
    certificateFormLayout.setObjectName(u"certificateFormLayout")

    # Labels
    usrPrivateKeyLabel = LabelWidget(parent=self.certicateGroupBox, logger=OPCUASubUILogger,
                                     text=u"User Private Key", type="sub_label")
    usrPrivateKeyLabel.setObjectName(u"usrPrivateKeyLabel")

    certPasswordLabel = LabelWidget(parent=self.certicateGroupBox, logger=OPCUASubUILogger,
                                    text=u"Password", type="sub_label")
    certPasswordLabel.setObjectName(u"certPasswordLabel")

    certSavePasswordLabel = LabelWidget(parent=self.certicateGroupBox, logger=OPCUASubUILogger,
                                        text=u"Save Password", type="sub_label")
    certSavePasswordLabel.setObjectName(u"certSavePasswordLabel")

    # LineEdits
    self.usrPrivateKeyLineEdit = LineEditWidget(parent=self.certicateGroupBox,
                                                logger=OPCUASubUILogger,
                                                ph_text=u"user private key",
                                                minsize=QSize(0, 20))
    self.usrPrivateKeyLineEdit.setObjectName(u"usrPrivateKeyLineEdit")

    self.certPasswordLineEdit = LineEditWidget(parent=self.certicateGroupBox,
                                               logger=OPCUASubUILogger,
                                               ph_text=u"password", type="data",
                                               minsize=QSize(0, 20))
    self.certPasswordLineEdit.setObjectName(u"certPasswordLineEdit")

    # PushButton
    self.certBrowsePushButton = PushButtonWidget(parent=self.certicateGroupBox,
                                                 logger=OPCUASubUILogger,
                                                 text=u"...", minsize=QSize(30, 20))
    self.certBrowsePushButton.setObjectName(u"certBrowsePushButton")

    # Layout
    usrPrivateKeyHorizLayout = QHBoxLayout()
    usrPrivateKeyHorizLayout.setObjectName(u"usrPrivateKeyHorizLayout")

    # Add widgets to layout & set margins
    usrPrivateKeyHorizLayout.addWidget(self.usrPrivateKeyLineEdit)
    usrPrivateKeyHorizLayout.addWidget(self.certBrowsePushButton)
    usrPrivateKeyHorizLayout.setContentsMargins(0, 0, 0, 0)
    usrPrivateKeyHorizLayout.setSpacing(0)

    # CheckBox
    self.certSavePasswordCheckBox = QCheckBox(parent=self.certicateGroupBox)
    self.certSavePasswordCheckBox.setObjectName(u"certSavePasswordCheckBox")
    self.certSavePasswordCheckBox.setLayoutDirection(Qt.LeftToRight)

    # Add widgets to layout & set margins
    certificateFormLayout.setWidget(0, QFormLayout.LabelRole, usrPrivateKeyLabel)
    certificateFormLayout.setLayout(0, QFormLayout.FieldRole, usrPrivateKeyHorizLayout)
    certificateFormLayout.setWidget(1, QFormLayout.LabelRole, certPasswordLabel)
    certificateFormLayout.setWidget(1, QFormLayout.FieldRole, self.certPasswordLineEdit)
    certificateFormLayout.setWidget(2, QFormLayout.LabelRole, certSavePasswordLabel)
    certificateFormLayout.setWidget(2, QFormLayout.FieldRole, self.certSavePasswordCheckBox)
    certificateFormLayout.setContentsMargins(10, 15, 0, 0)
    certificateFormLayout.setHorizontalSpacing(6)
    certificateFormLayout.setVerticalSpacing(6)

  def _create_username_group_box(self) -> None:
    """
    Method to create a username group box managing various widgets in a layout.
    """

    # Create group box
    self.usernameGroupBox = QGroupBox(parent=self.authenticationGroupBox, title=u"Username")
    self.usernameGroupBox.setCheckable(True)
    self.usernameGroupBox.setChecked(False)
    self.usernameGroupBox.setObjectName(u"usernameGroupBox")

    # Create find servers form layout
    usernameFormLayout = QFormLayout(self.usernameGroupBox)
    usernameFormLayout.setObjectName(u"usernameFormLayout")

    # Labels
    usernameLabel = LabelWidget(parent=self.usernameGroupBox, logger=OPCUASubUILogger,
                                text=u"Username", type="sub_label")
    usernameLabel.setObjectName(u"usernameLabel")

    passwordLabel = LabelWidget(parent=self.usernameGroupBox, logger=OPCUASubUILogger,
                                text=u"Password", type="sub_label")
    passwordLabel.setObjectName(u"passwordLabel")

    savePasswordLabel = LabelWidget(parent=self.usernameGroupBox, logger=OPCUASubUILogger,
                                    text=u"Save Password", type="sub_label")
    savePasswordLabel.setObjectName(u"savePasswordLabel")

    # LineEdits
    self.usernameLineEdit = LineEditWidget(parent=self.usernameGroupBox,
                                           logger=OPCUASubUILogger, ph_text=u"username",
                                           type="data", minsize=QSize(0, 20))
    self.usernameLineEdit.setObjectName(u"usernameLineEdit")

    self.passwordLineEdit = LineEditWidget(parent=self.usernameGroupBox, logger=OPCUASubUILogger,
                                           ph_text=u"password", type="data",
                                           minsize=QSize(0, 20))
    self.passwordLineEdit.setObjectName(u"passwordLineEdit")

    # CheckBox
    self.savePasswordCheckBox = QCheckBox(self.usernameGroupBox)
    self.savePasswordCheckBox.setObjectName(u"savePasswordCheckBox")
    self.savePasswordCheckBox.setLayoutDirection(Qt.LeftToRight)

    # Add widgets to layout & set margins
    usernameFormLayout.setWidget(0, QFormLayout.LabelRole, usernameLabel)
    usernameFormLayout.setWidget(0, QFormLayout.FieldRole, self.usernameLineEdit)
    usernameFormLayout.setWidget(1, QFormLayout.LabelRole, passwordLabel)
    usernameFormLayout.setWidget(1, QFormLayout.FieldRole, self.passwordLineEdit)
    usernameFormLayout.setWidget(2, QFormLayout.LabelRole, savePasswordLabel)
    usernameFormLayout.setWidget(2, QFormLayout.FieldRole, self.savePasswordCheckBox)
    usernameFormLayout.setContentsMargins(10, 15, 0, 0)
    usernameFormLayout.setHorizontalSpacing(6)
    usernameFormLayout.setVerticalSpacing(6)

  def _create_authentication_group_box(self) -> None:
    """
    Method to create a authentication group box managing various widgets in a
    layout.
    """

    # Create group box
    self.authenticationGroupBox = QGroupBox(parent=self, title=u"Authentication")
    self.authenticationGroupBox.setObjectName(u"authenticationGroupBox")

    # Create vertical layout
    authVerticalLayout = QVBoxLayout(self.authenticationGroupBox)
    authVerticalLayout.setObjectName(u"authVerticalLayout")

    # None RadioButton
    self.noneCheckBox = QCheckBox(parent=self.authenticationGroupBox, text=u"None")
    self.noneCheckBox.setObjectName(u"noneCheckBox")
    self.noneCheckBox.setChecked(True)

    # Create sub group boxes
    self._create_certificate_group_box()
    self._create_username_group_box()

    # Add widgets to layout & set margins
    authVerticalLayout.addWidget(self.noneCheckBox)
    authVerticalLayout.addWidget(self.certicateGroupBox)
    authVerticalLayout.addWidget(self.usernameGroupBox)
    authVerticalLayout.setContentsMargins(10, 15, 0, 0)
    authVerticalLayout.setSpacing(6)

  def _create_buttons_group_box(self):
    """
    Method to create a buttons group box managing various widgets in a layout.
    """

    # Create group box
    self.buttonsGroupBox = QGroupBox(parent=self, title='')
    self.buttonsGroupBox.setObjectName(u"buttonsGroupBox")

    # Create vertical layout
    buttonsVerticalLayout = QVBoxLayout(self.buttonsGroupBox)
    buttonsVerticalLayout.setObjectName(u"buttonsVerticalLayout")

    # Pushbuttons
    self.testConnPushButton = PushButtonWidget(parent=self.buttonsGroupBox, logger=OPCUASubUILogger,
                                               text=u"Test Connection", type="round_button",
                                               minsize=QSize(0, 20))
    self.testConnPushButton.setObjectName(u"testConnPushButton")

    # Horizontal Layout
    btnsHorizontalLayout = QHBoxLayout()
    btnsHorizontalLayout.setObjectName(u"btnsHorizontalLayout")

    # HorizontalSpacer
    horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    # Apply Button
    self.applyPushButton = PushButtonWidget(parent=self.buttonsGroupBox, logger=OPCUASubUILogger,
                                            text=u"Apply", type="round_button",
                                            minsize=QSize(50, 20))
    self.applyPushButton.setObjectName(u"applyPushButton")

    # Cancel Button
    self.cancelPushButton = PushButtonWidget(parent=self.buttonsGroupBox, logger=OPCUASubUILogger,
                                             text=u"Cancel", type="round_button",
                                             minsize=QSize(50, 20))
    self.cancelPushButton.setObjectName(u"cancelPushButton")

    # Add widgets to layout & set margins
    btnsHorizontalLayout.addItem(horizontalSpacer)
    btnsHorizontalLayout.addWidget(self.applyPushButton)
    btnsHorizontalLayout.addWidget(self.cancelPushButton)
    btnsHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    btnsHorizontalLayout.setSpacing(5)

    # Add widgets to layout & set margins
    buttonsVerticalLayout.addWidget(self.testConnPushButton)
    buttonsVerticalLayout.addLayout(btnsHorizontalLayout)
    buttonsVerticalLayout.setContentsMargins(10, 15, 0, 0)
    buttonsVerticalLayout.setSpacing(15)

  def _create_local_connect(self):
    """
    Method to create connections of signals of the local widgets to the respective slots.
    """

    # PushButtons
    self.dlgMinimizeButton.clicked.connect(lambda: self.showMinimized())
    self.dlgCloseButton.clicked.connect(lambda: self.close())
    self.applyPushButton.clicked.connect(self._apply_changes)
    self.cancelPushButton.clicked.connect(self._cancel_changes)
    self.certBrowsePushButton.clicked.connect(lambda: self.browse_certificate_file.emit())
    self.testConnPushButton.clicked.connect(lambda: self.test_connection.emit())

    # CheckBoxes
    self.noneCheckBox.clicked.connect(self._on_none_checkbox_clicked)
    self.certicateGroupBox.clicked.connect(self._on_certificate_group_box_clicked)
    self.usernameGroupBox.clicked.connect(self._on_username_group_box_clicked)

  def _on_none_checkbox_clicked(self) -> None:
    """
    Method to process the event when the none checkbox selection changed.
    """

    self.noneCheckBox.setChecked(True)
    self.certicateGroupBox.setChecked(False)
    self.usernameGroupBox.setChecked(False)

  def _on_certificate_group_box_clicked(self) -> None:
    """
    Method to process the event when certificate groupbox checkbox selection changed.
    """

    self.noneCheckBox.setChecked(False)
    self.certicateGroupBox.setChecked(True)
    self.usernameGroupBox.setChecked(False)

  def _on_username_group_box_clicked(self) -> None:
    """
    Method to process the event when username groupbox checkbox selection changed.
    """

    self.noneCheckBox.setChecked(False)
    self.certicateGroupBox.setChecked(False)
    self.usernameGroupBox.setChecked(True)

  def _apply_changes(self):
    """
    Method to process the event when apply pushbutton pressed.
    """

    # Signals
    # server addresses
    self.opcua_server_address.emit(self.serverAddrLineEdit.text())
    self.discovery_server_address.emit(self.discoveryServerLineEdit.text())
    # certificate
    if self.certicateGroupBox.isChecked():
      self.certificate_password.emit(self.certPasswordLineEdit.text())
      self.save_certificate_password.emit(self.certSavePasswordCheckBox.isChecked())
    # username & password
    if self.usernameGroupBox.isChecked():
      self.username.emit(self.usernameLineEdit.text())
      self.password.emit(self.passwordLineEdit.text())
      self.save_password.emit(self.savePasswordCheckBox.isChecked())
    self.close()

  def _cancel_changes(self):
    """
    Method to process the event when cancel pushbutton pressed.
    """

    self.close()

  def mousePressEvent(self, event: QMouseEvent) -> None:
    """
    Method called on mouse press Event.
    """

    self.current_pos = event.globalPosition().toPoint()
    return super(EditConnectionDialog, self).mousePressEvent(event)

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called on Close Event.
    """

    self.dialog_closed.emit()
    return super(EditConnectionDialog, self).closeEvent(event)


class ServerAddressDialog(QDialog):

  """
  Class to manage the Server Address Dialog Widget.

  Keyword Argument:
    parent: QWidget
      parent widget
    settings: QSettings
      widget settings
    logger: Logger)
      logger class

  Parameter:
    dialog_state: int
      state of the dialog widget

  Signals:
    dialog_closed: Signal
      Signal emits when dialog closed
  """

  dialog_closed = Signal()

  def __init__(self, **kwargs):
    super().__init__(parent=kwargs.get('parent', None))

    self.setWindowTitle("Enter URL")

    self._init_dialog()
    # self._create_local_connect()

  def _init_dialog(self) -> None:
    """
    Method to initialize the UI.
    """

    # Layout
    self.layout = QVBoxLayout(self)
    self.layout.setObjectName(u"serverAddrDialogLayout")

    # Create label
    commandLabel = QLabel("Enter the URL of a computer with discovery service running:")
    commandLabel.setObjectName(u"commandLabel")

    # Create ComboBox with LineEdit
    self.serverAddrComboBox = QComboBox()
    self.serverAddrComboBox.setEditable(True)
    self.serverAddrComboBox.addItems(["opc.tcp://", "https://", "http://"])
    self.serverAddrComboBox.setObjectName(u"serverAddrComboBox")

    # Create Buttonbox
    QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
    self.buttonBox = QDialogButtonBox(QBtn)

    # Add widgets to layout
    self.layout.addWidget(commandLabel)
    self.layout.addWidget(self.serverAddrComboBox)
    self.layout.addWidget(self.buttonBox)

  def closeEvent(self, ev: QCloseEvent) -> None:
    """
    Method called on Close Event.
    """

    self.dialog_closed.emit()
    return super(ServerAddressDialog, self).closeEvent(ev)


class OPCUAStandardItem(StandardItem):

  NODE_ROLE = Qt.UserRole + 2


class OPCUAConfigDelegate(QStyledItemDelegate):

  connect_btn_clicked = Signal(bool)
  in_dir_enable_btn_clicked = Signal(bool)
  out_dir_enable_btn_clicked = Signal(bool)

  def __init__(self, parent: QObject=None) -> None:
    super(OPCUAConfigDelegate, self).__init__(parent=parent)

    self._pressed = None
    self.setObjectName(u"opcUAConfigDelegate")

  def paint(self, painter: QPainter, option: QStyleOptionViewItem,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    if isinstance(self.parent(), QAbstractItemView) and self.parent().model is index.model():
      self.parent().openPersistentEditor(index)
    return super(OPCUAConfigDelegate, self).paint(painter, option, index)

  def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    if not index.isValid():
      return

    item_data = json.loads(
      index.data(role=OPCUAStandardItem.DATA_ROLE)
    )
    if item_data['type'] == 'server' and index.column() == 1:
      # Create button widget
      connectBtnWdgt = QWidget(parent=parent)
      connectBtnWdgt.setObjectName(u"connectBtnWdgt")

      # Create layout
      connectBtnLayout = QHBoxLayout(connectBtnWdgt)
      connectBtnLayout.setObjectName(u"connectBtnLayout")

      # Create spacer
      connectBtnSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

      # Create connect button
      self.connectButton = PushButtonWidget(parent=connectBtnWdgt, maxsize=QSize(20, 20))
      self.connectButton.setCheckable(True)
      self.connectButton.setObjectName(u"connectButton")
      self.connectButton.setToolTip(u"Connect")
      self.connectButton.clicked.connect(lambda checked: self.connect_btn_clicked.emit(checked))

      # Add widgets to layout & set margins
      connectBtnLayout.addItem(connectBtnSpacer)
      connectBtnLayout.addWidget(self.connectButton)
      connectBtnLayout.setContentsMargins(0, 0, 0, 0)
      connectBtnLayout.setSpacing(0)

      return connectBtnWdgt

    if item_data['type'] == 'data_in_direction' and index.column() == 1:
      # Create in direction widget
      inDirectionWdgt = QWidget(parent=parent)
      inDirectionWdgt.setObjectName(u"inDirectionWdgt")

      # Create layout
      inDirectionLayout = QHBoxLayout(inDirectionWdgt)
      inDirectionLayout.setObjectName(u"inDirectionLayout")

      # Create spacer
      inDirectionSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

      # Create label
      inDirectionLabel = LabelWidget(parent=inDirectionWdgt, maxsize=QSize(20, 20),
                                     align=Qt.AlignCenter)
      inDirectionLabel.setObjectName(u"inDirectionLabel")

      # Create button
      self.inDirEnableBtn = PushButtonWidget(parent=inDirectionWdgt, maxsize=QSize(20, 20))
      self.inDirEnableBtn.setCheckable(True)
      self.inDirEnableBtn.setToolTip(u"Enable")
      self.inDirEnableBtn.setObjectName(u"inDirEnableBtn")
      self.inDirEnableBtn.clicked.connect(
        lambda checked: self.in_dir_enable_btn_clicked.emit(checked)
      )

      # Add widgets to layout & set margins
      inDirectionLayout.addItem(inDirectionSpacer)
      inDirectionLayout.addWidget(inDirectionLabel)
      inDirectionLayout.addWidget(self.inDirEnableBtn)
      inDirectionLayout.setContentsMargins(0, 0, 0, 0)
      inDirectionLayout.setSpacing(0)

      return inDirectionWdgt

    if item_data['type'] == 'data_out_direction' and index.column() == 1:
      # Create in direction widget
      outDirectionWdgt = QWidget(parent=parent)
      outDirectionWdgt.setObjectName(u"outDirectionWdgt")

      # Create layout
      outDirectionLayout = QHBoxLayout(outDirectionWdgt)
      outDirectionLayout.setObjectName(u"outDirectionLayout")

      # Create spacer
      outDirectionSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

      # Create label
      outDirectionLabel = LabelWidget(parent=outDirectionWdgt, maxsize=QSize(20, 20),
                                      align=Qt.AlignCenter)
      outDirectionLabel.setObjectName(u"outDirectionLabel")

      # Create button
      self.outDirEnableBtn = PushButtonWidget(parent=outDirectionWdgt, maxsize=QSize(20, 20))
      self.outDirEnableBtn.setCheckable(True)
      self.outDirEnableBtn.setToolTip(u"Enable")
      self.outDirEnableBtn.setObjectName(u"outDirEnableBtn")
      self.outDirEnableBtn.clicked.connect(
        lambda checked: self.out_dir_enable_btn_clicked.emit(checked)
      )

      # Add widgets to layout & set margins
      outDirectionLayout.addItem(outDirectionSpacer)
      outDirectionLayout.addWidget(outDirectionLabel)
      outDirectionLayout.addWidget(self.outDirEnableBtn)
      outDirectionLayout.setContentsMargins(0, 0, 0, 0)
      outDirectionLayout.setSpacing(0)

      return outDirectionWdgt

  def setEditorData(self, editor: QWidget,
                    index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    return super(OPCUAConfigDelegate, self).setEditorData(editor, index)

  def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    return super(OPCUAConfigDelegate, self).setModelData(editor, model, index)

  def sizeHint(self, option: QStyleOptionViewItem,
               index: Union[QModelIndex, QPersistentModelIndex]) -> QSize:
    size = super(OPCUAConfigDelegate, self).sizeHint(option, index)
    size.setHeight(20)
    return size


class OPCUAConfigTreeModel(QStandardItemModel):

  def __init__(self) -> None:
    super(OPCUAConfigTreeModel, self).__init__()

    self.root_node = self.invisibleRootItem()

  def clear(self) -> None:
    # Remove all rows but not the header
    self.removeRows(0, self.rowCount())

  def add_items(self, item: Union[Dict, None]=None,
                parent: Union[OPCUAStandardItem, None]=None) -> None:
    if item is None:
      return
    columns = [OPCUAStandardItem(text=item['name'], tooltip=item['name']),
               OPCUAStandardItem(tooltip=item['type'])]
    for col in columns:
      col.setData(json.dumps(item), OPCUAStandardItem.DATA_ROLE)
    if len(item['children']) > 0:
      for child in item['children']:
        child_columns = [OPCUAStandardItem(text=child['name'], tooltip=child['name']),
                         OPCUAStandardItem(tooltip=child['type'])]
        for col in child_columns:
          col.setData(json.dumps(child), OPCUAStandardItem.DATA_ROLE)
          # col.setToolTip(str(child['name']))
        columns[0].appendRow(child_columns)
        if len(child['children']) > 0:
          self.add_items(child['children'], child)
    if parent is None:
      self.root_node.appendRow(columns)
    else:
      parent.appendRow(columns)

  def update_items(self, item: Union[Dict, None]=None, upd_item: Union[Dict, None]=None,
                   parent: Union[OPCUAStandardItem, None]=None) -> None:
    if upd_item is None:
      return
    item_node = self.findItems(item['name'])
    if len(item_node) > 0 and len(item_node) < 2:
      self.removeRow(item_node[0].row(), item_node[0].parent())
      self.add_items(upd_item, parent)
    else:
      # Add the variable and value if not found
      self.add_items(item, parent)


class OPCUAConfigTreeView(TreeViewWidget):

  # Server Signals
  show_server_variables = Signal()
  remove_server = Signal()
  # Data flow Signals
  show_connected_variables = Signal()
  add_variables_pairs = Signal()
  remove_data_flow_group = Signal()

  def __init__(self, **kwargs) -> None:
    kwargs['tree_name'] = 'opc_config_tree'
    kwargs['tree_model'] = OPCUAConfigTreeModel()
    super(OPCUAConfigTreeView, self).__init__(**kwargs)

    # Delegate
    self.opcUAConfigDelegate = OPCUAConfigDelegate(parent=self)

    # setup the Tree View
    self.setItemDelegate(self.opcUAConfigDelegate)
    self.setContextMenuPolicy(Qt.CustomContextMenu)
    self.customContextMenuRequested.connect(self.open_menu)

    # Add protocol item
    try:
      item = json.loads('{"name": "OPC UA", "type": "protocol", "children": []}')
      self.add_items(var=item)
    except Exception:
      OPCUASubUILogger.exception("Unable to update item because:")

  def add_items(self, var: Dict=None, parent: OPCUAStandardItem=None) -> None:
    self.model.add_items(var, parent)
    self.header().resizeSection(0, 200)
    self.expandAll()

  def update_items(self, item: Dict=None, upd_item: Dict=None, parent: OPCUAStandardItem=None) -> None:
    self.model.update_items(item=item, upd_item=upd_item, parent=parent)
    self.header().resizeSection(0, 200)
    self.expandAll()

  def open_menu(self, pos: QPoint) -> None:
    indexes = self.selectedIndexes()
    if len(indexes) > 0:
      if not indexes[0].isValid():
        OPCUASubUILogger.info("Invalid index")
        return

      try:
        item = json.loads(self.data(indexes[0], OPCUAStandardItem.DATA_ROLE))
        if item['type'] == 'server':
          menu = QMenu(parent=self)
          menu.setObjectName(u"serverVarsConfigMenu")
          showVarAction = QAction(text=u"Show Variables", parent=self)
          removeAction = QAction(text=u"Remove Server", parent=self)
          menu.addActions([showVarAction, removeAction])

          # Connections
          showVarAction.triggered.connect(lambda: self.show_server_variables.emit())
          removeAction.triggered.connect(lambda: self.remove_server.emit())
          menu.exec(self.viewport().mapToGlobal(pos))
        if item['type'] == 'data_in_direction' or item['type'] == 'data_out_direction':
          menu = QMenu(parent=self)
          menu.setObjectName(u"connVarsConfigMenu")
          showVarAction = QAction(text=u"Show Variables", parent=self)
          addVarAction = QAction(text=u"Add Variables", parent=self)
          removeAction = QAction(text=u"Remove Group", parent=self)
          menu.addActions([showVarAction, addVarAction, removeAction])

          # Connections
          showVarAction.triggered.connect(lambda: self.show_connected_variables.emit())
          addVarAction.triggered.connect(lambda: self.add_variables_pairs.emit())
          removeAction.triggered.connect(lambda: self.remove_data_flow_group.emit())
          menu.exec(self.viewport().mapToGlobal(pos))
      except Exception:
        OPCUASubUILogger.exception("Unable to create context menu because:")


class OPCUAVarsTreeModel(QStandardItemModel):

  def __init__(self) -> None:
    super(OPCUAVarsTreeModel, self).__init__()

    self._fetched = []

  def clear(self) -> None:
    # Remove all rows but not the header
    self.removeRows(0, self.rowCount())
    self._fetched = []

  def _get_node_description(self, node: SyncNode) -> ua.ReferenceDescription:
    attributes = node.read_attributes([ua.AttributeIds.DisplayName, ua.AttributeIds.BrowseName,
                                       ua.AttributeIds.NodeId, ua.AttributeIds.NodeClass])
    description = ua.ReferenceDescription()
    description.DisplayName = attributes[0].Value.Value
    description.BrowseName = attributes[1].Value.Value
    description.NodeId = attributes[2].Value.Value
    description.NodeClass = attributes[3].Value.Value
    description.TypeDefinition = ua.TwoByteNodeId(ua.ObjectIds.FolderType)

    return description

  def _create_items(self, desc: ua.ReferenceDescription=None) -> List[OPCUAStandardItem]:
    disp_name = browse_name = node_id = "No Value"
    if desc is None:
      return None

    if desc.DisplayName:
      disp_name = desc.DisplayName.Text
    if desc.BrowseName:
      browse_name = desc.BrowseName.to_string()
    node_id = desc.NodeId.to_string()

    # To DO: Add logic for adding icons

    items = [OPCUAStandardItem(text=disp_name, tooltip=node_id),
             OPCUAStandardItem(text=browse_name, tooltip=node_id),
             OPCUAStandardItem(text=node_id, tooltip=node_id)]

    return items

  def _fetchMore(self, parent: OPCUAStandardItem) -> None:
    try:
      node = parent.data(OPCUAStandardItem.NODE_ROLE)
      description = node.get_children_descriptions()
      description.sort(key=lambda x: x.BrowseName)
      added = []
      for desc in description:
        if not desc.NodeId in added:
          self.add_item(desc, parent)
          added.append(desc.NodeId)
    except Exception:
      OPCUASubUILogger.exception(f"Unable to add node because:")

  def reset_cache(self, node: SyncNode) -> None:
    if node in self._fetched:
      self._fetched.remove(node)

  def set_root_node(self, node: SyncNode) -> None:
    desc = self._get_node_description(node)
    self.add_item(desc, node=node)

  def add_item(self, desc: ua.ReferenceDescription, parent: OPCUAStandardItem=None,
               node: SyncNode=None) -> None:
    items = self._create_items(desc=desc)
    if node:
      [item.setData(node, OPCUAStandardItem.NODE_ROLE) for item in items]
    else:
      parent_node = parent.data(OPCUAStandardItem.NODE_ROLE)
      [item.setData(new_node(parent_node, desc.NodeId), OPCUAStandardItem.NODE_ROLE)
       for item in items]

    if parent:
      return parent.appendRow(items)
    else:
      return self.appendRow(items)

  def canFetchMore(self, index: Union[QModelIndex, QPersistentModelIndex]) -> bool:
    item = self.itemFromIndex(index)
    if not item:
      return False
    node = item.data(OPCUAStandardItem.NODE_ROLE)
    if node not in self._fetched:
      self._fetched.append(node)
      return True
    return False

  def fetchMore(self, index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    parent = self.itemFromIndex(index)
    if parent:
      self._fetchMore(parent)

  def hasChildren(self, index: Union[QModelIndex, QPersistentModelIndex]) -> bool:
    item = self.itemFromIndex(index)
    if not item:
      return True
    node = item.data(OPCUAStandardItem.NODE_ROLE)
    if node in self._fetched:
      return QStandardItemModel.hasChildren(self, index)
    return True

  def mimeData(self, indexes: List[int]) -> QMimeData:
    mime_data = QMimeData()
    nodes = []
    for index in indexes:
      item = self.itemFromIndex(index)
      if item:
        node = item.data(OPCUAStandardItem.NODE_ROLE)
        if node:
          nodes.append(node.nodeid.to_string())
    mime_data.setText(", ".join(nodes))
    return mime_data


class OPCUAVarsTreeView(TreeViewWidget):

  def __init__(self, **kwargs) -> None:
    kwargs['tree_model'] = OPCUAVarsTreeModel()
    super(OPCUAVarsTreeView, self).__init__(**kwargs)

    # setup the Tree View
    self.header().setStretchLastSection(True)
    self.header().setSectionResizeMode(QHeaderView.Interactive)

    self.actionReload = QAction("&Reload", self)
    self.actionReload.triggered.connect(self.reload_current)

  def set_root_node(self, node):
    self.model.clear()
    self.model.set_root_node(node)
    self.expandToDepth(0)

  def get_current_node(self, index: Union[QModelIndex, QPersistentModelIndex]=None) -> Any:
    if index is None:
      index = self.currentIndex()
    index = index.sibling(index.row(), 0)
    item = self.model.itemFromIndex(index)
    if not item:
      return None
    node = item.data(OPCUAStandardItem.NODE_ROLE)
    if not node:
      OPCUASubUILogger.error("Item does not contain data, report!")
    return node

  def copy_nodeid(self) -> None:
    node = self.get_current_node()
    text = node.nodeid.to_string()
    QApplication.clipboard().setText(text)

  def get_current_path(self) -> List:
    index = self.currentIndex()
    index = index.sibling(index.row(), 0)
    item = self.model.itemFromIndex(index)
    path = []
    while item and item.data(OPCUAStandardItem.NODE_ROLE):
      node = item.data(OPCUAStandardItem.NODE_ROLE)
      name = node.read_browse_name().to_string()
      path.insert(0, name)
      item = item.parent()
    return path

  def copy_path(self) -> None:
    path = self.get_current_path()
    path_str = ",".join(path)
    QApplication.clipboard().setText(path_str)

  def reload_current(self) -> None:
    pass


class OPCUATableModel(QStandardItemModel):

  def __init__(self) -> None:
    super(OPCUATableModel, self).__init__()

    self.root_node = self.invisibleRootItem()

  def clear(self) -> None:
    self.removeRows(0, self.rowCount())

  def add_item(self, data: Any) -> None:
    pass

  def update_item(self, data: Any) -> None:
    pass


class OPCUAAttrsTableView(TableViewWidget):

  def __init__(self, **kwargs) -> None:
    kwargs['table_name'] = 'opcua_attrs_table'
    kwargs['table_model'] = OPCUATableModel()
    kwargs['header_labels'] = ['Attribute', 'Value', 'DataType']
    super(OPCUAAttrsTableView, self).__init__(**kwargs)


class OPCUASubsTableView(TableViewWidget):

  def __init__(self, **kwargs) -> None:
    kwargs['table_name'] = 'opcua_subs_table'
    kwargs['table_model'] = OPCUATableModel()
    kwargs['header_labels'] = ['DisplayName', 'Value', 'Timestamp']
    super(OPCUASubsTableView, self).__init__(**kwargs)


if __name__ == '__main__':
  # For development purpose only
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  app.setAttribute(Qt.AA_UseHighDpiPixmaps)
  # Create an instance of subclassed QWidget
  edit_conn_dialog = EditConnectionDialog()
  # Show the widget
  edit_conn_dialog.show()
  # execute the program
  sys.exit(app.exec())