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

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QLabel, QSizeGrip

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))))
  from scripts.settings.Logger import Logger


class DummyLogger(Logger):

  pass


class MainWindowBottomBar(QFrame):

  def __init__(self, parent: QWidget=None, logger: Logger=DummyLogger, height: int=30) -> None:
    super(MainWindowBottomBar, self).__init__(parent=parent)

    self._logger = logger
    self._height = height

    # Setup the bottom bar
    self.setObjectName(u"mainWindowBottomBar")
    self.setFrameShape(QFrame.NoFrame)
    self.setFrameShadow(QFrame.Raised)
    self.setMaximumSize(QSize(16777215, self._height))

    self.init_UI()

  def init_UI(self):
    # Create bottom bar layout
    bottomBarHorizontalLayout = QHBoxLayout(self)
    bottomBarHorizontalLayout.setObjectName(u"bottomBarHorizontalLayout")

    # Details frame
    self._create_details_frame()

    # Status frame
    self._create_status_frame()

    # Version frame
    self._create_version_frame()

    # Grip frame
    self._create_grip_frame()

    # Add Widgets to Layout & set margins
    bottomBarHorizontalLayout.addWidget(self.detailsFrame)
    bottomBarHorizontalLayout.addWidget(self.statusFrame)
    bottomBarHorizontalLayout.addWidget(self.versionFrame)
    bottomBarHorizontalLayout.addWidget(self.gripFrame)
    bottomBarHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    bottomBarHorizontalLayout.setSpacing(0)

  def _create_details_frame(self):
    # Create details frame
    self.detailsFrame = QFrame(self)
    self.detailsFrame.setObjectName(u"detailsFrame")
    self.detailsFrame.setFrameShape(QFrame.NoFrame)
    self.detailsFrame.setFrameShadow(QFrame.Raised)
    self.detailsFrame.setMaximumSize(QSize(250, self._height))

    # Create details frame layout
    detailsFrameHorizontalLayout = QHBoxLayout(self.detailsFrame)
    detailsFrameHorizontalLayout.setObjectName(u"detailsFrameHorizontalLayout")

    # Create details label
    self.detailsLabel = QLabel(self.detailsFrame)
    self.detailsLabel.setObjectName(u"detailsLabel")
    self.detailsLabel.setText(u"Details")

    # Add Widgets to Layout & set margins
    detailsFrameHorizontalLayout.addWidget(self.detailsLabel)
    detailsFrameHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    detailsFrameHorizontalLayout.setSpacing(0)

  def _create_status_frame(self):
    # Create status frame
    self.statusFrame = QFrame(self)
    self.statusFrame.setObjectName(u"statusFrame")
    self.statusFrame.setFrameShape(QFrame.NoFrame)
    self.statusFrame.setFrameShadow(QFrame.Raised)
    self.statusFrame.setMaximumSize(QSize(16777215, self._height))

    # Create status frame layout
    statusFrameHorizontalLayout = QHBoxLayout(self.statusFrame)
    statusFrameHorizontalLayout.setObjectName(u"statusFrameHorizontalLayout")

    # Create status label
    self.statusLabel = QLabel(self.statusFrame)
    self.statusLabel.setObjectName(u"statusLabel")

    # Add Widgets to Layout & set margins
    statusFrameHorizontalLayout.addWidget(self.statusLabel)
    statusFrameHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    statusFrameHorizontalLayout.setSpacing(0)

  def _create_version_frame(self):
    # Create status frame
    self.versionFrame = QFrame(self)
    self.versionFrame.setObjectName(u"versionFrame")
    self.versionFrame.setFrameShape(QFrame.NoFrame)
    self.versionFrame.setFrameShadow(QFrame.Raised)
    self.versionFrame.setMaximumSize(QSize(50, self._height))

    # Create version frame layout
    versionFrameHorizontalLayout = QHBoxLayout(self.versionFrame)
    versionFrameHorizontalLayout.setObjectName(u"versionFrameHorizontalLayout")

    # Create version label
    self.versionLabel = QLabel(self.versionFrame)
    self.versionLabel.setObjectName(u"versionLabel")
    self.versionLabel.setText(u"v1.0.0")

    # Add Widgets to Layout & set margins
    versionFrameHorizontalLayout.addWidget(self.versionLabel)
    versionFrameHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    versionFrameHorizontalLayout.setSpacing(0)

  def _create_grip_frame(self):
    # Create grip frame
    self.gripFrame = QFrame(self)
    self.gripFrame.setObjectName(u"gripFrame")
    self.gripFrame.setFrameShape(QFrame.StyledPanel)
    self.gripFrame.setFrameShadow(QFrame.Raised)
    self.gripFrame.setMinimumSize(QSize(25, self._height))
    self.gripFrame.setMaximumSize(QSize(25, self._height))

    # Create grip frame layout
    gripFrameHorizontalLayout = QHBoxLayout(self.gripFrame)
    gripFrameHorizontalLayout.setObjectName(u"gripFrameHorizontalLayout")

    # Create Size Grip
    self.sizeGrip = QSizeGrip(self.gripFrame)
    self.sizeGrip.setObjectName(u"sizeGrip")
    self.sizeGrip.setToolTip(u"Resize Window")

    # Add Widgets to Layout & set margins
    gripFrameHorizontalLayout.addWidget(self.sizeGrip)
    gripFrameHorizontalLayout.setContentsMargins(9, 9, 0, 0)
    gripFrameHorizontalLayout.setSpacing(0)


def _bottom_bar_main():
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of bottom bar
  bottom_bar = MainWindowBottomBar()
  # It helps to delete old/empty log files
  bottom_bar._logger.remove_log_files()
  # Show the bottom bar
  bottom_bar.show()
  # execute the program
  sys.exit(app.exec())


if __name__ == '__main__':
  """For development purpose only"""
  _bottom_bar_main()