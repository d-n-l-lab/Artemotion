## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the sub widgets of bottom area of main 3D
##              Widget.
##
##############################################################################################
##
import os
import sys

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QVBoxLayout)

try:
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget, SliderWidget
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget, SliderWidget


class PlayBackCtrlWdgt(QFrame):

  """
  Class to create a sub widget managing the playback control buttons of the main 3D animation.

  Keyword Arguments:
    parent: QWidget
      parent widget of the dialog
    logger: Logger
      logger class
  """

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(PlayBackCtrlWdgt, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Assign attributes to the frame
    self.setObjectName(u"playBackBttnsWdgt")
    if self._parent is None:
      self.resize(QSize(500, 20))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self._init_UI()

  def _init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create layout
    playbackBttnsWdgtLayout = QVBoxLayout(self)
    playbackBttnsWdgtLayout.setObjectName(u"playbackBttnsWdgtLayout")

    # Slider
    self.slider = SliderWidget(parent=self, logger=self._logger)

    # Add widgets to Layout & set margins
    playbackBttnsWdgtLayout.addLayout(self._create_buttons_layout())
    playbackBttnsWdgtLayout.addWidget(self.slider)
    playbackBttnsWdgtLayout.setContentsMargins(2, 2, 2, 2)
    playbackBttnsWdgtLayout.setSpacing(5)

  def _create_reverse_pb_buttons(self) -> QHBoxLayout:
    """
    Method to create reverse playback control buttons.
    """

    # Create Layout
    reverseBttnLayout = QHBoxLayout()
    reverseBttnLayout.setObjectName(u"reverseBttnLayout")

    # Create Buttons
    self.fastRVButton = PushButtonWidget(parent=self, logger=self._logger, type="left_button",
                                         maxsize=QSize(50, 20), text=u"FastR")
    self.fastRVButton.setObjectName(u"fastRVButton")
    # self.fastRVButton.setEnabled(False)

    self.doubleStepRVButton = PushButtonWidget(parent=self, logger=self._logger,
                                               maxsize=QSize(50, 20), text=u"DStepR")
    self.doubleStepRVButton.setObjectName(u"doubleStepRVButton")
    # self.doubleStepRVButton.setEnabled(False)

    self.singleStepRVButton = PushButtonWidget(parent=self, logger=self._logger,
                                               maxsize=QSize(50, 20), text=u"SStepR")
    self.singleStepRVButton.setObjectName(u"singleStepRVButton")
    # self.singleStepRVButton.setEnabled(False)

    self.pauseRVButton = PushButtonWidget(parent=self, logger=self._logger, maxsize=QSize(50, 20),
                                          text=u"PauseR")
    self.pauseRVButton.setObjectName(u"pauseRVButton")
    # self.pauseRVButton.setEnabled(False)

    self.playRVButton = PushButtonWidget(parent=self, logger=self._logger, maxsize=QSize(50, 20),
                                         text=u"PlayR")
    self.playRVButton.setObjectName(u"playRVButton")
    # self.playRVButton.setEnabled(False)

    # Add widgets to Layout & set margins
    reverseBttnLayout.addWidget(self.fastRVButton)
    reverseBttnLayout.addWidget(self.doubleStepRVButton)
    reverseBttnLayout.addWidget(self.singleStepRVButton)
    reverseBttnLayout.addWidget(self.pauseRVButton)
    reverseBttnLayout.addWidget(self.playRVButton)
    reverseBttnLayout.setContentsMargins(0, 0, 0, 0)
    reverseBttnLayout.setSpacing(0)

    return reverseBttnLayout

  def _create_forward_pb_buttons(self) -> QHBoxLayout:
    """
    Method to create forward playback control buttons.
    """

    # Create Layout
    forwardBttnLayout = QHBoxLayout()
    forwardBttnLayout.setObjectName(u"forwardBttnLayout")

    # Create Buttons
    self.fastFWButton = PushButtonWidget(parent=self, logger=self._logger, type="right_button",
                                         maxsize=QSize(50, 20), text=u"FastF")
    self.fastFWButton.setObjectName(u"fastFWButton")
    # self.fastFWButton.setEnabled(False)

    self.doubleStepFWButton = PushButtonWidget(parent=self, logger=self._logger,
                                               maxsize=QSize(50, 20), text=u"DStepF")
    self.doubleStepFWButton.setObjectName(u"doubleStepFWButton")
    # self.doubleStepFWButton.setEnabled(False)

    self.singleStepFWButton = PushButtonWidget(parent=self, logger=self._logger,
                                               maxsize=QSize(50, 20), text=u"SStepF")
    self.singleStepFWButton.setObjectName(u"singleStepFWButton")
    # self.singleStepFWButton.setEnabled(False)

    self.pauseFWButton = PushButtonWidget(parent=self, logger=self._logger, maxsize=QSize(50, 20),
                                          text=u"PauseF")
    self.pauseFWButton.setObjectName(u"pauseFWButton")
    # self.pauseFWButton.setEnabled(False)

    self.playFWButton = PushButtonWidget(parent=self, logger=self._logger, maxsize=QSize(50, 20),
                                         text=u"PlayF")
    self.playFWButton.setObjectName(u"playFWButton")
    # self.playFWButton.setEnabled(False)

    # Add widgets to Layout & set margins
    forwardBttnLayout.addWidget(self.playFWButton)
    forwardBttnLayout.addWidget(self.pauseFWButton)
    forwardBttnLayout.addWidget(self.singleStepFWButton)
    forwardBttnLayout.addWidget(self.doubleStepFWButton)
    forwardBttnLayout.addWidget(self.fastFWButton)
    forwardBttnLayout.setContentsMargins(0, 0, 0, 0)
    forwardBttnLayout.setSpacing(0)

    return forwardBttnLayout

  def _create_buttons_layout(self) -> None:
    """
    Method to create the layout managing the buttons.
    """

    # Create layout
    pbCtrlBttnsLayout = QHBoxLayout()
    pbCtrlBttnsLayout.setObjectName(u"pbCtrlBttnsLayout")

    # Add widgets to Layout & set margins
    pbCtrlBttnsLayout.addLayout(self._create_reverse_pb_buttons())
    pbCtrlBttnsLayout.addLayout(self._create_forward_pb_buttons())
    pbCtrlBttnsLayout.setContentsMargins(0, 0, 0, 0)
    pbCtrlBttnsLayout.setSpacing(0)

    return pbCtrlBttnsLayout

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called when widget is closed.    
    """

    return super(PlayBackCtrlWdgt, self).closeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of top bar
  playback_bttns_wdgt = PlayBackCtrlWdgt(logger=None)
  # Show the top bar
  playback_bttns_wdgt.show()
  # execute the program
  sys.exit(app.exec())