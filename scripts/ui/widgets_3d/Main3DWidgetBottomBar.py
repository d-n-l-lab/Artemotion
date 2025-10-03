## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the bottom 3D area widget.
##
##############################################################################################
##
import os
import sys

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QTimer, QSize, Signal, Qt
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy)

try:
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.Main3DBottomSubWidgets import PlayBackCtrlWdgt
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.Main3DBottomSubWidgets import PlayBackCtrlWdgt


class DummyLogger(Logger):

  pass


class Main3DWidgetBottomBar(QFrame):

  """
  Class to manage the widgets included in the Main 3D Widget bottom bar.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      settings of the widget
    logger: Logger
      Logger class
    height: int
      height of the bar


  Signals:
    main_3d_playback_control: Signal(str)
      signal emitted when control of playback is requested
  """

  main_3d_playback_control = Signal(str)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(Main3DWidgetBottomBar, self).__init__(parent=self._parent)

    self._logger = kwargs['logger']
    self._height = kwargs.get('height', 40)

    # Setup the bottom bar
    self.setObjectName(u"main3DWidgetBottomBar")
    self.setMinimumSize(QSize(0, self._height))
    self.setMaximumSize(QSize(16777215, self._height))
    self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

    # Get the widget settings
    self._settings = kwargs.get('settings', None)
    if self._settings is not None:
      self.read_settings()

    # Playback Attributes
    self._pb_dir = 'fwd'

    self.init_UI()

    # Connections
    self._create_local_connects()

    # Widgets connections
    self._create_playback_widget_connections()

    # Create timer
    self.animation_timer = QTimer(self)
    self.animation_timer.setInterval(1)
    self.animation_timer.setTimerType(Qt.PreciseTimer)
    self.animation_timer.timeout.connect(lambda: self.main_3d_playback_control.emit(self._pb_dir))

  def init_UI(self) -> None:
    """
    Method to initialize the widget.
    """

    # Create horizontal layout
    main3DBottomBarHorizLayout = QHBoxLayout(self)
    main3DBottomBarHorizLayout.setObjectName(u"main3DBottomBarHorizLayout")

    dummySpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    self.pb_ctrl_wdgt = PlayBackCtrlWdgt(parent=self, logger=self._logger)

    # Add widgets to the layout & set margins
    main3DBottomBarHorizLayout.addItem(dummySpacer)
    main3DBottomBarHorizLayout.addWidget(self.pb_ctrl_wdgt)
    main3DBottomBarHorizLayout.addItem(dummySpacer)
    main3DBottomBarHorizLayout.setContentsMargins(0, 0, 0, 0)
    main3DBottomBarHorizLayout.setSpacing(0)

  def read_settings(self) -> None:
    """
    Method responsible to read the Widget settings.
    """

    pass

  def _create_local_connects(self) -> None:
    """
    Method to create connections of signals of the local widgets to the respective slots.
    """

    pass

  def _create_playback_widget_connections(self) -> None:
    """
    Method to create connections of the signals of the playback widgets.
    """

    # Forward Controls
    self.pb_ctrl_wdgt.fastFWButton.clicked.connect(
      lambda: self.main_3d_playback_control.emit('fast_fw')
    )
    self.pb_ctrl_wdgt.doubleStepFWButton.clicked.connect(
      lambda: self.main_3d_playback_control.emit('double')
    )
    self.pb_ctrl_wdgt.singleStepFWButton.clicked.connect(
      lambda: self.main_3d_playback_control.emit('fwd')
    )
    self.pb_ctrl_wdgt.pauseFWButton.clicked.connect(
      lambda: self.animation_timer.stop()
    )
    self.pb_ctrl_wdgt.playFWButton.clicked.connect(
      lambda: self.on_animation_pb_initiated(dir='fwd')
    )

    # Reverse Controls
    self.pb_ctrl_wdgt.fastRVButton.clicked.connect(
      lambda: self.main_3d_playback_control.emit('fast_rv')
    )
    self.pb_ctrl_wdgt.doubleStepRVButton.clicked.connect(
      lambda: self.main_3d_playback_control.emit('double')
    )
    self.pb_ctrl_wdgt.singleStepRVButton.clicked.connect(
      lambda: self.main_3d_playback_control.emit('bwd')
    )
    self.pb_ctrl_wdgt.pauseRVButton.clicked.connect(
      lambda: self.animation_timer.stop()
    )
    self.pb_ctrl_wdgt.playRVButton.clicked.connect(
      lambda: self.on_animation_pb_initiated(dir='bwd')
    )

  def on_animation_pb_initiated(self, dir: str) -> None:
    """
    Slot/Method called when the playback is initiated.

    Arguments:
      dir: str
        playback direction
    """

    self._pb_dir = dir
    if not self.animation_timer.isActive():
      self.animation_timer.start()

  def on_animation_pb_finished(self) -> None:
    """
    Slot/Method called when playback of animation is completed.
    """

    self.animation_timer.stop()

  def save_state(self) -> None:
    """
    Method to save the widget state and perform cleanup before closing.
    """

    pass

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called on Close Event.
    """

    self.save_state()
    return super(Main3DWidgetBottomBar, self).closeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of top bar
  bottom_bar = Main3DWidgetBottomBar(logger=DummyLogger)
  # It helps to delete old/empty log files
  bottom_bar._logger.remove_log_files()
  # Show the top bar
  bottom_bar.show()
  # execute the program
  sys.exit(app.exec())