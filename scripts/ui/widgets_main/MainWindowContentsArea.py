## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including class to manage the main window contents area.
##
##############################################################################################
##
import os
import sys
import posixpath

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QVBoxLayout, QStackedWidget,
                               QWidget, QFrame)

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_3d.Main3DWidget import Main3DWidget
  from scripts.ui.widgets_rob.SimRobotCtrlWidget import SimRobotCtrlWidget
  from scripts.ui.widgets_anim.AnimationCtrlWidget import AnimationCtrlWidget
  from scripts.ui.widgets_func.SceneEditCtrlWidget import SceneEditCtrlWidget
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_3d.Main3DWidget import Main3DWidget
  from scripts.ui.widgets_rob.SimRobotCtrlWidget import SimRobotCtrlWidget
  from scripts.ui.widgets_anim.AnimationCtrlWidget import AnimationCtrlWidget
  from scripts.ui.widgets_func.SceneEditCtrlWidget import SceneEditCtrlWidget


class DummyLogger(Logger):

  # For development purpose only
  pass


class MainWindowContentsArea(QFrame):

  def __init__(self, parent: QWidget=None, logger: Logger=DummyLogger, settings: QSettings=None) -> None:
    super(MainWindowContentsArea, self).__init__(parent=parent)

    self._logger = logger
    self._settings = settings

    self.animDataWidget = None

    # Setup the contents area
    self.setFrameShape(QFrame.NoFrame)
    self.setFrameShadow(QFrame.Raised)
    self.setObjectName(u"mainWindowContentsArea")

    self.init_UI()

    # Set Contents Area Default Style
    self.set_stylesheet()

  def init_UI(self):
    """
    Method to initialize the UI.
    """

    # Create contents area layout
    contentsAreaMainLayout = QGridLayout(self)
    contentsAreaMainLayout.setObjectName(u"contentsAreaMainLayout")

    # Main 3D
    self._create_main_3d_area()

    # Right Contents Area
    self._create_right_contents_area()

    # Bottom Contents Area
    self._create_bottom_contents_area()

    # Add widgets to Layout & set margins
    contentsAreaMainLayout.addWidget(self.main3DAreaFrame, 0, 0, 13, 15)
    contentsAreaMainLayout.addWidget(self.rightContentsAreaFrame, 0, 16, 20, 5)
    contentsAreaMainLayout.addWidget(self.bottomContentsAreaFrame, 13, 0, 7, 15)
    contentsAreaMainLayout.setContentsMargins(0, 0, 0, 0)
    contentsAreaMainLayout.setSpacing(0)

    # Connections
    self._create_main_3d_area_connects()
    self._create_right_contents_area_connects()
    self._create_bottom_contents_area_connects()

  def set_stylesheet(self, theme: str='default', qss: str='MainWindowContentsArea.qss') -> None:
    """
    Method to set the stylesheet of the widget.

    Arguments:
      theme: str
        style theme: default
      qss: str
        name of the stylesheet file
    """

    # Set the StyleSheet
    qss_file = PathManager.get_qss_path(logger=self._logger,
                                        qss_file=os.path.join(theme, qss))
    icons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.relpath(qss_file)))),
                              "icons", theme)
    with open(qss_file, 'r') as fh:
      style_sheet = fh.read()
      self.setStyleSheet(style_sheet.replace("<icons_path>",
                                             f"{icons_path}".replace(os.sep, posixpath.sep)))

  def _create_main_3d_area(self) -> None:
    """
    Method to create main 3D area.
    """

    # Create 3D frame
    self.main3DAreaFrame = QFrame(self)
    self.main3DAreaFrame.setObjectName(u"main3DAreaFrame")
    self.main3DAreaFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Create 3D area frame layout
    main3DAreaFrameLayout = QVBoxLayout(self.main3DAreaFrame)
    main3DAreaFrameLayout.setObjectName(u"main3DAreaFrameLayout")

    self.main3DWidget = Main3DWidget(parent=self.main3DAreaFrame, settings=self._settings)
    self.main3DWidget.setObjectName(u"main3DWidget")

    # Add widgets to Layout & set margins
    main3DAreaFrameLayout.addWidget(self.main3DWidget)
    main3DAreaFrameLayout.setContentsMargins(0, 0, 0, 0)
    main3DAreaFrameLayout.setSpacing(0)

  def _create_scene_edit_ctrl_page(self) -> None:
    """
    Method to create Scene Edit Control page.
    """

    # Create page
    self.sceneEditCtrlPage = QFrame()
    self.sceneEditCtrlPage.setObjectName(u"sceneEditCtrlPage")

    # Create vertical layout
    sceneEditCtrlPageLayout = QVBoxLayout(self.sceneEditCtrlPage)
    sceneEditCtrlPageLayout.setObjectName(u"sceneEditCtrlPageLayout")

    # Create Animation data widget
    self.sceneEditCtrlWidget = SceneEditCtrlWidget(parent=self.sceneEditCtrlPage,
                                                   settings=self._settings)

    # Add widgets to vertical layout & set margins
    sceneEditCtrlPageLayout.addWidget(self.sceneEditCtrlWidget)
    sceneEditCtrlPageLayout.setContentsMargins(0, 0, 0, 0)
    sceneEditCtrlPageLayout.setSpacing(0)

  def _create_right_contents_area(self) -> None:
    """
    Method to create right contents area.
    """

    # Create right contents area frame
    self.rightContentsAreaFrame = QFrame(self)
    self.rightContentsAreaFrame.setObjectName(u"rightContentsAreaFrame")
    self.rightContentsAreaFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Create layout
    rightContentsAreaFrameLayout = QVBoxLayout(self.rightContentsAreaFrame)
    rightContentsAreaFrameLayout.setObjectName(u"rightContentsAreaFrameLayout")

    # Create Stacked Widget
    self.rightContentsStackedWdgt = QStackedWidget(self.rightContentsAreaFrame)
    self.rightContentsStackedWdgt.setObjectName(u"rightContentsStackedWdgt")

    # Create pages
    self._create_scene_edit_ctrl_page()

    # Add pages
    self.rightContentsStackedWdgt.addWidget(self.sceneEditCtrlPage)

    # Add widgets to layout & set margins
    rightContentsAreaFrameLayout.addWidget(self.rightContentsStackedWdgt)
    rightContentsAreaFrameLayout.setContentsMargins(0, 0, 0, 0)
    rightContentsAreaFrameLayout.setSpacing(0)

  def _create_animation_ctrl_page(self) -> None:
    """
    Method to create Animation Control page.
    """

    # Create page
    self.animationCtrlPage = QFrame()
    self.animationCtrlPage.setObjectName(u"animationCtrlPage")

    # Create vertical layout
    animationCtrlPageLayout = QHBoxLayout(self.animationCtrlPage)
    animationCtrlPageLayout.setObjectName(u"animationCtrlPageLayout")

    # Create simulated robot control widget
    self.simRobotCtrlWidget = SimRobotCtrlWidget(parent=self.animationCtrlPage,
                                                 settings=self._settings)

    # Create animation control widget
    self.animationCtrlWidget = AnimationCtrlWidget(parent=self.animationCtrlPage,
                                                   settings=self._settings)

    # Add widgets to vertical layout & set margins
    animationCtrlPageLayout.addWidget(self.simRobotCtrlWidget)
    animationCtrlPageLayout.addWidget(self.animationCtrlWidget)
    animationCtrlPageLayout.setContentsMargins(0, 0, 0, 0)
    animationCtrlPageLayout.setStretch(0, 1)
    animationCtrlPageLayout.setSpacing(0)

  def _create_bottom_contents_area(self) -> None:
    """
    Method to create connections of bottom contents area.
    """

    # Create bottom contents area frame
    self.bottomContentsAreaFrame = QFrame(self)
    self.bottomContentsAreaFrame.setObjectName(u"bottomContentsAreaFrame")
    self.bottomContentsAreaFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Create bottom contents area frame layout
    bottomContentsAreaFrameLayout = QHBoxLayout(self.bottomContentsAreaFrame)
    bottomContentsAreaFrameLayout.setObjectName(u"bottomContentsAreaFrameLayout")

    # Create stacked widget
    self.bottomContentsStackedWdgt = QStackedWidget(self.bottomContentsAreaFrame)
    self.bottomContentsStackedWdgt.setObjectName(u"bottomContentsStackedWdgt")

    # Create pages
    self._create_animation_ctrl_page()

    # Add pages
    self.bottomContentsStackedWdgt.addWidget(self.animationCtrlPage)

    # # Add widgets to layout & set margins
    bottomContentsAreaFrameLayout.addWidget(self.bottomContentsStackedWdgt)
    bottomContentsAreaFrameLayout.setContentsMargins(0, 0, 0, 0)
    bottomContentsAreaFrameLayout.setSpacing(0)

  def _create_main_3d_area_connects(self) -> None:
    """
    Method to create connections of signals of the main 3D area to the respective slots.
    """

    self.main3DWidget.main_3d_bottom_bar.main_3d_playback_control.connect(
      self.animationCtrlWidget.animPathsWdgt.on_robot_pose_frm_path_req_for_pb
    )

    pass

  def _create_right_contents_area_connects(self) -> None:
    """
    Method to create connections of signals of the right contents area to the respective slots.
    """

    pass

  def _create_bottom_contents_area_connects(self) -> None:
    """
    Method to create connections of signals of the bottom contents area to the respective slots.
    """

    # Animation Control Widget
    ## Animation Data Widget
    self.animationCtrlWidget.animDataWdgt.publish_animation_point.connect(
      self.sceneEditCtrlWidget.connectivityPage.opcConfigWidget.on_animation_data_point_recvd
    )
    ## Simulated Robot Control Widget
    self.simRobotCtrlWidget.sim_rob_ctrl_current_pose.connect(
      self.animationCtrlWidget.animPathsWdgt.on_robot_current_pose_recvd
    )
    self.simRobotCtrlWidget.sim_rob_ctrl_current_pose.connect(
      self.animationCtrlWidget.anim_data_viz_wdgt.on_updated_robot_keyframes_data_recvd
    )
    self.simRobotCtrlWidget.sim_rob_ctrl_added_robots.connect(
      self.animationCtrlWidget.animPathsWdgt.on_robots_got_added
    )
    self.simRobotCtrlWidget.sim_rob_ctrl_added_robots.connect(
      self.animationCtrlWidget.anim_data_viz_wdgt.on_robots_got_added
    )
    self.simRobotCtrlWidget.sim_rob_ctrl_create_update_robot_in_3d.connect(
      self.main3DWidget.main_3d_contents_area.main3DGLWidget.create_robot_3d
    )
    self.simRobotCtrlWidget.sim_rob_ctrl_curves_ik_solutions.connect(
      self.animationCtrlWidget.animPathsWdgt.on_robot_path_ik_solutions_recvd
    )
    ## Animation Paths Widget
    self.animationCtrlWidget.animPathsWdgt.request_robot_current_pose.connect(
      self.simRobotCtrlWidget.on_current_robot_pose_req_recvd
    )
    self.animationCtrlWidget.animPathsWdgt.publish_robot_path_data_for_ik.connect(
      self.simRobotCtrlWidget.on_curves_data_ik_computation_req_recvd
    )
    self.animationCtrlWidget.animPathsWdgt.publish_robot_path_data_for_curve.connect(
      self.main3DWidget.main_3d_contents_area.main3DGLWidget.create_curves
    )
    self.animationCtrlWidget.animPathsWdgt.publish_robot_pose_ik_for_pb.connect(
      self.simRobotCtrlWidget.on_updated_ik_sol_received_for_pb
    )
    self.animationCtrlWidget.animPathsWdgt.playback_finished.connect(
      self.main3DWidget.main_3d_bottom_bar.on_animation_pb_finished
    )
    # Animation Plot Widget
    self.animationCtrlWidget.anim_data_viz_wdgt.add_key_frame.connect(
      self.simRobotCtrlWidget.on_current_robot_pose_req_recvd
    )

  def save_state(self) -> None:
    """
    Method to save the state before exiting.
    """

    self.main3DWidget.save_state()
    self.simRobotCtrlWidget.save_state()
    self.sceneEditCtrlWidget.save_state()
    self.animationCtrlWidget.save_state()

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called when widget exits.
    """

    self.save_state()
    event.accept()
    return super(MainWindowContentsArea, self).closeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of contents area
  contents_area = MainWindowContentsArea()
  # It helps to delete old/empty log files
  contents_area._logger.remove_log_files()
  # Show the bottom bar
  contents_area.show()
  # execute the program
  sys.exit(app.exec())