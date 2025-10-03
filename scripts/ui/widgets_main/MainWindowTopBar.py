## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including MainWindowTopBar class managing various widgets and controls.
##
##############################################################################################
##
import os
import sys
import json

from PySide6.QtGui import Qt
from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import (QApplication, QWidget, QFrame, QHBoxLayout, QLabel, QPushButton,
                               QMenu, QSpacerItem, QSizePolicy)

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))))
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger


class DummyLogger(Logger):

  pass


class MainWindowTopBar(QFrame):

  """
  Class to manage Main Window Top Bar Widget.

  Keyword Arguments:
    parent: QWidget
      parent widget
    logger: Logger
      logger class
    height: int
      height of the top bar
  """

  # Signals
  add_robot = Signal(str)
  exit_main_application = Signal()
  anim_window_change_req = Signal(str)

  def __init__(self, **kwargs) -> None:
    super(MainWindowTopBar, self).__init__(parent=kwargs.get('parent', None))

    self._logger = kwargs['logger']
    self._height = kwargs.get('height', 30)

    # Setup the top bar
    self.setFrameShape(QFrame.NoFrame)
    self.setFrameShadow(QFrame.Raised)
    self.setObjectName(u"mainWindowTopBar")
    self.setMaximumSize(QSize(16777215, self._height))

    # Get menu items
    self.menu_items = self._get_menu_items('mainMenu.json')

    self.init_UI()

    self._create_file_menu_actions_trigger()
    self._create_scene_menu_actions_trigger()
    self._create_window_menu_actions_trigger()

  def init_UI(self):
    # Create top bar layout
    topBarHorizontalLayout = QHBoxLayout(self)
    topBarHorizontalLayout.setObjectName(u"topBarHorizontalLayout")

    # Create spacers
    leftHSpacer = QSpacerItem(40, self._height, QSizePolicy.Expanding)
    rightHSpacer = QSpacerItem(40, self._height, QSizePolicy.Expanding)

    # Menu Frame
    self._create_menu_frame()

    # Window Title Frame
    self._create_window_title_frame()

    # Window Control Frame
    self._create_window_ctrl_frame()

    # Add widgets to layout & set margins
    topBarHorizontalLayout.addWidget(self.menuFrame)
    topBarHorizontalLayout.addItem(leftHSpacer)
    topBarHorizontalLayout.addWidget(self.windowTitleFrame)
    topBarHorizontalLayout.addItem(rightHSpacer)
    topBarHorizontalLayout.addWidget(self.windowControlFrame)
    topBarHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    topBarHorizontalLayout.setSpacing(0)

  def _get_menu_items(self, file_name=''):
    menu_items = {}
    menu_file = PathManager.get_config_path(logger=self._logger, config_file=file_name)
    if menu_file is not None:
      with open(menu_file, 'r') as mf:
        menu_items = json.load(mf)

    return menu_items

  def _add_menu_items(self, menu_obj, data, shortcut=''):
    try:
      if isinstance(data, dict):
        for k, v in data.items():
          if isinstance(v, list):
            sub_menu = QMenu(k, menu_obj)
            menu_obj.addMenu(sub_menu)
            for sub_dict in v:
              self._add_menu_items(sub_menu, sub_dict)
          else:
            self._add_menu_items(menu_obj, k, v)
      elif isinstance(data, list):
        for elem in data:
          self._add_menu_items(menu_obj, elem)
      elif data == "Separator":
        menu_obj.addSeparator()
      else:
        action = menu_obj.addAction(data)
        action.setShortcut(shortcut)
        action.setIconVisibleInMenu(False)
    except Exception:
      self._logger.exception(f"Unable to add {data} to  {menu_obj} as menu item because:")

  def _create_menu_frame(self):
    # Create Menu Frame
    self.menuFrame = QFrame(self)
    self.menuFrame.setObjectName(u"menuFrame")
    self.menuFrame.setFrameShape(QFrame.NoFrame)
    self.menuFrame.setFrameShadow(QFrame.Raised)
    self.menuFrame.setMinimumSize(QSize(230, self._height))
    self.menuFrame.setMaximumSize(QSize(230, self._height))

    # Create Menu Frame Layout
    menuFrameHorizontalLayout = QHBoxLayout(self.menuFrame)
    menuFrameHorizontalLayout.setObjectName(u"menuFrameHorizontalLayout")

    # Create Menu items
    self.filePushButton = QPushButton(self.menuFrame)
    self.filePushButton.setMaximumSize(QSize(40, 30))
    self.filePushButton.setObjectName(u"filePushButton")
    self.filePushButton.setText(u"File")

    # Add menu items
    fileMenu = QMenu("&File", self.filePushButton)
    fileMenu.setObjectName(u"fileMenu")
    self.filePushButton.setMenu(fileMenu)
    self._add_menu_items(fileMenu, self.menu_items['File'])

    self.editPushButton = QPushButton(self.menuFrame)
    self.editPushButton.setMaximumSize(QSize(40, 30))
    self.editPushButton.setObjectName(u"editPushButton")
    self.editPushButton.setText(u"Edit")

    # Add menu items
    editMenu = QMenu("&Edit", self.editPushButton)
    editMenu.setObjectName(u"editMenu")
    self.editPushButton.setMenu(editMenu)
    self._add_menu_items(editMenu, self.menu_items['Edit'])

    self.scenePushButton = QPushButton(self.menuFrame)
    self.scenePushButton.setMaximumSize(QSize(50, 30))
    self.scenePushButton.setObjectName(u"scenePushButton")
    self.scenePushButton.setText(u"Scene")

    # Add menu items
    sceneMenu = QMenu("&Scene", self.scenePushButton)
    sceneMenu.setObjectName(u"sceneMenu")
    self.scenePushButton.setMenu(sceneMenu)
    self._add_menu_items(sceneMenu, self.menu_items['Scene'])

    self.windowPushButton = QPushButton(self.menuFrame)
    self.windowPushButton.setMaximumSize(QSize(60, 30))
    self.windowPushButton.setObjectName(u"windowPushButton")
    self.windowPushButton.setText(u"Window")

    # Add menu items
    windowMenu = QMenu("&Window", self.windowPushButton)
    windowMenu.setObjectName(u"windowMenu")
    self.windowPushButton.setMenu(windowMenu)
    self._add_menu_items(windowMenu, self.menu_items['Window'])

    self.helpPushButton = QPushButton(self.menuFrame)
    self.helpPushButton.setMaximumSize(QSize(40, 30))
    self.helpPushButton.setObjectName(u"helpPushButton")
    self.helpPushButton.setText(u"Help")

    # Add menu items
    helpMenu = QMenu("&Help", self.helpPushButton)
    helpMenu.setObjectName(u"helpMenu")
    self.helpPushButton.setMenu(helpMenu)
    self._add_menu_items(helpMenu, self.menu_items['Help'])

    # Add Widgets to layout & set margins
    menuFrameHorizontalLayout.addWidget(self.filePushButton)
    menuFrameHorizontalLayout.addWidget(self.editPushButton)
    menuFrameHorizontalLayout.addWidget(self.scenePushButton)
    menuFrameHorizontalLayout.addWidget(self.windowPushButton)
    menuFrameHorizontalLayout.addWidget(self.helpPushButton)
    menuFrameHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    menuFrameHorizontalLayout.setSpacing(0)

  def _create_window_title_frame(self):
    # Create Window title frame
    self.windowTitleFrame = QFrame(self)
    self.windowTitleFrame.setObjectName(u"windowTitleFrame")
    self.windowTitleFrame.setFrameShape(QFrame.NoFrame)
    self.windowTitleFrame.setFrameShadow(QFrame.Raised)
    self.windowTitleFrame.setMaximumSize(QSize(16777215, self._height))

    # Create Window Title Frame Layout
    winTitleFrameHorizontalLayout = QHBoxLayout(self.windowTitleFrame)
    winTitleFrameHorizontalLayout.setObjectName(u"winTitleFrameHorizontalLayout")

    # Create spacers
    leftHSpacer = QSpacerItem(40, self._height, QSizePolicy.Expanding)
    rightHSpacer = QSpacerItem(40, self._height, QSizePolicy.Expanding)

    # Create Label
    self.windowTitleLabel = QLabel(self.windowTitleFrame)
    self.windowTitleLabel.setObjectName(u"windowTitleLabel")
    self.windowTitleLabel.setMaximumSize(QSize(16777215, self._height))
    self.windowTitleLabel.setAlignment(Qt.AlignCenter)
    self.windowTitleLabel.setText(u"ArteMotion")

    # Add Widgets to Layout & set margins
    winTitleFrameHorizontalLayout.addItem(leftHSpacer)
    winTitleFrameHorizontalLayout.addWidget(self.windowTitleLabel)
    winTitleFrameHorizontalLayout.addItem(rightHSpacer)
    winTitleFrameHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    winTitleFrameHorizontalLayout.setSpacing(0)

  def _create_window_ctrl_frame(self):
    # Create Window Control Frame
    self.windowControlFrame = QFrame(self)
    self.windowControlFrame.setObjectName(u"windowControlFrame")
    self.windowControlFrame.setFrameShape(QFrame.NoFrame)
    self.windowControlFrame.setFrameShadow(QFrame.Raised)
    self.windowControlFrame.setMinimumSize(QSize(150, self._height))
    self.windowControlFrame.setMaximumSize(QSize(150, self._height))

    # Create Window Control Frame Layout
    winCtrlFrameHorizontalLayout = QHBoxLayout(self.windowControlFrame)
    winCtrlFrameHorizontalLayout.setObjectName(u"winCtrlFrameHorizontalLayout")

    # Create Pushbuttons
    self.minimizePushButton = QPushButton(self.windowControlFrame)
    self.minimizePushButton.setObjectName(u"minimizePushButton")
    self.minimizePushButton.setMinimumSize(QSize(self.windowControlFrame.width()/3, self._height))
    self.minimizePushButton.setText("")

    self.maximizePushButton = QPushButton(self.windowControlFrame)
    self.maximizePushButton.setObjectName(u"maximizePushButton")
    self.maximizePushButton.setMinimumSize(QSize(self.windowControlFrame.width()/3, self._height))
    self.maximizePushButton.setText("")

    self.closePushButton = QPushButton(self.windowControlFrame) 
    self.closePushButton.setObjectName(u"closePushButton")
    self.closePushButton.setMinimumSize(QSize(self.windowControlFrame.width()/3, self._height))
    self.closePushButton.setText("")

    # Add Widgets to Layout & set margins
    winCtrlFrameHorizontalLayout.addWidget(self.minimizePushButton)
    winCtrlFrameHorizontalLayout.addWidget(self.maximizePushButton)
    winCtrlFrameHorizontalLayout.addWidget(self.closePushButton)
    winCtrlFrameHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    winCtrlFrameHorizontalLayout.setSpacing(0)

  def _create_file_menu_actions_trigger(self) -> None:
    """
    Method to add connections of the trigger of the actions of the file menu.
    """

    # Exit action
    self.filePushButton.menu().actions()[8].triggered.connect(
      lambda: self.exit_main_application.emit()
    )

  def _create_scene_menu_actions_trigger(self) -> None:
    """
    Method to add connections of the trigger of the actions of the scene menu.
    """

    # Add Robots
    # KUKA
    self.scenePushButton.menu().actions()[0].menu().actions()[0].menu().actions()[0].triggered.connect(
      lambda: self.add_robot.emit("KR16-R2010-2")
    )
    # self.scenePushButton.menu().actions()[0].menu().actions()[0].menu().actions()[1].triggered.connect(
    #   lambda: self.add_robot.emit("KR20-R3100")
    # )
    # self.scenePushButton.menu().actions()[0].menu().actions()[0].menu().actions()[2].triggered.connect(
    #   lambda: self.add_robot.emit("KR30-R2100")
    # )
    # Staubli
    self.scenePushButton.menu().actions()[0].menu().actions()[1].menu().actions()[0].triggered.connect(
      lambda: self.add_robot.emit("Staubli-RX160")
    )
    # self.scenePushButton.menu().actions()[0].menu().actions()[1].menu().actions()[1].triggered.connect(
    #   lambda: self.add_robot.emit("Staubli-RX160L")
    # )

  def _create_window_menu_actions_trigger(self) -> None:
    """
    Method to add connections of the trigger of the actions of the window menu.
    """

    # Animation-Visualize
    self.windowPushButton.menu().actions()[0].menu().actions()[0].triggered.connect(
      lambda: self.anim_window_change_req.emit("Animation Visualize")
    )
    # Animation-Data
    self.windowPushButton.menu().actions()[0].menu().actions()[1].triggered.connect(
      lambda: self.anim_window_change_req.emit("Animation Data")
    )


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of top bar
  top_bar = MainWindowTopBar()
  # It helps to delete old/empty log files
  top_bar._logger.remove_log_files()
  # Show the top bar
  top_bar.show()
  # execute the program
  sys.exit(app.exec())