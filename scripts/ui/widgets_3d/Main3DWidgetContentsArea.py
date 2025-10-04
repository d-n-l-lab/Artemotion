## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the main 3D widget content area.
##
##############################################################################################
##
import os
import sys

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QSettings, QSize
from PySide6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout

try:
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget
  from scripts.ui.widgets_3d.PyVistaWidget import PyVistaWidget
  # Keep old import for compatibility (can be removed later)
  # from scripts.ui.widgets_sub.Main3DSubWidgets import Main3DGLWidget
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget
  from scripts.ui.widgets_3d.PyVistaWidget import PyVistaWidget
  # Keep old import for compatibility (can be removed later)
  # from scripts.ui.widgets_sub.Main3DSubWidgets import Main3DGLWidget


class DummyLogger(Logger):

  pass


class Main3DWidgetContentsArea(QFrame):

  def __init__(self, parent: QWidget=None, logger: Logger=DummyLogger,
               settings: QSettings=None) -> None:
    super(Main3DWidgetContentsArea, self).__init__(parent=parent)

    self._logger = logger
    self._settings = settings

    # Setup the contents area
    self.setObjectName(u"main3DGLControlsFrame")
    self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
    if parent is None:
      self.resize(QSize(800, 500))

    self.init_UI()

    # Connections
    self._create_local_connects()

  def init_UI(self) -> None:
    # Create horizontal layout
    main3DMiddleHorizLayout = QHBoxLayout(self)
    main3DMiddleHorizLayout.setObjectName(u"main3DMiddleHorizLayout")

    # Create widgets
    self._create_main_3d_gl_controls_area()

    # Create 3D Widget (PyVista-based)
    self.main3DGLWidget = PyVistaWidget(parent=self, settings=self._settings)
    self.main3DGLWidget.setObjectName(u"main3DGLWidget")

    # Add widgets to the layout & set margins
    main3DMiddleHorizLayout.addWidget(self.main3DGLControlsFrame)
    main3DMiddleHorizLayout.addWidget(self.main3DGLWidget)
    main3DMiddleHorizLayout.setContentsMargins(0, 0, 0, 0)
    main3DMiddleHorizLayout.setSpacing(0)

  def _create_main_3d_gl_controls_area(self):
    # Create controls frame
    self.main3DGLControlsFrame = QFrame(self)
    self.main3DGLControlsFrame.setMinimumSize(QSize(100, 0))
    self.main3DGLControlsFrame.setMaximumSize(QSize(100, 16777215))
    self.main3DGLControlsFrame.setObjectName(u"main3DGLControlsFrame")
    self.main3DGLControlsFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

    # Create layout
    main3DGLControlsVertLayout = QVBoxLayout(self.main3DGLControlsFrame)
    main3DGLControlsVertLayout.setObjectName(u"main3DGLControlsVertLayout")

    dummyLabel = LabelWidget(parent=self.main3DGLControlsFrame, logger=self._logger,
                             text=u"Main 3D GL Controls", type="dummy_label")
    dummyLabel.setObjectName(u"dummyLabel")

    # Add widgets to layout & set margin
    main3DGLControlsVertLayout.addWidget(dummyLabel)
    main3DGLControlsVertLayout.setContentsMargins(0, 0, 0, 0)
    main3DGLControlsVertLayout.setSpacing(5)

  def _create_local_connects(self) -> None:
    pass

  def save_state(self) -> None:
    self.main3DGLWidget.save_state()

  def closeEvent(self, event: QCloseEvent) -> None:
    self.save_state()
    event.accept()
    return super(Main3DWidgetContentsArea, self).closeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of contents area
  contents_area = Main3DWidgetContentsArea()
  # It helps to delete old/empty log files
  contents_area._logger.remove_log_files()
  # Show the bottom bar
  contents_area.show()
  # execute the program
  sys.exit(app.exec())