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

from PySide6.QtGui import QCloseEvent, QResizeEvent
from PySide6.QtCore import QSettings, QSize
from PySide6.QtWidgets import (QApplication, QWidget, QFrame, QStackedWidget, QLabel, QPushButton,
                               QHBoxLayout, QVBoxLayout)

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_comm.TCPClientWidget import TCPClientWidget
  from scripts.ui.widgets_func.ArtemisCtrlWidget import ArtemisCtrlWidget
  from scripts.ui.widgets_3d.Main3DEnvSetupWidget import Main3DEnvSetupWidget
  from scripts.ui.widgets_func.OPCUAConfigCtrlWidget import OPCUAConfigCtrlWidget
except:
  # For the development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_comm.TCPClientWidget import TCPClientWidget
  from scripts.ui.widgets_func.ArtemisCtrlWidget import ArtemisCtrlWidget
  from scripts.ui.widgets_3d.Main3DEnvSetupWidget import Main3DEnvSetupWidget
  from scripts.ui.widgets_func.OPCUAConfigCtrlWidget import OPCUAConfigCtrlWidget


class SceneEditCtrlUILogger(Logger):

  FILE_NAME = "ui_scene_edit_ctrl"
  LOGGER_NAME = "UISceneEditCtrl"


class SceneEditCtrlWidget(QFrame):

  def __init__(self, parent: QWidget=None, settings: QSettings=None) -> None:
    super(SceneEditCtrlWidget, self).__init__(parent=parent)

    self._settings = settings

    # Assign attributes to the frame
    self.setObjectName(u"sceneEditCtrlWidget")
    self.setWindowTitle(u"Scene Editor")
    if parent is None:
      self.resize(QSize(514, 303))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self.init_UI()

    # Set Scene Edit/Control Widget default stylesheet
    self.set_stylesheet()

    # It helps to delete old/empty log files
    SceneEditCtrlUILogger.remove_log_files()

  def init_UI(self) -> None:
    # Create main layout
    sceneEditorVertLayout = QVBoxLayout(self)
    sceneEditorVertLayout.setObjectName(u"sceneEditorVertLayout")
  
    self._create_stack_navigation_frame()
    self._create_scene_editor_stacked_wdgt()

    # Add widgets to the layout &set margins
    sceneEditorVertLayout.addWidget(self.stackNavigateBtnsFrame)
    sceneEditorVertLayout.addWidget(self.sceneEditorStckdWdgt)
    sceneEditorVertLayout.setContentsMargins(0, 0, 0, 0)
    sceneEditorVertLayout.setSpacing(0)

    # Create connections
    self._create_local_connects()

    # Initialize stacked widget
    self._on_page_select_button_clicked()
    self._on_scene_edit_stckd_wdgt_page_chngd()

  def set_stylesheet(self, theme: str='default', qss: str='SceneEditCtrlWidget.qss') -> None:
    try:
      # Set the StyleSheet
      qss_file = PathManager.get_qss_path(logger=SceneEditCtrlUILogger,
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

  def _create_stack_navigation_frame(self) -> None:
    # Create frame
    self.stackNavigateBtnsFrame = QFrame(self)
    self.stackNavigateBtnsFrame.setMinimumSize(QSize(0, 30))
    self.stackNavigateBtnsFrame.setMaximumSize(QSize(16777215, 30))
    self.stackNavigateBtnsFrame.setObjectName(u"stackNavigateBtnsFrame")
    self.stackNavigateBtnsFrame.setFrameStyle(QFrame.NoFrame | QFrame.Raised)

    # Create layout
    stackNavigateBtnsHorizLayout = QHBoxLayout(self.stackNavigateBtnsFrame)
    stackNavigateBtnsHorizLayout.setObjectName(u"stackNavigateBtnsHorizLayout")

    # Create Pushbuttons
    self.sceneEditPageButton = QPushButton(self.stackNavigateBtnsFrame)
    self.sceneEditPageButton.setObjectName(u"sceneEditPageButton")
    self.sceneEditPageButton.setText(u"Edit Scene")
    self.sceneEditPageButton.setMinimumHeight(25)

    self.exportPlaybackButton = QPushButton(self.stackNavigateBtnsFrame)
    self.exportPlaybackButton.setObjectName(u"exportPlaybackButton")
    self.exportPlaybackButton.setText(u"Export Playback")
    self.exportPlaybackButton.setMinimumHeight(25)

    self.connectivityButton = QPushButton(self.stackNavigateBtnsFrame)
    self.connectivityButton.setObjectName(u"connectivityButton")
    self.connectivityButton.setText(u"Connectivity")
    self.connectivityButton.setMinimumHeight(25)

    # Add widgets to the layout & set margins
    stackNavigateBtnsHorizLayout.addWidget(self.sceneEditPageButton)
    stackNavigateBtnsHorizLayout.addWidget(self.exportPlaybackButton)
    stackNavigateBtnsHorizLayout.addWidget(self.connectivityButton)
    stackNavigateBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    stackNavigateBtnsHorizLayout.setSpacing(0)

  def _create_scene_editor_stacked_wdgt(self) -> None:
    # Create stacked widget
    self.sceneEditorStckdWdgt = QStackedWidget(self)
    self.sceneEditorStckdWdgt.setObjectName(u"sceneEditorStckdWdgt")

    # Create pages
    self.sceneEditPage = SceneEditCtrlPage(settings=self._settings)
    self.exportPlaybackPage = ExportPlaybackPage(settings=self._settings)
    self.connectivityPage = ConnectivityPage(settings=self._settings)

    # Add pages
    self.sceneEditorStckdWdgt.addWidget(self.sceneEditPage)
    self.sceneEditorStckdWdgt.addWidget(self.exportPlaybackPage)
    self.sceneEditorStckdWdgt.addWidget(self.connectivityPage)

  def _create_local_connects(self) -> None:
    # Pushbuttons
    self.sceneEditPageButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=0)
    )
    self.exportPlaybackButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=1)
    )
    self.connectivityButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=2)
    )

    # Stacked Widget
    self.sceneEditorStckdWdgt.currentChanged.connect(
      self._on_scene_edit_stckd_wdgt_page_chngd
    )

  def _on_page_select_button_clicked(self, idx: int=0) -> None:
    self.sceneEditorStckdWdgt.setCurrentIndex(idx)

  def _on_scene_edit_stckd_wdgt_page_chngd(self, idx: int=0) -> None:
    if not isinstance(idx, int):
      SceneEditCtrlUILogger.warning("Invalid index type received")
      return

    if idx == 0:
      self.sceneEditPageButton.setEnabled(False)
      self.exportPlaybackButton.setEnabled(True)
      self.connectivityButton.setEnabled(True)
    elif idx == 1:
      self.sceneEditPageButton.setEnabled(True)
      self.exportPlaybackButton.setEnabled(False)
      self.connectivityButton.setEnabled(True)
    elif idx == 2:
      self.sceneEditPageButton.setEnabled(True)
      self.exportPlaybackButton.setEnabled(True)
      self.connectivityButton.setEnabled(False)

  def save_state(self) -> None:
    self.connectivityPage.opcConfigWidget.save_state()
    self.connectivityPage.tcpClientWidget.save_state()

  def closeEvent(self, event: QCloseEvent) -> None:
    self.save_state()
    return super().closeEvent(event)


class SceneEditCtrlPage(QFrame):

  def __init__(self, parent: QWidget=None, settings: QSettings=None) -> None:
    super(SceneEditCtrlPage, self).__init__(parent=parent)

    self.setObjectName(u"sceneEditPage")
    self.setWindowTitle(u"Scene Editor")
    if parent is None:
      self.resize(410, 990)
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Get the application settings
    self._settings = settings

    self.init_page()

  def init_page(self):
    # Create layout
    sceneEditPageMainLayout = QVBoxLayout(self)
    sceneEditPageMainLayout.setObjectName(u"sceneEditPageMainLayout")

    # Create Artemis Control Widget
    self.artemisCtrlWidget = ArtemisCtrlWidget(parent=self,
                                               logger=SceneEditCtrlUILogger,
                                               settings=self._settings)

    # Add 3D Environment Setup Widget
    self.main3DEnvSetupWdgt = Main3DEnvSetupWidget(parent=self,
                                                   logger=SceneEditCtrlUILogger,
                                                   settings=self._settings)

    # Add widgets to layout & set margins
    sceneEditPageMainLayout.addWidget(self.artemisCtrlWidget)
    sceneEditPageMainLayout.addWidget(self.main3DEnvSetupWdgt)
    sceneEditPageMainLayout.setContentsMargins(0, 0, 0, 0)
    sceneEditPageMainLayout.setSpacing(0)

  def resizeEvent(self, event: QResizeEvent) -> None:
    self.artemisCtrlWidget.setMinimumHeight(self.height() / 2)
    self.main3DEnvSetupWdgt.setMinimumHeight(self.height() / 2)
    return super(SceneEditCtrlPage, self).resizeEvent(event)


class ExportPlaybackPage(QFrame):

  def __init__(self, parent: QWidget=None, settings: QSettings=None) -> None:
    super(ExportPlaybackPage, self).__init__(parent=parent)

    self.setObjectName(u"exportPlaybackPage")
    self.setWindowTitle(u"Export Playback")
    if parent is None:
      self.resize(410, 990)
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Get the application settings
    self._settings = settings

    self.init_page()

  def init_page(self):
    # Create layout
    expPlaybackPageMainLayout = QVBoxLayout(self)
    expPlaybackPageMainLayout.setObjectName(u"expPlaybackPageMainLayout")

    # Add widget
    self.exportPlaybackLabel = QLabel(self)
    self.exportPlaybackLabel.setObjectName(u"exportPlaybackLabel")
    self.exportPlaybackLabel.setText(u"Export Playback Label")

    # Add widgets to layout & set margins
    expPlaybackPageMainLayout.addWidget(self.exportPlaybackLabel)
    expPlaybackPageMainLayout.setContentsMargins(0, 0, 0, 0)
    expPlaybackPageMainLayout.setSpacing(0)

  def resizeEvent(self, event: QResizeEvent) -> None:
    return super(ExportPlaybackPage, self).resizeEvent(event)


class ConnectivityPage(QFrame):

  def __init__(self, parent: QWidget=None, settings: QSettings=None) -> None:
    super(ConnectivityPage, self).__init__(parent=parent)

    self.setObjectName(u"connectivityPage")
    self.setWindowTitle(u"Connectivity")
    if parent is None:
      self.resize(410, 990)
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Get the application settings
    self._settings = settings

    self.init_page()

  def init_page(self):
    # Create layout
    connectivityPageMainLayout = QVBoxLayout(self)
    connectivityPageMainLayout.setObjectName(u"connectivityPageMainLayout")

    # OPC Config Widget
    self.opcConfigWidget = OPCUAConfigCtrlWidget(parent=self, settings=self._settings)

    # TCP Client Widget
    self.tcpClientWidget = TCPClientWidget(parent=self, settings=self._settings)

    # Add widgets to layout & set margins
    connectivityPageMainLayout.addWidget(self.opcConfigWidget)
    connectivityPageMainLayout.addWidget(self.tcpClientWidget)
    connectivityPageMainLayout.setContentsMargins(0, 0, 0, 0)
    connectivityPageMainLayout.setSpacing(0)

  def resizeEvent(self, event: QResizeEvent) -> None:
    self.opcConfigWidget.setMinimumHeight(self.height() / 2)
    self.tcpClientWidget.setMinimumHeight(self.height() / 2)
    return super(ConnectivityPage, self).resizeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed Widget
  scene_edit_ctrl_widget = SceneEditCtrlWidget()
  # Show the widget
  scene_edit_ctrl_widget.show()
  # execute the program
  sys.exit(app.exec())