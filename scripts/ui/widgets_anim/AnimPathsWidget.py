## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various classes to manage the animation paths data. The classes
##              are responsible to compute Curves data creating the Path of the simulated robot.
##
##############################################################################################
##
import os
import sys
import glm
import posixpath
import numpy as np

from typing import List, Dict

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QObject, QThread, Signal, QSize, QItemSelection
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout, QHBoxLayout

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.maths.Bezier import BezierSpline
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget, ComboBoxWidget
  from scripts.ui.widgets_sub.anim.AnimPathsSubWidgets import KeyFramesTableView
except:
  # For the development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.maths.Bezier import BezierSpline
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget, ComboBoxWidget
  from scripts.ui.widgets_sub.anim.AnimPathsSubWidgets import KeyFramesTableView


class AnimPathsUILogger(Logger):

  FILE_NAME = "ui_path_planning"
  LOGGER_NAME = "UI"


class AnimPathsWidgetWorker(QObject):
  """
  Class to manage the Animation Paths widget worker. This class is responsible to compute the
  Curves i.e. the path of the simulated robot and/or the target.

  Signals:
    computed_robot_path: Signal(glm.array)
      signal emitted to publish computed robot path
  """

  computed_robot_path = Signal(glm.array)

  def __init__(self) -> None:
    super(AnimPathsWidgetWorker, self).__init__()

    self._resolution = 12.0 # in msec (Every 12 msec a point is generated)
    self._robot_path = BezierSpline(logger=AnimPathsUILogger)
    self._robot_poses = glm.array(np.array([])).reinterpret_cast(glm.vec3)

  def _setup_robot_poses(self, poses: List) -> glm.array:
    """
    Method to setup the robot's poses to pass to the BezierSpline to compute the required
    robot's path.

    Arguments:
      poses: List
        robot pose

    Returns:
      poses_array: glm.array[glm.vec3]
        array containing robot poses
    """

    poses_array = glm.array(np.array([])).reinterpret_cast(glm.vec3)
    try:
      for pose in poses:
          poses_array = glm.array(poses_array).concat(
                          glm.array(
                            glm.vec3(pose['x_pose'], pose['y_pose'], pose['z_pose']),
                            glm.vec3(pose['a_pose'], pose['b_pose'], pose['c_pose'])
                          )
                        )
    except Exception:
      AnimPathsUILogger.exception("Unable to create array of poses because:")
    finally:
      return poses_array

  def _compute_num_samples(self, total_time: float) -> float:
    """
    Method to compute the number of samples required in the path generation.

    Arguments:
      total_time: float
        total time of the path in msec
    """

    if total_time < 0:
      total_time = 1000.0 # at least to have 1 sec

    return int(total_time/self._resolution)

  def update_sample_resolution(self, resolution: float) -> None:
    """
    Slot/Method to update the sample resultion. The resolution determines the rate of poses
    generated within a given time on a complete path.

    Arguments:
      resolution: float
        sample resolution
    """

    if resolution < 4.0:
      self._resolution = 4.0
      return

    self._resolution = resolution

  def compute_robot_path(self, total_time: float, poses: List) -> None:
    """
    Method to compute robot's path based on Bezier Spline.

    Arguments:
      total_time: float
        total time of the path in msec
      pose: List
        list of lists containing robot poses
    """

    if not poses:
      return

    self._robot_path.num_samples = self._compute_num_samples(total_time=total_time)
    self._robot_path.poses = self._setup_robot_poses(
                              poses=[item for sub in poses for item in sub]
                            ) # list of lists of dict
    self.computed_robot_path.emit(self._robot_path.spline_poses)


class AnimPathsWidget(QFrame):

  """
  Class to manage the Paths data/Keyframes data.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      widget settings

  Signals (to external widgets):
    playback_finished: Signal()
      signal emitted to report playback finished
    request_robot_current_pose: Signal()
      signal emitted to request the current pose of the robot
    request_target_current_pose: Signal()
      signal emitted to request the current pose of the target
    updated_robot_key_frames_data: Signal(list)
      signal emitted when key frames data of robot is updated
    updated_target_key_frames_data: Signal(list)
      signal emitted when key frames data of target is updated
    publish_robot_path_data_for_ik: Signal(glm.array)
      signal emitted when robot path data is sent to compute IK
    publish_robot_path_data_for_curve: Signal(glm.array)
      signal emitted when robot path data is sent to render curve
    publish_robot_pose_ik_for_pb: Signal(str, glm.array, list)
      signal emitted to publish robot pose & respective ik solution for playback

  Signals (to worker):
    req_robot_path_computation: Signal(float, list)
      signal emitted to request robot path computation
  """

  # Signals (to external widgets)
  playback_finished = Signal()
  request_robot_current_pose = Signal()
  request_target_current_pose = Signal()
  updated_robot_key_frames_data = Signal(list)
  updated_target_key_frames_data = Signal(list)
  publish_robot_path_data_for_ik = Signal(str, glm.array)
  publish_robot_path_data_for_curve = Signal(glm.array)
  publish_robot_pose_ik_for_pb = Signal(str, glm.array, list)

  # Signals (to worker)
  req_robot_path_computation = Signal(float, list)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(AnimPathsWidget, self).__init__(parent=self._parent)

    self._settings = kwargs.get('settings', None)

    # Assign attributes to the frame
    self.setObjectName(u"animPathsWidget")
    self.setWindowTitle(u"Animation Paths")
    if self._parent is None:
      self.resize(QSize(500, 392))

    # Curves/Path data
    self._rob_path = {}
    self._rob_path_gen = None
    self._rob_path_ik_sols = {}
    self._rob_path_ik_sols_gen = None

    self.init_UI()

    # It helps to delete old/empty log files
    AnimPathsUILogger.remove_log_files()

  def init_UI(self) -> None:
    # Create main layout
    animPathsHorizLayout = QHBoxLayout(self)
    animPathsHorizLayout.setObjectName(u"animPathsHorizLayout")

    # Paths data widget
    self.robot_paths_data_wdgt = PathsDataWidget(parent=self, settings=self._settings,
                                                 logger=AnimPathsUILogger, show_roll=True)
    self.target_paths_data_wdgt = PathsDataWidget(parent=self, settings=self._settings,
                                                  logger=AnimPathsUILogger)

    # Add widgets to the layout &set margins
    animPathsHorizLayout.addWidget(self.robot_paths_data_wdgt)
    animPathsHorizLayout.addWidget(self.target_paths_data_wdgt)
    animPathsHorizLayout.setContentsMargins(20, 10, 20, 10)
    animPathsHorizLayout.setSpacing(10)

    # Connections
    self._create_paths_data_wdgt_connects()

    # Workers & threads
    self._create_anim_paths_wdgt_worker_thread()

  def _create_paths_data_wdgt_connects(self) -> None:
    """
    Method to create connections of paths data widgets.
    """

    # PushButtons
    self.robot_paths_data_wdgt.addButton.clicked.connect(
      lambda: self.request_robot_current_pose.emit()
    )
    self.target_paths_data_wdgt.addButton.clicked.connect(
      lambda: self.request_target_current_pose.emit()
    )

    # Signals
    self.robot_paths_data_wdgt.updated_key_frames_data.connect(
      lambda data: self.updated_robot_key_frames_data.emit(data)
    )
    self.target_paths_data_wdgt.updated_key_frames_data.connect(
      lambda data: self.updated_target_key_frames_data.emit(data)
    )

  def _create_anim_paths_wdgt_worker_thread(self) -> None:
    """
    Method to create the widget worker thread.
    """

    # Create the Worker & Thread
    self.anim_paths_wdgt_worker_thread = QThread(self)
    self.anim_paths_wdgt_worker = AnimPathsWidgetWorker()
    self.anim_paths_wdgt_worker.moveToThread(self.anim_paths_wdgt_worker_thread)

    # Connections
    self.req_robot_path_computation.connect(self.anim_paths_wdgt_worker.compute_robot_path)

    self.anim_paths_wdgt_worker.computed_robot_path.connect(self._on_computed_robot_path_recvd)

    # Start the thread
    self.anim_paths_wdgt_worker_thread.start()

  def _update_target_paths_data_wdgt(self, data: Dict={}) -> None:
    """
    Method to update the data in robots path widget.
    """

    # data = {'path_of': 'robot', 'xpos': 1234.56, 'ypos': -4321.65, 'zpos': 7890.12, 'roll': -69.25}
    if not data:
      return

    self.target_paths_data_wdgt.keyFramesTableView.add_item(item=data)

  def _on_computed_robot_path_recvd(self, path_data: glm.array):
    """
    Slot/method called when computed robot path data received.

    Arguments:
      path_data: glm.array
        array containing robot path data
    """

    if len(path_data) == 0:
      return

    robot_name = self.robot_paths_data_wdgt.pathSourceComboBox.currentText()
    if robot_name:
      self._rob_path[robot_name] = path_data
      self.publish_robot_path_data_for_ik.emit(robot_name, path_data)
      self.publish_robot_path_data_for_curve.emit(
        self._rob_path[robot_name][0::2].reinterpret_cast(glm.float32)
      )

  def on_robots_got_added(self, robots: List) -> None:
    """
    Slot/Method called when robot configuration received.

    Arguments:
      robots: List
        list containing robots added
    """

    if not robots:
      return

    self.robot_paths_data_wdgt.pathSourceComboBox.clear()
    self.robot_paths_data_wdgt.pathSourceComboBox.addItems(robots)
    self.robot_paths_data_wdgt.addButton.setEnabled(True)

  def on_robot_current_pose_recvd(self, pose: Dict) -> None:
    """
    Slot/Method called when robot's updated pose received.

    Arguments:
      pose: Dict
        robot's current cartesian pose
    """

    if not pose:
      return

    try:
      data = {'path_of': 'robot', 'x_pose': pose['x_pose'], 'y_pose': pose['y_pose'],
              'z_pose': pose['z_pose'], 'a_pose': pose['a_pose'], 'b_pose': pose['b_pose'],
              'c_pose': pose['c_pose']}
      self.robot_paths_data_wdgt.keyFramesTableView.add_item(data=data)
    except Exception:
      AnimPathsUILogger.exception("Unable to add the data because:")

  def on_keyframes_with_total_time_recvd(self, total_time: float, keyframes: List) -> None:
    """
    Slot/Method called when keyframes with total time is received.

    Arguments:
      total_time: float
        total animation time
      keyframes: List
        list containing keyframes data
    """

    if total_time < 0.0:
      total_time = 0.0

    if not keyframes:
      return

    self.req_robot_path_computation.emit(total_time, keyframes)

  def on_robot_path_ik_solutions_recvd(self, robot_name: str, sols: List) -> None:
    """
    Slot/Method called when IK solutions of robot's path received.

    Arguments:
      robot_name: str
        name of the robot
      sols: List
        list containing the computed ik solutions
    """

    if not robot_name:
      return

    if not sols:
      return

    self._rob_path_ik_sols[robot_name] = sols

  def _robot_path_solutions_sanity_check(self, robot_name: str) -> bool:
    """
    Method to check the vailidity of the robot path and computed IK solutions.

    Arguments:
      robot_name: str
        name of the robot
    """

    valid = True
    try:
      assert robot_name in self._rob_path
      assert robot_name in self._rob_path_ik_sols
      assert len(self._rob_path) == len(self._rob_path_ik_sols)
    except AssertionError:
      valid = False
    finally:
      return valid

  def on_robot_pose_frm_path_req_for_pb(self, dir: str) -> None:
    """
    Slot/Method called when robot pose from path data is requested for the playback.

    Arguments:
      dir: str
        direction of playback
    """

    robot_name = self.robot_paths_data_wdgt.pathSourceComboBox.currentText()
    if not robot_name:
      return

    if not dir:
      dir = 'fwd'

    if self._robot_path_solutions_sanity_check(robot_name=robot_name):
      if self._rob_path_gen is None:
        if dir == 'fwd':
          self._rob_path_gen = (path for path in self._rob_path[robot_name])
        elif dir == 'bwd':
          self._rob_path_gen = reversed(self._rob_path[robot_name])

      if self._rob_path_ik_sols_gen is None:
        if dir == 'fwd':
          self._rob_path_ik_sols_gen = (sol for sol in self._rob_path_ik_sols[robot_name])
        elif dir == 'bwd':
          self._rob_path_ik_sols_gen = reversed(self._rob_path_ik_sols[robot_name])

      try:
        if dir == 'fwd':
          trans = next(self._rob_path_gen)
          angls = next(self._rob_path_gen)
        elif dir == 'bwd':
          angls = next(self._rob_path_gen)
          trans = next(self._rob_path_gen)
        self.publish_robot_pose_ik_for_pb.emit(
          robot_name, glm.array(trans, angls), next(self._rob_path_ik_sols_gen)
        )
      except StopIteration:
        self.playback_finished.emit()
        self._rob_path_gen = None
        self._rob_path_ik_sols_gen = None

  def save_state(self):
    """
    Method to save the widget state and perform cleanup before closing.
    """

    try:
      if self.anim_paths_wdgt_worker_thread.isRunning():
        self.anim_paths_wdgt_worker_thread.quit()
        self.anim_paths_wdgt_worker_thread.wait()
    except Exception:
      AnimPathsUILogger.exception("Unable to close the worker thread because:")

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called when the widget is closed.
    """

    self.save_state()
    return super(AnimPathsWidget, self).closeEvent(event)


class PathsDataWidget(QFrame):

  """
  Class to manage the animation/path data of the robot's TCP/Tool.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      widget settings
    logger: Logger
      logger class

  Signals:
    updated_key_frames_data: Signal(list)
      signal emitted to publish key frames data
  """

  updated_key_frames_data = Signal(list)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(PathsDataWidget, self).__init__(parent=self._parent)

    self._logger = kwargs['logger']
    self._settings = kwargs.get('settings', None)

    # Assign attributes to the frame
    self.setObjectName(u"pathDataWidget")
    self.setWindowTitle(u"Paths Data")
    if self._parent is None:
      self.resize(QSize(500, 392))

    self._show_roll = kwargs.get('show_roll', False)

    self._init_UI()

  def _init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create Main Layout
    pathsDataWdgtMainLayout = QVBoxLayout(self)
    pathsDataWdgtMainLayout.setObjectName(u"pathsDataWdgtMainLayout")

    self.keyFramesTableView = KeyFramesTableView(parent=self, logger=self._logger,
                                                 show_roll=self._show_roll)

    # Add widgets to the layout &set margins
    pathsDataWdgtMainLayout.addLayout(self._create_top_bar())
    pathsDataWdgtMainLayout.addWidget(self.keyFramesTableView)
    pathsDataWdgtMainLayout.addLayout(self._create_bottom_bar())
    pathsDataWdgtMainLayout.setContentsMargins(0, 0, 0, 0)
    pathsDataWdgtMainLayout.setSpacing(6)

    # Connections
    self._create_local_connects()

  def _create_top_bar(self) -> QHBoxLayout:
    """
    Method to create control widgets shown at the top bar.

    Returns:
      top_bar_layout: QHBoxLayout
        top bar horizontal layout
    """

    # Create layout
    topBarLayout = QHBoxLayout()
    topBarLayout.setObjectName(u"topBarLayout")

    # Label
    self.pathSourceComboBox = ComboBoxWidget(parent=self, logger=self._logger,
                                             type="sub_combo_box", minsize=QSize(0, 20))
    self.pathSourceComboBox.setObjectName(u"pathSourceComboBox")

    # Add widgets to the layout & set margins
    topBarLayout.addWidget(self.pathSourceComboBox)
    topBarLayout.setContentsMargins(0, 0, 0, 0)
    topBarLayout.setSpacing(6)

    return topBarLayout

  def _create_bottom_bar(self) -> QHBoxLayout:
    """
    Method to create control widgets shown at the bottom bar.

    Returns:
      bottom_bar_layout: QHBoxLayout
        bottom bar horizontal layout
    """

    # Create layout
    bottomBarLayout = QHBoxLayout()
    bottomBarLayout.setObjectName(u"bottomBarLayout")

    # Create Buttons
    self.addButton = PushButtonWidget(parent=self, logger=self._logger, text=u"Add",
                                      type="round_button", minsize=QSize(0, 20))
    self.addButton.setObjectName(u"addButton")
    self.addButton.setEnabled(False)

    self.delButton = PushButtonWidget(parent=self, logger=self._logger, text=u"Del",
                                      type="round_button", minsize=QSize(0, 20))
    self.delButton.setObjectName(u"delButton")
    self.delButton.setEnabled(False)

    # Add widgets to the layout & set margins
    bottomBarLayout.addWidget(self.addButton)
    bottomBarLayout.addWidget(self.delButton)
    bottomBarLayout.setContentsMargins(0, 0, 0, 0)
    bottomBarLayout.setSpacing(6)

    return bottomBarLayout

  def _create_local_connects(self) -> None:
    """
    Method to create connections of local widgets.
    """

    # PushButtons
    self.delButton.clicked.connect(self._on_del_button_clicked)

    # Table View
    self.keyFramesTableView.selectionModel().selectionChanged.connect(
      self._on_kf_table_selection_chngd
    )
    self.keyFramesTableView.key_frames_data.connect(
      lambda data: self.updated_key_frames_data.emit(data)
    )

  def _on_del_button_clicked(self) -> None:
    """
    Slot/Method called when delete button is clicked.
    """

    indexes = self.keyFramesTableView.selectedIndexes()
    if not indexes:
      self._logger.warning("No KeyFrames selected to remove")
      return

    self.keyFramesTableView.remove_row(indexes=indexes)

  def _on_kf_table_selection_chngd(self, selected: QItemSelection,
                                   deselected: QItemSelection) -> None:
    """
    Method to process the event when the item selection changes in the TableView.

    Arguments:
      selected: QItemSelection
        Item selected in the TableView.
      deselected: QItemSelection
        Item deselected in the TableView.
    """

    if selected.data() is None or not selected.data().isValid():
      self.delButton.setEnabled(False)
      return

    try:
      indexes = selected.indexes()
      if not indexes:
        return
      self.delButton.setEnabled(True)
    except Exception:
      self._logger.exception("Unable to get the item data because:")


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed Widget
  path_planning_widget = AnimPathsWidget()
  # Show the widget
  path_planning_widget.show()
  # execute the program
  sys.exit(app.exec())