## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the widgets related to Animation controls.
##
##############################################################################################
##
import os
import sys
import posixpath

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QApplication, QFrame, QStackedWidget, QVBoxLayout, QHBoxLayout)

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_comm.AnimDataWidget import AnimDataWidget
  from scripts.ui.widgets_anim.AnimPathsWidget import AnimPathsWidget
  from scripts.ui.widgets_anim.AnimPlotWidgets import AnimDataVizWidget
except:
  # For the development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_comm.AnimDataWidget import AnimDataWidget
  from scripts.ui.widgets_anim.AnimPathsWidget import AnimPathsWidget
  from scripts.ui.widgets_anim.AnimPlotWidgets import AnimDataVizWidget


class AnimationCtrlUILogger(Logger):

  FILE_NAME = "ui_animation_ctrl"
  LOGGER_NAME = "UIAnimationCtrl"


class AnimationCtrlWidget(QFrame):

  """
  Subclassed QFrame to create AnimationCtrlWidget. This is the main class managing various widgets
  to manage animation data and key frames.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      settings of the widget
  """

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(AnimationCtrlWidget, self).__init__(parent=self._parent)

    self._settings = kwargs.get('settings', None)

    # Assign attributes to the frame
    self.setObjectName(u"animationCtrlWidget")
    self.setWindowTitle(u"Animation Control")
    if self._parent is None:
      self.resize(QSize(1501, 392))

    self.init_UI()

    # Set Scene Edit/Control Widget default stylesheet
    self.set_stylesheet()

    # It helps to delete old/empty log files
    AnimationCtrlUILogger.remove_log_files()

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create main layout
    animationCtrlHorizLayout = QVBoxLayout(self)
    animationCtrlHorizLayout.setObjectName(u"animationCtrlHorizLayout")

    # Create widgets
    self._create_animation_ctrl_stacked_wdgt()

    # Add widgets to the layout &set margins
    animationCtrlHorizLayout.addWidget(self.animCtrlStckdWdgt)
    animationCtrlHorizLayout.setContentsMargins(0, 0, 0, 0)
    animationCtrlHorizLayout.setSpacing(0)

    # Connections
    self._create_anim_widgets_connections()

  def set_stylesheet(self, theme: str='default', qss: str='AnimationCtrlWidget.qss') -> None:
    """
    Method to set the stylesheet of the widget.

    Arguments:
      theme: str
        style theme: default
      qss: str
        name of the stylesheet file
    """

    try:
      # Set the StyleSheet
      qss_file = PathManager.get_qss_path(logger=AnimationCtrlUILogger,
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
      AnimationCtrlUILogger.info("Unable to set stylesheet because:")

  def _create_anim_data_wdgts_page(self) -> None:
    """
    Method to create a page managing animation data widgets.
    """

    # create page
    self.animDataWdgtsPage = QFrame(self)
    self.animDataWdgtsPage.setObjectName(u"animDataWdgtsPage")

    # Create layout
    animDataWdgtsPageLayout = QHBoxLayout(self.animDataWdgtsPage)
    animDataWdgtsPageLayout.setObjectName(u"animDataWdgtsPageLayout")

    # Create widgets
    self.animDataWdgt = AnimDataWidget(parent=self, settings=self._settings)
    self.animPathsWdgt = AnimPathsWidget(parent=self, settings=self._settings)

    # Add widgets to layout & set margins
    animDataWdgtsPageLayout.addWidget(self.animDataWdgt)
    animDataWdgtsPageLayout.addWidget(self.animPathsWdgt)
    animDataWdgtsPageLayout.setContentsMargins(0, 0, 0, 0)
    animDataWdgtsPageLayout.setSpacing(0)

  def _create_animation_ctrl_stacked_wdgt(self) -> None:
    """
    Method to create a stacked widget to manage the animation control widgets.
    """

    # Create stacked widget
    self.animCtrlStckdWdgt = QStackedWidget(self)
    self.animCtrlStckdWdgt.setObjectName(u"animCtrlStckdWdgt")

    # Create pages
    self.anim_data_viz_wdgt = AnimDataVizWidget(parent=self.animCtrlStckdWdgt,
                                                settings=self._settings,
                                                logger=AnimationCtrlUILogger)
    self._create_anim_data_wdgts_page()

    # Add pages
    self.animCtrlStckdWdgt.addWidget(self.anim_data_viz_wdgt)
    self.animCtrlStckdWdgt.addWidget(self.animDataWdgtsPage)

  def _create_anim_widgets_connections(self) -> None:
    """
    Method to create connections of various animation widgets.
    """

    # AnimPathsWidget
    self.animPathsWdgt.updated_robot_key_frames_data.connect(
      self.anim_data_viz_wdgt.on_updated_robot_keyframes_data_recvd
    )

    # AnimPlotWidgets
    self.anim_data_viz_wdgt.update_keyframes_with_total_time.connect(
      self.animPathsWdgt.on_keyframes_with_total_time_recvd
    )

  def on_stckd_wdgt_page_chng_req_rcvd(self, page: str) -> None:
    """
    Slot/Method called to change the stacked widget page.

    Arguments:
      page: str
        name of the page
    """

    if not page:
      return

    if page == "Animation Visualize":
      self.animCtrlStckdWdgt.setCurrentIndex(0)
    elif page == "Animation Data":
      self.animCtrlStckdWdgt.setCurrentIndex(1)

  def save_state(self) -> None:
    """
    Method to save the widget state and perform cleanup before closing.
    """

    self.animDataWdgt.save_state()
    self.animPathsWdgt.save_state()

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called when the widget is closed.
    """

    self.save_state()
    return super(AnimationCtrlWidget, self).closeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed Widget
  animation_ctrl_widget = AnimationCtrlWidget()
  # Show the widget
  animation_ctrl_widget.show()
  # execute the program
  sys.exit(app.exec())