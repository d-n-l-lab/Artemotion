## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the Main 3D Widget.
##
##############################################################################################
##
import os
import sys
import posixpath

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_3d.Main3DWidgetTopBar import Main3DWidgetTopBar
  from scripts.ui.widgets_3d.Main3DWidgetBottomBar import Main3DWidgetBottomBar
  from scripts.ui.widgets_3d.Main3DWidgetContentsArea import Main3DWidgetContentsArea
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_3d.Main3DWidgetTopBar import Main3DWidgetTopBar
  from scripts.ui.widgets_3d.Main3DWidgetBottomBar import Main3DWidgetBottomBar
  from scripts.ui.widgets_3d.Main3DWidgetContentsArea import Main3DWidgetContentsArea


class Main3DWidgetLogger(Logger):

  FILE_NAME = 'ui_main_3d'
  LOGGER_NAME = "UIMain3DLogger"


class Main3DWidget(QFrame):

  """
  Class to manage the Main 3D Widget. This class instantiate various other 3D widgets classes.

  KeyWord Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      settings of the widget
  """

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(Main3DWidget, self).__init__(parent=self._parent)

    self._settings = kwargs.get('settings', None)

    # Assign attributes
    if not self.objectName():
      self.setObjectName(u"main3DWidget")
    self.setWindowTitle(u"Main 3D")
    if self._parent is None:
      self.resize(700, 500)

    self.init_UI()

    # Set 3D Widget Default Style
    self.set_stylesheet()

    # It helps to delete old/empty log files
    Main3DWidgetLogger.remove_log_files()

  def init_UI(self) -> None:
    """
    Method to initialize the widget.
    """

    # Create main Layout
    main3DWidgetVertLayout = QVBoxLayout(self)
    main3DWidgetVertLayout.setObjectName(u"main3DWidgetVertLayout")

    # Create top bar
    self.main_3d_top_bar = Main3DWidgetTopBar(parent=self, logger=Main3DWidgetLogger, height=40)
    self.main_3d_contents_area = Main3DWidgetContentsArea(parent=self, logger=Main3DWidgetLogger,
                                                          settings=self._settings)
    self.main_3d_bottom_bar = Main3DWidgetBottomBar(parent=self, logger=Main3DWidgetLogger,
                                                    height=50)

    # Add Widgets to the layout & set margins
    main3DWidgetVertLayout.addWidget(self.main_3d_top_bar)
    main3DWidgetVertLayout.addWidget(self.main_3d_contents_area)
    main3DWidgetVertLayout.addWidget(self.main_3d_bottom_bar)
    main3DWidgetVertLayout.setContentsMargins(0, 0, 0, 0)
    main3DWidgetVertLayout.setSpacing(0)

  def set_stylesheet(self, theme: str='default', qss: str='Main3DWidget.qss') -> None:
    """
    Method to activate the style sheet on the UI elements.

    Arguments:
      theme: str
        theme of the style
      qss: str
        name of the stylesheet file
    """

    # Set the StyleSheet
    qss_file = PathManager.get_qss_path(logger=Main3DWidgetLogger,
                                        qss_file=os.path.join(theme, qss))
    icons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.relpath(qss_file)))),
                              "icons", theme)
    with open(qss_file, 'r') as fh:
      style_sheet = fh.read()
      self.setStyleSheet(style_sheet.replace("<icons_path>",
                                             f"{icons_path}".replace(os.sep, posixpath.sep)))

  def save_state(self) -> None:
    """
    Method to save the widget state and perform cleanup before closing.
    """

    self.main_3d_bottom_bar.save_state()
    self.main_3d_contents_area.save_state()

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called on Close Event.
    """

    self.save_state()
    return super().closeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
  app = QApplication(sys.argv)
  # Create an instance of 3D widget
  _main_3d = Main3DWidget()
  # Show the 3D widget
  _main_3d.show()
  # execute the program
  sys.exit(app.exec())