## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including MainWindow class.
##
##############################################################################################
##
import os
import sys
import posixpath

from PySide6.QtGui import QKeyEvent, QMouseEvent, QCloseEvent, QResizeEvent, QScreen
from PySide6.QtCore import QSettings, QSize, Signal, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

try:
  from config import AppConfig
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_main.MainWindowTopBar import MainWindowTopBar
  from scripts.ui.widgets_main.MainWindowBottomBar import MainWindowBottomBar
  from scripts.ui.widgets_main.MainWindowContentsArea import MainWindowContentsArea
except:
  # For the development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from config import AppConfig
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_main.MainWindowTopBar import MainWindowTopBar
  from scripts.ui.widgets_main.MainWindowBottomBar import MainWindowBottomBar
  from scripts.ui.widgets_main.MainWindowContentsArea import MainWindowContentsArea


_config = AppConfig()


class UIMainWindowLogger(Logger):

  FILE_NAME = "ui_main_window"
  LOGGER_NAME = "UIMainWindowLogger"


class MainWindow(QMainWindow):

  """
  Subclassed QMainWidow to create MainWindow class. This class manages all the sub-widgets
  and is an entry point to the application.

  Parameters:
    main_window_state: int
      state of the main window i.e. minimized and maximized
    shift_key_pressed: bool
      status of shift key
    alt_key_pressed: bool
      status of alt key
    ctrl_key_pressed: bool
      status of ctrl key

  Arguments:
    parent: QMainWindow
      parent widget
  """

  # Parameters
  main_window_state = 0
  shift_key_pressed = False
  alt_key_pressed = False
  ctrl_key_pressed = False

  # Signals
  request_robot_current_pose = Signal()

  def __init__(self, parent: QMainWindow=None) -> None:
    super(MainWindow, self).__init__(parent=parent)

    # setup Settings for application
    self.settings = QSettings(_config.App['company'], _config.App['name'])
    self._read_settings()

    # Set Window Size, Title and other attributes
    # self.main_window_width, self.main_window_height = self._get_screen_size()
    self.setObjectName(u"mainWindow")
    self.setMinimumSize(QSize(450, 300))
    self.resize(self.main_window_width, self.main_window_height)

    self.centralWidget = QWidget(self)
    self.centralWidget.setObjectName(u"centralWidget")

    self.setWindowFlag(Qt.FramelessWindowHint)
    self.setAttribute(Qt.WA_TranslucentBackground)

    UIMainWindowLogger.info(f"Initiating {_config.App['name']}")
    self.init_UI()

    # Setup central widgets
    self.setCentralWidget(self.centralWidget)

    # Set Main Window default Style
    self.set_stylesheet()

    # Move Window
    def move_window(event):
      if self.main_window_state == 1:
        self._restore_maximize_main()

      # Move window on left click
      if event.buttons() == Qt.LeftButton:
        self.move(self.pos() + event.globalPos() - self.current_pos)
        self.current_pos = event.globalPos()
        event.accept()

    # Set top bar
    self.top_bar.mouseMoveEvent = move_window

    # Welcome message
    self.on_status_message_received(msg=f"Welcome to {_config.App['name']}")

    # It helps to delete old/empty log files
    UIMainWindowLogger.remove_log_files()

  def _get_screen_size(self):
    """
    Method to get the screen size.
    """

    screen = QScreen.availableGeometry(QApplication.primaryScreen())
    return screen.width(), screen.height()

  def _save_settings(self) -> None:
    """
    Method to save the widget's settings to the System's registry.
    """

    self.settings.setValue("main_window_title", _config.App['name'])
    self.settings.setValue("main_window_width", self.size().width())
    self.settings.setValue("main_window_height", self.size().height())
    self.settings.setValue("main_window_state", self.saveState())

  def _read_settings(self) -> None:
    """
    Method to read the widget's settings from System's registry.
    """

    self.main_window_title = str(self.settings.value("main_window_title", _config.App['name']))
    self.main_window_width = int(self.settings.value("main_window_width", 1600))
    self.main_window_height = int(self.settings.value("main_winow_height", 900))

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create main layout
    self.mainVerticalLayout = QVBoxLayout(self.centralWidget)
    self.mainVerticalLayout.setObjectName(u"mainVerticalLayout")

    # Create top bar
    self.top_bar = MainWindowTopBar(parent=self.centralWidget,
                                    logger=UIMainWindowLogger,
                                    height=30)
    # # Create contents area
    self.contents_area = MainWindowContentsArea(parent=self.centralWidget,
                                                logger=UIMainWindowLogger,
                                                settings=self.settings)
    # Create bottom bar
    self.bottom_bar = MainWindowBottomBar(parent=self.centralWidget,
                                          logger=UIMainWindowLogger,
                                          height=30)

    # Create connections
    self._create_local_connects()
    self._create_top_bar_connects()
    self._create_contents_area_connects()

    # Add Widgets to Layout & set margins
    self.mainVerticalLayout.addWidget(self.top_bar)
    self.mainVerticalLayout.addWidget(self.contents_area)
    self.mainVerticalLayout.addWidget(self.bottom_bar)
    self.mainVerticalLayout.setContentsMargins(0, 0, 0, 0)
    self.mainVerticalLayout.setSpacing(0)

  def set_stylesheet(self, theme: str='default', qss: str='MainWindow.qss') -> None:
    """
    Method to set the stylesheet of the widget.

    Arguments:
      theme: str
        style theme: default
      qss: str
        name of the stylesheet file
    """

    qss_file = PathManager.get_qss_path(logger=UIMainWindowLogger,
                                        qss_file=os.path.join(theme, qss))
    if qss_file is None:
      UIMainWindowLogger.warning(f"Invalid qss file received")
      return

    icons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.relpath(qss_file)))),
                              "icons", theme)
    with open(qss_file, 'r') as fh:
      style_sheet = fh.read()
      self.setStyleSheet(style_sheet.replace("<icons_path>",
                                             f"{icons_path}".replace(os.sep, posixpath.sep)))

  def _create_local_connects(self) -> None:
    """
    Method to create connections of local widgets & signals.
    """

    # Signals
    self.request_robot_current_pose.connect(
      self.contents_area.simRobotCtrlWidget.on_current_robot_pose_req_recvd
    )

  def _create_top_bar_connects(self) -> None:
    """
    Method to create connections of widgets from the Top Bar.
    """

    # Top Bar Window Controls
    self.top_bar.minimizePushButton.clicked.connect(lambda: self.showMinimized())
    self.top_bar.maximizePushButton.clicked.connect(lambda: self._restore_maximize_main())
    self.top_bar.closePushButton.clicked.connect(lambda: self.close())

    # Top Bar Menu Signals
    # File Menu Signals
    self.top_bar.exit_main_application.connect(lambda: self.close())

    # Scene Menu Signals
    self.top_bar.add_robot.connect(
      self.contents_area.simRobotCtrlWidget.on_add_robot_req_recvd
    )
    # Window Menu Signals
    self.top_bar.anim_window_change_req.connect(
      self.contents_area.animationCtrlWidget.on_stckd_wdgt_page_chng_req_rcvd
    )

  def _create_contents_area_connects(self):
    """
    Method to create connections of the widgets of contents area.
    """

    # Anim Data Widget
    # self.anim_data_wdgt.publish_status_message.connect(
    #   self.on_status_message_received
    # )
    # self.tcp_client_wdgt.publish_tcp_client_sock_msg.connect(
    #   self.anim_data_wdgt.on_tcp_client_sock_msg_recvd
    # )
    # self.contents_area.anim_data_wdgt.publish_status_message.connect(
    #   self.on_status_message_received
    # )

    pass

  def _restore_maximize_main(self) -> None:
    """
    Method to minimize and maximize the MainWindow.
    """

    if self.main_window_state == 0:
      self.showMaximized()
      self.main_window_state = 1
      self.top_bar.maximizePushButton.setToolTip("Restore")
    elif self.main_window_state == 1:
      self.main_window_state = 0
      self.showNormal()
      self.resize(self.width() + 1, self.height() + 1)
      self.top_bar.maximizePushButton.setToolTip("Maximize")

  def _process_keyboard_commands(self, key: Qt.Key) -> None:
    """
    Method to process various keyboard commands.

    Arguments:
      key: Qt.Key
    """

    # Commands with ctrl key pressed
    if self.ctrl_key_pressed:
      if key == Qt.Key_K:
        self.request_robot_current_pose.emit()

  def on_status_message_received(self, msg: str) -> None:
    """
    Slot/Method called when the status message is received.

    Arguments:
      msg: str
        status message
    """

    self.bottom_bar.statusLabel.setText(msg)

  def mousePressEvent(self, event: QMouseEvent) -> None:
    """
    Method called when the mouse left button is pressed.

    Arguments:
      event: QMouseEvent
        mouse event
    """

    self.current_pos = event.globalPos()

  def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
    """
    Method called when the mouse left button is double clicked.

    Arguments:
      event: QMouseEvent
        mouse event
    """

    if event.button() == Qt.LeftButton:
      self._restore_maximize_main()

  def keyPressEvent(self, event: QKeyEvent) -> None:
    """
    Method called when a key is pressed.

    Arguments:
      event: QKeyEvent
        key event
    """

    if event.isAutoRepeat():
      return

    key = event.key()
    if key == Qt.Key_Shift:
      self.shift_key_pressed = True
    elif key == Qt.Key_Alt:
      self.alt_key_pressed = True
    elif key == Qt.Key_Control:
      self.ctrl_key_pressed = True
    self._process_keyboard_commands(key=key)
    event.accept()
    return super(MainWindow, self).keyPressEvent(event)

  def keyReleaseEvent(self, event: QKeyEvent) -> None:
    """
    Method called when a key is released.

    Arguments:
      event: QKeyEvent
        key event
    """

    if event.isAutoRepeat():
      return

    key = event.key()
    if key == Qt.Key_Shift:
      self.shift_key_pressed = False
    elif key == Qt.Key_Alt:
      self.alt_key_pressed = False
    elif key == Qt.Key_Control:
      self.ctrl_key_pressed = False
    event.accept()
    return super(MainWindow, self).keyReleaseEvent(event)

  def resizeEvent(self, event: QResizeEvent) -> None:
    """
    Method called when the widget is resized.

    event: QResizeEvent
      resize event
    """

    return super(MainWindow,self).resizeEvent(event)

  def save_state(self) -> None:
    """
    Method to save the widget state and perform cleanup before closing.
    """

    self._save_settings()
    self.contents_area.save_state()

  def closeEvent(self, event: QCloseEvent):
    """
    Method called when the widget is resized.

    event: QCloseEvent
      close event
    """

    UIMainWindowLogger.info(f"{_config.App['name']} exit.")
    self.save_state()
    event.accept()
    return super(MainWindow, self).closeEvent(event)


def main():
  """
  Main function to launch the application MainWindow.
  """

  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed QMainWindow
  artemotion = MainWindow()
  # Show the main window
  artemotion.show()
  # execute the program
  sys.exit(app.exec())


if __name__ == '__main__':
  """For development purpose only"""
  # Call the main function
  main()