## -*- coding: utf-8 -*- ##
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage widgets to control the Simulated robot.
##
##############################################################################################
##
import os
import sys
import glm
import posixpath

from typing import List, Dict

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QObject, QThread, QSize, Signal, Qt
from PySide6.QtWidgets import (QApplication, QFrame, QStackedWidget, QSpacerItem, QVBoxLayout,
                               QHBoxLayout, QGroupBox, QSizePolicy)

try:
  from config import ConfigRobot
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.artebotics.Optimization import OptimizedSolver
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget, PushButtonWidget, ComboBoxWidget
  from scripts.ui.widgets_sub.SimRobCtrlSubWidgets import SimRobCtrlWdgtsLayout
except:
  # For the development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from config import ConfigRobot
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
  from scripts.artebotics.Optimization import OptimizedSolver
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget, PushButtonWidget, ComboBoxWidget
  from scripts.ui.widgets_sub.SimRobCtrlSubWidgets import SimRobCtrlWdgtsLayout


class SimRobotCtrlUILogger(Logger):

  FILE_NAME = "ui_sim_robot_ctrl"
  LOGGER_NAME = "UISimRobotCtrl"


class SimRobotCtrlWdgtFunc:

  """
  Class to manage Simulation Robot Ctrl Widget functionality.

  Keyword Arguments:
    parent: QWidget
      parent widget
    logger: Logger
      Logger class
  """

  def __init__(self, **kwargs) -> None:
    super(SimRobotCtrlWdgtFunc, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    # Robots
    self.robots = {}

    # Robot's attributes
    # thetas
    self.Θ1 = self.Θ2 = self.Θ3 = self.Θ4 = self.Θ5 = self.Θ6 = 0.0

    # pose
    self.x = self.y = self.z = 0.0 # in meters
    self.a = self.b = self.c = 0.0 # in radians

  def read_settings(self) -> None:
    """
    Method responsible to read the Widget settings. It should be derived in sub class.
    """

    pass

  def compute_robot_fk(self, robot_name: str, angles: List) -> None:
    """
    Method to compute robot forward kinematics.

    Arguments:
      robot_name: str
        name of the robot
      angles: List
        list containing angle position of the axes of the robot
    """

    if robot_name not in self.robots:
      return

    if not angles:
      return

    self.robots[robot_name]['solver'].compute_fk(axes_angles=angles)

  def compute_robot_ik(self, robot_name: str, pose: glm.array, axes_angs: List[float]) -> List:
    """
    Method to compute robot inverse kinematics.

    Arguments:
      robot_name: str
        name of the robot
      pose: Dict
        updated cartesian pose values
      axes_angs: List[Float]
        current angle values of the robot axes

    Returns:
      res: List
        list containing computed axes angle values
    """

    if not robot_name:
      return

    if len(pose) == 0:
      return

    res = self.robots[robot_name]['solver'].compute_ik(
            tg_pose=pose.reinterpret_cast(glm.float32), axes_angles=axes_angs
          )

    return res

  def setup_robots(self, robot_name: str) -> bool:
    """
    Method to setup the robot/s. This method sets up robot config and solver.

    Arguments:
      robot_name: str
        name of the robot

    Returns:
      success: bool
        success flag
    """

    success = False
    try:
      if robot_name not in self.robots:
        self.robots[robot_name] = {}
        self.robots[robot_name]['config'] = ConfigRobot(config_file=robot_name + ".yaml")
        self.robots[robot_name]['solver'] = OptimizedSolver(
                                              Logger=SimRobotCtrlUILogger,
                                              robot_config=self.robots[robot_name]['config']
                                            )
        success = True
    except Exception:
      SimRobotCtrlUILogger.exception(
        f"Unable to setup {robot_name} robot configuration & solver because:"
      )
    finally:
      return success

  def update_current_thetas(self, Θs: List[float]) -> None:
    """
    Slot/Method to update the current axes angles.

    Keyword Arguments:
      Θs: List[float]
        current thetas
    """

    self.Θ1 = Θs[0]
    self.Θ2 = Θs[1]
    self.Θ3 = Θs[2]
    self.Θ4 = Θs[3]
    self.Θ5 = Θs[4]
    self.Θ6 = Θs[5]

  def update_current_pose(self, pose: glm.array) -> None:
    """
    Slot/Method to update the current pose of the robot.

    Keyword Arguments:
      pose: glm.array
        current pose of the robot
    """

    self.x = pose[0].x
    self.y = pose[0].y
    self.z = pose[0].z
    self.a = pose[1].z
    self.b = pose[1].y
    self.c = pose[1].x


class SimRobotCtrlWidget(SimRobotCtrlWdgtFunc, QFrame):

  """
  Class to manage the widget to control the simulated robot in 3D viewer.

  Keyword Arguments:
    parent : QWidget
      parent widget
    settings: QSettings
      settings of the widget
    logger : Logger
      Logger class

  Signals:
    sim_rob_ctrl_msg_sent: Signal(str)
      Signal to publish various event messages
    sim_rob_ctrl_current_pose: Signal(dict)
      signal emitted to publish current robot pose
    sim_rob_ctrl_added_robots: Signal(list)
      signal emitted to publish robots added
    sim_rob_ctrl_curves_ik_solutions: Signal(list)
      signal emitted to publish the ik solutions of curves/path data
    sim_rob_ctrl_create_update_robot_in_3d: Signal(object, list)
      signal emitted to create or update the robot in 3d
  """

  # Signals
  sim_rob_ctrl_msg_sent = Signal(str)
  sim_rob_ctrl_current_pose = Signal(dict)
  sim_rob_ctrl_added_robots = Signal(list)
  sim_rob_ctrl_curves_ik_solutions = Signal(str, list)
  sim_rob_ctrl_create_update_robot_in_3d = Signal(object, list)

  def __init__(self, **kwargs) -> None:
    kwargs['logger'] = SimRobotCtrlUILogger
    self._parent = kwargs.get('parent', None)
    super(SimRobotCtrlWidget, self).__init__(**kwargs)

    # Assign attributes to the frame
    self.setObjectName(u"simRobotCtrlWidget")
    self.setWindowTitle(u"Sim Robot Control")
    if self._parent is None:
      self.resize(QSize(500, 392))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Get the application settings
    self._settings = kwargs.get('settings', None)
    if self._settings is not None:
      self.read_settings()

    # Added robots
    self._added_robots = [] # list of robots added into the UI

    self.init_UI()

    # Set Scene Edit/Control Widget default stylesheet
    self.set_stylesheet()

    # It helps to delete old/empty log files
    SimRobotCtrlUILogger.remove_log_files()

  def init_UI(self) -> None:
    # Create main layout
    simRobotJogCtrlMainLayout = QVBoxLayout(self)
    simRobotJogCtrlMainLayout.setObjectName(u"simRobotJogCtrlMainLayout")

    # Create Layouts & Widgets
    self._create_top_vertical_layout()
    verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
    self._create_stacked_widget()

    # Add widgets to the layout &set margins
    simRobotJogCtrlMainLayout.addLayout(self.simRobCtrlTopVertLayout)
    simRobotJogCtrlMainLayout.addItem(verticalSpacer)
    simRobotJogCtrlMainLayout.addWidget(self.simRobotCtrlStackedWidget)
    simRobotJogCtrlMainLayout.setContentsMargins(20, 10, 20, 10)
    simRobotJogCtrlMainLayout.setSpacing(10)

    # Connections
    self._create_local_connect()
    self._create_axes_jogging_ctrl_page_connects()
    self._create_cart_jogging_ctrl_page_connects()

    # Initialize stacked widget
    self._on_page_select_button_clicked()
    self._on_stckd_wdgt_page_chngd()

  def set_stylesheet(self, theme: str='default', qss: str='SimRobotCtrlWidget.qss') -> None:
    try:
      # Set the StyleSheet
      qss_file = PathManager.get_qss_path(logger=SimRobotCtrlUILogger,
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

  def _create_stacked_wdgt_ctrl_btns_layout(self) -> QHBoxLayout:
    """
    Method to create a layout to manage the selection buttons of the stacked widget.
    """

    # Create buttons layout
    stackedWdgtsBtnsHorizLayout = QHBoxLayout()
    stackedWdgtsBtnsHorizLayout.setObjectName(u"stackedWdgtsBtnsHorizLayout")

    # Create buttons
    self.axesJogPageSelectButton = PushButtonWidget(parent=self, logger=SimRobotCtrlUILogger,
                                                    text=u"Axes Jogging", type="left_button",
                                                    minsize=QSize(0, 20))
    self.axesJogPageSelectButton.setObjectName(u"axesJogPageSelectButton")

    self.cartJogPageSelectButton = PushButtonWidget(parent=self, logger=SimRobotCtrlUILogger,
                                                    text=u"Cartesian Jogging",
                                                    type="right_button", minsize=QSize(0, 20))
    self.cartJogPageSelectButton.setObjectName(u"cartJogPageSelectButton")

    # Add widgets to layout & set margins
    stackedWdgtsBtnsHorizLayout.addWidget(self.axesJogPageSelectButton)
    stackedWdgtsBtnsHorizLayout.addWidget(self.cartJogPageSelectButton)
    stackedWdgtsBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    stackedWdgtsBtnsHorizLayout.setSpacing(0)

    return stackedWdgtsBtnsHorizLayout

  def _create_top_vertical_layout(self) -> None:
    """
    Method to create top vertical layout to manage Title label & selection buttons layout.
    """

    self.simRobCtrlTopVertLayout = QVBoxLayout()
    self.simRobCtrlTopVertLayout.setObjectName(u"simRobCtrlTopVertLayout")

    # Create title label
    simRobotCtrlTitleLabel = LabelWidget(parent=self, logger=SimRobotCtrlUILogger,
                                         text=u"Robot Controls", minsize=QSize(0, 20),
                                         align=Qt.AlignCenter)
    simRobotCtrlTitleLabel.setObjectName(u"simRobotCtrlTitleLabel")

    btnsHorizLayout = self._create_stacked_wdgt_ctrl_btns_layout()

    # Create Robot selection
    simRobSelectHorizLayout = QHBoxLayout()
    simRobSelectHorizLayout.setObjectName(u"simRobSelectHorizLayout")

    # Robot Selection
    self.simRobSelComboBox = ComboBoxWidget(parent=self, logger=SimRobotCtrlUILogger,
                                            type="sub_combo_box", minsize=QSize(0, 20))
    self.simRobSelComboBox.setObjectName(u"simRobSelComboBox")

    # Home Pushbutton
    self.simRobHomeBttn = PushButtonWidget(parent=self, logger=self._logger, text=u"Home",
                                           type="round_button", minsize=QSize(70, 20))
    self.simRobHomeBttn.setObjectName(u"simRobHomeBttn")

    # Add widgets to layout & set margins
    simRobSelectHorizLayout.addWidget(self.simRobSelComboBox)
    simRobSelectHorizLayout.addWidget(self.simRobHomeBttn)
    simRobSelectHorizLayout.setContentsMargins(0, 0, 0, 0)
    simRobSelectHorizLayout.setSpacing(150)

    # Add widgets to layout & set margins
    self.simRobCtrlTopVertLayout.addWidget(simRobotCtrlTitleLabel)
    self.simRobCtrlTopVertLayout.addLayout(simRobSelectHorizLayout)
    self.simRobCtrlTopVertLayout.addLayout(btnsHorizLayout)
    self.simRobCtrlTopVertLayout.setContentsMargins(0, 0, 0, 0)
    self.simRobCtrlTopVertLayout.setSpacing(15)

  def _create_stacked_widget(self) -> None:
    """
    Main method to create stacked widget with required pages.
    """

    # Create stacked widget
    self.simRobotCtrlStackedWidget = QStackedWidget(self)
    self.simRobotCtrlStackedWidget.setObjectName(u"simRobotCtrlStackedWidget")

    # Create pages
    self.axesJoggingCtrlPage = AxesJoggingCtrlPage(parent=self, settings=self._settings,
                                                   logger=SimRobotCtrlUILogger)

    self.cartJoggingCtrlPage = CartJoggingCtrlPage(parent=self, settings=self._settings,
                                                   logger=SimRobotCtrlUILogger)

    # Add Pages
    self.simRobotCtrlStackedWidget.addWidget(self.axesJoggingCtrlPage)
    self.simRobotCtrlStackedWidget.addWidget(self.cartJoggingCtrlPage)

  def _create_local_connect(self) -> None:
    """
    Method to create connections of signals of the local widgets to the respective slots.
    """

    # Pushbuttons
    self.simRobHomeBttn.clicked.connect(self._send_robot_to_home)
    self.axesJogPageSelectButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=0)
    )
    self.cartJogPageSelectButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=1)
    )

    # Stacked Widget
    self.simRobotCtrlStackedWidget.currentChanged.connect(
      self._on_stckd_wdgt_page_chngd
    )

  def _create_axes_jogging_ctrl_page_connects(self) -> None:
    """
    Method to create the connections of signals/widgets of Axes Jogging Control page.
    """

    # Signals
    self.axesJoggingCtrlPage.axes_jog_ctrl_update_thetas.connect(
      self.on_updated_theta_value_recvd_frm_ui
    )

  def _create_cart_jogging_ctrl_page_connects(self) -> None:
    """
    Method to create the connections of signals/widgets of Cartesian Jogging Control page.
    """

    # Signals
    self.cartJoggingCtrlPage.cart_jog_ctrl_update_pose.connect(
      self.on_updated_cart_value_recvd_frm_ui
    )

  def _on_page_select_button_clicked(self, idx: int=0) -> None:
    """
    Method to process the event when selection button clicked.

    Argument:
      idx: int
        index of the page to be made active
    """

    self.simRobotCtrlStackedWidget.setCurrentIndex(idx)

  def _on_stckd_wdgt_page_chngd(self, idx: int=0) -> None:
    """
    Method to process the event when the page of stacked widget changes.

    Argument:
      idx: int
        index of the page to be made active
    """

    if not isinstance(idx, int):
      SimRobotCtrlUILogger.warning("Invalid index type received")
      return

    if idx == 0:
      self.axesJogPageSelectButton.setEnabled(False)
      self.cartJogPageSelectButton.setEnabled(True)
    elif idx == 1:
      self.axesJogPageSelectButton.setEnabled(True)
      self.cartJogPageSelectButton.setEnabled(False)

  def _manage_robots_in_the_scene(self, robot_name: str) -> bool:
    """
    Method to manage the robots in the scene/UI.

    Arguments:
      robot_name: str
        name of the robot

    Returns:
      added: bool
        added flag
    """

    added = False

    if robot_name in self._added_robots:
      return added

    self._added_robots.append(robot_name)
    self.simRobSelComboBox.clear()
    self.simRobSelComboBox.addItems(self._added_robots)
    self.sim_rob_ctrl_added_robots.emit(self._added_robots)
    added = True

    return added

  def on_updated_theta_value_recvd_frm_ui(self, robot_name: str, Θs: Dict) -> None:
    """
    Slot/Method called when updated theta values of the robot is received from robot's axes
    jogging control widgets.

    Keyword Arguments:
      robot_name: str
        name of the robot
      Θs: Dict
        thetas current values
    """

    if not Θs:
      return

    if not robot_name:
      robot_name = self.simRobSelComboBox.currentText()

    # Check again to make sure that the robot is solvable
    if robot_name not in self.robots:
      return

    angles = [Θs['Θ1'], Θs['Θ2'], Θs['Θ3'], Θs['Θ4'], Θs['Θ5'], Θs['Θ6']]

    try:
      self.compute_robot_fk(robot_name=robot_name, angles=angles)
    except Exception:
      SimRobotCtrlUILogger.exception(f"Unable to compute {robot_name} FK because:")
      return
    else:
      self.update_current_thetas(angles)
      self.sim_rob_ctrl_create_update_robot_in_3d.emit(
        self.robots[robot_name]['config'], self.robots[robot_name]['solver'].fk.axes_transforms
      )
      self.on_updated_pose_values_recvd(pose=self.robots[robot_name]['solver'].fk.robot_pose)

  def move_robot_via_ik_sol(self, robot_name: str, sol: List) -> None:
    """
    Method called to move the robot using IK solutions.

    Arguments:
      robot_name: str
        name of the robot
      pose: glm.array
        cartesian pose values
      sols: List
        list containing solutions from IK
    """

    if not sol:
      return

    try:
      self.compute_robot_fk(robot_name=robot_name, angles=sol[1])
    except Exception:
      SimRobotCtrlUILogger.exception(f"Unable to compute {robot_name} FK because:")
      return
    else:
      self.sim_rob_ctrl_create_update_robot_in_3d.emit(
        self.robots[robot_name]['config'], self.robots[robot_name]['solver'].fk.axes_transforms
      )
      self.on_updated_theta_values_recvd(Θs=sol[1])
      self.on_robot_axes_position_limits_reached(last_tg_pose=sol[0], axes_out_of_limits=sol[2])

  def on_updated_cart_value_recvd_frm_ui(self, robot_name: str, pose: glm.array) -> None:
    """
    Slot/Method called when updated cartesian pose values of the robot is received from robot's
    cartesian jogging control widgets.

    Keyword Arguments:
      pose: glm.array
        cartesian pose values
      robot_name: str
        name of the robot
    """

    if len(pose) == 0:
      return

    if not robot_name:
      robot_name = self.simRobSelComboBox.currentText()

    # Check again to make sure that the robot is solvable
    if robot_name not in self.robots:
      return

    try:
      res = self.compute_robot_ik(
              robot_name=robot_name, pose=pose,
              axes_angs=[self.Θ1, self.Θ2, self.Θ3, self.Θ4, self.Θ5, self.Θ6]
            )
    except Exception:
      SimRobotCtrlUILogger.exception(f"Unable to compute {robot_name} IK because:")
    else:
      self.move_robot_via_ik_sol(robot_name=robot_name, sol=res)
      self.update_current_pose(pose=pose)

  def _send_robot_to_home(self) -> None:
    """
    Slot/Method called when the robot is requested to be sent to the home position.
    """

    robot_name = self.simRobSelComboBox.currentText()
    if not robot_name:
      return

    home = self.robots[robot_name]['solver'].ik.home
    self.on_updated_theta_value_recvd_frm_ui(
      robot_name=robot_name,
      Θs={'Θ1': home[0], 'Θ2': home[1], 'Θ3': home[2],
          'Θ4': home[3], 'Θ5': home[4], 'Θ6': home[5]}
    )

    # Update Axes Jogging Control Page
    self.axesJoggingCtrlPage.update_current_thetas(
      Θ1=home[0], Θ2=home[1], Θ3=home[2], Θ4=home[3], Θ5=home[4], Θ6=home[5]
    )

  def on_add_robot_req_recvd(self, robot_name: str) -> None:
    """
    Slot/Method called when request received to add a robot.

    Arguments:
      robot_name: str
        name of the robot
    """

    if not robot_name:
      return

    if not self._manage_robots_in_the_scene(robot_name=robot_name):
      return

    if self.setup_robots(robot_name=robot_name):
      limits = self.robots[robot_name]['solver'].ik.axes_pos_limits
      # Update Axes Jogging Control Page
      self.axesJoggingCtrlPage.update_thetas_limits(
        Θ1_limits=limits[0], Θ2_limits=limits[1], Θ3_limits=limits[2],
        Θ4_limits=limits[3], Θ5_limits=limits[4], Θ6_limits=limits[5],
      )
      self._send_robot_to_home()

  def on_updated_theta_values_recvd(self, Θs: List[float]) -> None:
    """
    Slot/Method called when updated theta values of the robot is received and robot's axes
    jogging control widgets are updated.

    Keyword Arguments:
      Θs: Dict
        thetas current values
    """

    if not Θs:
      return

    self.update_current_thetas(Θs=Θs)

    # Update Axes Jogging Control Page
    self.axesJoggingCtrlPage.update_current_thetas(
      Θ1=self.Θ1, Θ2=self.Θ2, Θ3=self.Θ3, Θ4=self.Θ4, Θ5=self.Θ5, Θ6=self.Θ6
    )

  def on_updated_pose_values_recvd(self, pose: glm.array) -> None:
    """
    Slot/Method called when updated pose values of the robot is received and robot's cartesian
    jogging control widgets are updated.

    Keyword Arguments:
      pose: Dict
        current pose of the robot
    """

    if not pose:
      return

    self.update_current_pose(pose)

    # Update cartesian jogging control page
    self.cartJoggingCtrlPage.update_current_cartesian_pose(
      x_pose=self.x, y_pose=self.y, z_pose=self.z, a_pose=self.a, b_pose=self.b, c_pose=self.c
    )

  def on_current_robot_pose_req_recvd(self) -> None:
    """
    Slot/Method called when a request received to publish current robot cartesian pose values.
    """

    self.sim_rob_ctrl_current_pose.emit(
      {
        'x_pose': self.x,
        'y_pose': self.y,
        'z_pose': self.z,
        'a_pose': self.a,
        'b_pose': self.b,
        'c_pose': self.c
      }
    )

  def on_robot_axes_position_limits_reached(self, last_tg_pose: glm.array,
                                            axes_out_of_limits: List) -> None:
    """
    Slot/Method called when robot axes reached their position limits.
    """

    if not axes_out_of_limits:
      return

    for a in axes_out_of_limits:
      msg = f"Axes-{a+1} position limit has been violated!!!"
      SimRobotCtrlUILogger.warning(msg)
      self.sim_rob_ctrl_msg_sent.emit(msg)

    self.on_updated_pose_values_recvd(pose=last_tg_pose)

  def on_curves_data_ik_computation_req_recvd(self, robot_name: str, path_data: glm.array) -> None:
    """
    Slot/Method called when IK computation is requested of robot's path data.

    Arguments:
      robot_name: str
        name of the robot
      path_data: glm.array
        array containing curves/path data
    """

    if robot_name not in self._added_robots:
      return

    if len(path_data) == 0:
      return

    try:
      path_data_iter = iter(path_data)
      results = [self.compute_robot_ik(robot_name=robot_name,
                                      pose=glm.array(vec, next(path_data_iter)),
                                      axes_angs=[])
                for vec in path_data_iter]
    except Exception:
      SimRobotCtrlUILogger.exception("Unable to compute IK solutions of curves/path data because:")
    else:
      self.sim_rob_ctrl_curves_ik_solutions.emit(robot_name, results)

  def on_updated_ik_sol_received_for_pb(self, robot_name: str, pose: glm.array, sol: List) -> None:
    """
    Slot/Method when computed IK solution received to perform a playback.

    Arguments:
      robot_name: str
        name of the robot
      path_data: glm.array
        array containing curves/path data
      sol: List
        list containing IK solution
    """

    if robot_name not in self.robots:
      return

    self.move_robot_via_ik_sol(robot_name=robot_name, sol=sol)
    if not sol[2]: self.on_updated_pose_values_recvd(pose=pose)

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
    return super(SimRobotCtrlWidget, self).closeEvent(event)


class AxesJoggingCtrlPage(QFrame):

  """
  Class to manage the page widget to control the robot using Axes jogging.

  Signals:
    axes_jog_ctrl_update_thetas: Signal(dict)
      signal emitted to update the theta values
    axes_jog_ctrl_home_pose: Signal()
      signal emitted to send the robot to home pose

  Keyword Arguments:
    parent : QWidget
      parent widget
    settings: QSettings
      settings of the widget
    logger : Logger
      Logger class
  """

  # Signals
  axes_jog_ctrl_update_thetas = Signal(str, dict)

  def __init__(self, **kwargs) -> None:
    super(AxesJoggingCtrlPage, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"axesJoggingCtrlPage")
    if kwargs.get('parent') is None:
      self.resize(QSize(375, 382))

    self.init_UI()

    # Update theta limits & apply
    self.update_thetas_limits()

    # Update current theta values & apply
    self.update_current_thetas()

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create widget layout
    axesJogCtrlPageVertLayout = QVBoxLayout(self)
    axesJogCtrlPageVertLayout.setObjectName(u"axesJogCtrlPageVertLayout")

    # Create group boxes
    self._create_axes_theta_ctrl_grp_box()

    # Add widgets to layout & set margins
    # axesJogCtrlPageVertLayout.addLayout(miscellaneousCtrlHorizLayout)
    axesJogCtrlPageVertLayout.addWidget(self.axesThetaCtrlGrpBox)
    axesJogCtrlPageVertLayout.setContentsMargins(15, 0, 15, 0)
    axesJogCtrlPageVertLayout.setSpacing(6)

    # Connections
    self._create_local_connects()

  def _create_axes_theta_ctrl_grp_box(self) -> None:
    """
    Method to create a group box to manage the widgets to control the theta values of a robot's
    axes.
    """

    # Create Group Box
    self.axesThetaCtrlGrpBox = QGroupBox(parent=self, title=u"Axes Controls")
    self.axesThetaCtrlGrpBox.setObjectName(u"axesThetaCtrlGrpBox")

    # Create Layout
    axesThetaCtrlVertLayout = QVBoxLayout(self.axesThetaCtrlGrpBox)
    axesThetaCtrlVertLayout.setObjectName(u"axesThetaCtrlVertLayout")

    # Create Sub Layouts
    self.theta_1 = SimRobCtrlWdgtsLayout(parent=self.axesThetaCtrlGrpBox, logger=self._logger,
                                         lbl_txt=u"Θ₁: ", show_limits=True)
    self.theta_2 = SimRobCtrlWdgtsLayout(parent=self.axesThetaCtrlGrpBox, logger=self._logger,
                                         lbl_txt=u"Θ₂: ", show_limits=True)
    self.theta_3 = SimRobCtrlWdgtsLayout(parent=self.axesThetaCtrlGrpBox, logger=self._logger,
                                         lbl_txt=u"Θ₃: ", show_limits=True)
    self.theta_4 = SimRobCtrlWdgtsLayout(parent=self.axesThetaCtrlGrpBox, logger=self._logger,
                                         lbl_txt=u"Θ₄: ", show_limits=True)
    self.theta_5 = SimRobCtrlWdgtsLayout(parent=self.axesThetaCtrlGrpBox, logger=self._logger,
                                         lbl_txt=u"Θ₅: ", show_limits=True)
    self.theta_6 = SimRobCtrlWdgtsLayout(parent=self.axesThetaCtrlGrpBox, logger=self._logger,
                                         lbl_txt=u"Θ₆: ", show_limits=True)

    # Add widgets to layout & set margins
    axesThetaCtrlVertLayout.addLayout(self.theta_1)
    axesThetaCtrlVertLayout.addLayout(self.theta_2)
    axesThetaCtrlVertLayout.addLayout(self.theta_3)
    axesThetaCtrlVertLayout.addLayout(self.theta_4)
    axesThetaCtrlVertLayout.addLayout(self.theta_5)
    axesThetaCtrlVertLayout.addLayout(self.theta_6)
    axesThetaCtrlVertLayout.setContentsMargins(10, 15, 0, 0)
    axesThetaCtrlVertLayout.setSpacing(6)

  def _create_local_connects(self) -> None:
    """
    Method to create connections of signals of the local widgets to the respective slots.
    """

    # LineEdits
    self.theta_1.lineEdit.text_modified.connect(
      lambda: self._on_thetas_values_changed_using_line_edits(
        idx=1, value=float(self.theta_1.lineEdit.text())
      )
    )
    self.theta_2.lineEdit.text_modified.connect(
      lambda: self._on_thetas_values_changed_using_line_edits(
        idx=2, value=float(self.theta_2.lineEdit.text())
      )
    )
    self.theta_3.lineEdit.text_modified.connect(
      lambda: self._on_thetas_values_changed_using_line_edits(
        idx=3, value=float(self.theta_3.lineEdit.text())
      )
    )
    self.theta_4.lineEdit.text_modified.connect(
      lambda: self._on_thetas_values_changed_using_line_edits(
        idx=4, value=float(self.theta_4.lineEdit.text())
      )
    )
    self.theta_5.lineEdit.text_modified.connect(
      lambda: self._on_thetas_values_changed_using_line_edits(
        idx=5, value=float(self.theta_5.lineEdit.text())
      )
    )
    self.theta_6.lineEdit.text_modified.connect(
      lambda: self._on_thetas_values_changed_using_line_edits(
        idx=6, value=float(self.theta_6.lineEdit.text())
      )
    )

    # Sliders
    self.theta_1.sliderWidget.value_modified.connect(
      lambda: self._on_thetas_values_changed_using_sliders(
        idx=1, value=float(self.theta_1.sliderWidget.value())
      )
    )
    self.theta_2.sliderWidget.value_modified.connect(
      lambda: self._on_thetas_values_changed_using_sliders(
        idx=2, value=float(self.theta_2.sliderWidget.value())
      )
    )
    self.theta_3.sliderWidget.value_modified.connect(
      lambda: self._on_thetas_values_changed_using_sliders(
        idx=3, value=float(self.theta_3.sliderWidget.value())
      )
    )
    self.theta_4.sliderWidget.value_modified.connect(
      lambda: self._on_thetas_values_changed_using_sliders(
        idx=4, value=float(self.theta_4.sliderWidget.value())
      )
    )
    self.theta_5.sliderWidget.value_modified.connect(
      lambda: self._on_thetas_values_changed_using_sliders(
        idx=5, value=float(self.theta_5.sliderWidget.value())
      )
    )
    self.theta_6.sliderWidget.value_modified.connect(
      lambda: self._on_thetas_values_changed_using_sliders(
        idx=6, value=float(self.theta_6.sliderWidget.value())
      )
    )

  def _on_thetas_limits_changed(self) -> None:
    """
    Method called when theta limits get updated to update the UI elements.
    """

    # Labels
    if hasattr(self.theta_1, 'lowLimLabel'): self.theta_1.lowLimLabel.setText(f"{self._Θ1_limits[0]:>6}°")
    if hasattr(self.theta_1, 'upLimLabel'): self.theta_1.upLimLabel.setText(f"{self._Θ1_limits[1]:>5}°")
    if hasattr(self.theta_2, 'lowLimLabel'): self.theta_2.lowLimLabel.setText(f"{self._Θ2_limits[0]:>6}°")
    if hasattr(self.theta_2, 'upLimLabel'): self.theta_2.upLimLabel.setText(f"{self._Θ2_limits[1]:>5}°")
    if hasattr(self.theta_3, 'lowLimLabel'): self.theta_3.lowLimLabel.setText(f"{self._Θ3_limits[0]:>6}°")
    if hasattr(self.theta_3, 'upLimLabel'): self.theta_3.upLimLabel.setText(f"{self._Θ3_limits[1]:>5}°")
    if hasattr(self.theta_4, 'lowLimLabel'): self.theta_4.lowLimLabel.setText(f"{self._Θ4_limits[0]:>6}°")
    if hasattr(self.theta_4, 'upLimLabel'): self.theta_4.upLimLabel.setText(f"{self._Θ4_limits[1]:>5}°")
    if hasattr(self.theta_5, 'lowLimLabel'): self.theta_5.lowLimLabel.setText(f"{self._Θ5_limits[0]:>6}°")
    if hasattr(self.theta_5, 'upLimLabel'): self.theta_5.upLimLabel.setText(f"{self._Θ5_limits[1]:>5}°")
    if hasattr(self.theta_6, 'lowLimLabel'): self.theta_6.lowLimLabel.setText(f"{self._Θ6_limits[0]:>6}°")
    if hasattr(self.theta_6, 'upLimLabel'): self.theta_6.upLimLabel.setText(f"{self._Θ6_limits[1]:>5}°")

    # LineEdits
    self.theta_1.lineEdit.min = self._Θ1_limits[0]
    self.theta_1.lineEdit.max = self._Θ1_limits[1]
    self.theta_2.lineEdit.min = self._Θ2_limits[0]
    self.theta_2.lineEdit.max = self._Θ2_limits[1]
    self.theta_3.lineEdit.min = self._Θ3_limits[0]
    self.theta_3.lineEdit.max = self._Θ3_limits[1]
    self.theta_4.lineEdit.min = self._Θ4_limits[0]
    self.theta_4.lineEdit.max = self._Θ4_limits[1]
    self.theta_5.lineEdit.min = self._Θ5_limits[0]
    self.theta_5.lineEdit.max = self._Θ5_limits[1]
    self.theta_6.lineEdit.min = self._Θ6_limits[0]
    self.theta_6.lineEdit.max = self._Θ6_limits[1]

    # Sliders
    self.theta_1.sliderWidget.min = self._Θ1_limits[0]
    self.theta_1.sliderWidget.max = self._Θ1_limits[1]
    self.theta_2.sliderWidget.min = self._Θ2_limits[0]
    self.theta_2.sliderWidget.max = self._Θ2_limits[1]
    self.theta_3.sliderWidget.min = self._Θ3_limits[0]
    self.theta_3.sliderWidget.max = self._Θ3_limits[1]
    self.theta_4.sliderWidget.min = self._Θ4_limits[0]
    self.theta_4.sliderWidget.max = self._Θ4_limits[1]
    self.theta_5.sliderWidget.min = self._Θ5_limits[0]
    self.theta_5.sliderWidget.max = self._Θ5_limits[1]
    self.theta_6.sliderWidget.min = self._Θ6_limits[0]
    self.theta_6.sliderWidget.max = self._Θ6_limits[1]

  def _update_thetas_locally(self, idx: int, value: float) -> None:
    """
    Decorator method to update the thetas based on local widgets.

    Arguments:
      idx: int
        theta index
      values: float
        theta value
    """

    if not idx:
      self._logger.warning("Not a valid theta index!!!")
      return

    if idx == 1: self._Θ1 = value
    elif idx == 2: self._Θ2 = value
    elif idx == 3: self._Θ3 = value
    elif idx == 4: self._Θ4 = value
    elif idx == 5: self._Θ5 = value
    elif idx == 6: self._Θ6 = value

    self.axes_jog_ctrl_update_thetas.emit('',
      {'Θ1': self._Θ1, 'Θ2': self._Θ2, 'Θ3': self._Θ3,
       'Θ4': self._Θ4, 'Θ5': self._Θ5, 'Θ6': self._Θ6}
    )

  def _update_line_edits_on_thetas_values_changed(self) -> None:
    """
    Method called when theta values get updated to update the LineEdits.
    """

    # LineEdits
    self.theta_1.lineEdit.setText(f"{self._Θ1:.2f}")
    self.theta_2.lineEdit.setText(f"{self._Θ2:.2f}")
    self.theta_3.lineEdit.setText(f"{self._Θ3:.2f}")
    self.theta_4.lineEdit.setText(f"{self._Θ4:.2f}")
    self.theta_5.lineEdit.setText(f"{self._Θ5:.2f}")
    self.theta_6.lineEdit.setText(f"{self._Θ6:.2f}")

  def _update_sliders_on_thetas_values_changed(self) -> None:
    """
    Method called when theta values get updated to update the Sliders.
    """

    # Sliders
    self.theta_1.sliderWidget.set_value(self._Θ1)
    self.theta_2.sliderWidget.set_value(self._Θ2)
    self.theta_3.sliderWidget.set_value(self._Θ3)
    self.theta_4.sliderWidget.set_value(self._Θ4)
    self.theta_5.sliderWidget.set_value(self._Θ5)
    self.theta_6.sliderWidget.set_value(self._Θ6)

  def _on_thetas_values_changed_using_line_edits(self, idx: int, value: float) -> None:
    """
    Slot/Method called when the theta values changed using the LineEdits.

    Arguments:
      idx: int
        theta index
      value: float
        theta value
    """

    self._update_thetas_locally(idx=idx, value=value)

    self._update_sliders_on_thetas_values_changed()

  def _on_thetas_values_changed_using_sliders(self, idx: int, value: float) -> None:
    """
    Slot/Method called when the theta values changed using the Sliders.

    Arguments:
      idx: int
        theta index
      value: float
        theta value
    """

    self._update_thetas_locally(idx=idx, value=value)

    self._update_line_edits_on_thetas_values_changed()

  def update_thetas_limits(self, **Θs_limits: Dict) -> None:
    """
    Method to update the theta limits.

    Keyword Arguments:
      Θ1_limits: List
        theta 1 limits (in Degrees)
      Θ2_limits: List
        theta 2 limits (in Degrees)
      Θ3_limits: List
        theta 3 limits (in Degrees)
      Θ4_limits: List
        theta 4 limits (in Degrees)
      Θ5_limits: List
        theta 5 limits (in Degrees)
      Θ6_limits: List
        theta 6 limits (in Degrees)
    """

    self._Θ1_limits = Θs_limits.get('Θ1_limits', [-360, 360])
    self._Θ2_limits = Θs_limits.get('Θ2_limits', [-360, 360])
    self._Θ3_limits = Θs_limits.get('Θ3_limits', [-360, 360])
    self._Θ4_limits = Θs_limits.get('Θ4_limits', [-360, 360])
    self._Θ5_limits = Θs_limits.get('Θ5_limits', [-360, 360])
    self._Θ6_limits = Θs_limits.get('Θ6_limits', [-360, 360])

    # Apply limit values
    self._on_thetas_limits_changed()

  def update_current_thetas(self, **Θs) -> None:
    """
    Slot/Mathod to update the current theta value of the robot.

    Keyword Arguments:
      Θ1: float
        theta1 value (in Degrees)
      Θ2: float
        theta2 value (in Degrees)
      Θ3: float
        theta3 value (in Degrees)
      Θ4: float
        theta4 value (in Degrees)
      Θ5: float
        theta5 value (in Degrees)
      Θ6: float
        theta6 value (in Degrees)
    """

    self._Θ1 = Θs.get('Θ1', 0.0)
    self._Θ2 = Θs.get('Θ2', 0.0)
    self._Θ3 = Θs.get('Θ3', 0.0)
    self._Θ4 = Θs.get('Θ4', 0.0)
    self._Θ5 = Θs.get('Θ5', 0.0)
    self._Θ6 = Θs.get('Θ6', 0.0)

    self._update_line_edits_on_thetas_values_changed()
    self._update_sliders_on_thetas_values_changed()


class CartJoggingCtrlPage(QFrame):

  """
  Class to manage the page widget to control the robot using cartesian jogging.

  Keyword Arguments:
    parent : QWidget
      parent widget
    settings: QSettings
      settings of the widget
    logger : Logger
      Logger class
  """

  # Constants
  POSE_LE_W = 45
  POSE_LBL_W = 30
  POSE_LIM_LBL_W = 70
  POSE_WDGT_H = 20
  POSE_VALUE_PRECISION = 0.1

  # Signals
  cart_jog_ctrl_update_pose = Signal(str, glm.array)

  def __init__(self, **kwargs) -> None:
    super(CartJoggingCtrlPage, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"cartJoggingCtrlPage")
    if kwargs.get('parent') is None:
      self.resize(QSize(375, 382))

    self.init_UI()

    # # Update pose limits & apply
    self.update_cartesian_pose_limits()

    # # Update current pose & apply
    self.update_current_cartesian_pose()

  def init_UI(self) -> None:
    # Create widget layout
    cartJogCtrlPageVertLayout = QVBoxLayout(self)
    cartJogCtrlPageVertLayout.setObjectName(u"cartJogCtrlPageVertLayout")

    # Create group boxes
    self._create_cartesian_pose_ctrl_grp_box()

    # Add widgets to layout & set margins
    cartJogCtrlPageVertLayout.addWidget(self.cartPoseCtrlGrpBox)
    cartJogCtrlPageVertLayout.setContentsMargins(15, 0, 15, 0)
    cartJogCtrlPageVertLayout.setSpacing(30)

    # # Connections
    self._create_local_connects()

  def _create_cartesian_pose_ctrl_grp_box(self) -> None:
    """
    Method to create a group box to manage the widgets to control the cartesian values of a
    robot's pose.
    """

    # Create Group Box
    self.cartPoseCtrlGrpBox = QGroupBox(parent=self, title=u"Axes Controls")
    self.cartPoseCtrlGrpBox.setObjectName(u"cartPoseCtrlGrpBox")

    # Create Layout
    cartPoseCtrlVertLayout = QVBoxLayout(self.cartPoseCtrlGrpBox)
    cartPoseCtrlVertLayout.setObjectName(u"axesThetaCtrlVertLayout")

    # Create Sub Layouts
    self.y_pose = SimRobCtrlWdgtsLayout(parent=self.cartPoseCtrlGrpBox, logger=self._logger,
                                        lbl_txt=u"Y:  ")
    self.z_pose = SimRobCtrlWdgtsLayout(parent=self.cartPoseCtrlGrpBox, logger=self._logger,
                                        lbl_txt=u"Z:  ")
    self.x_pose = SimRobCtrlWdgtsLayout(parent=self.cartPoseCtrlGrpBox, logger=self._logger,
                                        lbl_txt=u"X:  ")
    self.a_pose = SimRobCtrlWdgtsLayout(parent=self.cartPoseCtrlGrpBox, logger=self._logger,
                                        lbl_txt=u"A:  ")
    self.b_pose = SimRobCtrlWdgtsLayout(parent=self.cartPoseCtrlGrpBox, logger=self._logger,
                                        lbl_txt=u"B:  ")
    self.c_pose = SimRobCtrlWdgtsLayout(parent=self.cartPoseCtrlGrpBox, logger=self._logger,
                                        lbl_txt=u"C:  ")

    # Add widgets to layout & set margins
    cartPoseCtrlVertLayout.addLayout(self.x_pose)
    cartPoseCtrlVertLayout.addLayout(self.y_pose)
    cartPoseCtrlVertLayout.addLayout(self.z_pose)
    cartPoseCtrlVertLayout.addLayout(self.a_pose)
    cartPoseCtrlVertLayout.addLayout(self.b_pose)
    cartPoseCtrlVertLayout.addLayout(self.c_pose)
    cartPoseCtrlVertLayout.setContentsMargins(10, 15, 0, 0)
    cartPoseCtrlVertLayout.setSpacing(6)

  def _create_local_connects(self) -> None:
    """
    Method to create connections of signals of the local widgets to the respective slots.
    """

    # LineEdits
    self.x_pose.lineEdit.text_modified.connect(
      lambda: self._on_cart_pose_changed_using_line_edits(
        pose='x', value=float(self.x_pose.lineEdit.text())
      )
    )
    self.y_pose.lineEdit.text_modified.connect(
      lambda: self._on_cart_pose_changed_using_line_edits(
        pose='y', value=float(self.y_pose.lineEdit.text())
      )
    )
    self.z_pose.lineEdit.text_modified.connect(
      lambda: self._on_cart_pose_changed_using_line_edits(
        pose='z', value=float(self.z_pose.lineEdit.text())
      )
    )
    self.a_pose.lineEdit.text_modified.connect(
      lambda: self._on_cart_pose_changed_using_line_edits(
        pose='a', value=float(self.a_pose.lineEdit.text())
      )
    )
    self.b_pose.lineEdit.text_modified.connect(
      lambda: self._on_cart_pose_changed_using_line_edits(
        pose='b', value=float(self.b_pose.lineEdit.text())
      )
    )
    self.c_pose.lineEdit.text_modified.connect(
      lambda: self._on_cart_pose_changed_using_line_edits(
        pose='c', value=float(self.c_pose.lineEdit.text())
      )
    )

    # Sliders
    self.x_pose.sliderWidget.value_modified.connect(
      lambda: self._on_cart_pose_changed_using_sliders(
        pose='x', value=float(self.x_pose.sliderWidget.value())
      )
    )
    self.y_pose.sliderWidget.value_modified.connect(
      lambda: self._on_cart_pose_changed_using_sliders(
        pose='y', value=float(self.y_pose.sliderWidget.value())
      )
    )
    self.z_pose.sliderWidget.value_modified.connect(
      lambda: self._on_cart_pose_changed_using_sliders(
        pose='z', value=float(self.z_pose.sliderWidget.value())
      )
    )
    self.a_pose.sliderWidget.value_modified.connect(
      lambda: self._on_cart_pose_changed_using_sliders(
        pose='a', value=float(self.a_pose.sliderWidget.value())
      )
    )
    self.b_pose.sliderWidget.value_modified.connect(
      lambda: self._on_cart_pose_changed_using_sliders(
        pose='b', value=float(self.b_pose.sliderWidget.value())
      )
    )
    self.c_pose.sliderWidget.value_modified.connect(
      lambda: self._on_cart_pose_changed_using_sliders(
        pose='c', value=float(self.c_pose.sliderWidget.value())
      )
    )

  def _on_pose_limits_changed(self) -> None:
    """
    Method called when pose limits get updated to update the UI elements.
    """

    # Labels
    if hasattr(self.x_pose, 'lowLimLabel'): self.x_pose.lowLimLabel.setText(f"{self._x_limits[0]}°")
    if hasattr(self.x_pose, 'upLimLabel'): self.x_pose.upLimLabel.setText(f"{self._x_limits[1]}°")
    if hasattr(self.y_pose, 'lowLimLabel'): self.y_pose.lowLimLabel.setText(f"{self._y_limits[0]}°")
    if hasattr(self.y_pose, 'upLimLabel'): self.y_pose.upLimLabel.setText(f"{self._y_limits[1]}°")
    if hasattr(self.z_pose, 'lowLimLabel'): self.z_pose.lowLimLabel.setText(f"{self._z_limits[0]}°")
    if hasattr(self.z_pose, 'upLimLabel'): self.z_pose.upLimLabel.setText(f"{self._z_limits[1]}°")
    if hasattr(self.a_pose, 'lowLimLabel'): self.a_pose.lowLimLabel.setText(f"{self._a_limits[0]}°")
    if hasattr(self.a_pose, 'upLimLabel'): self.a_pose.upLimLabel.setText(f"{self._a_limits[1]}°")
    if hasattr(self.b_pose, 'lowLimLabel'): self.b_pose.lowLimLabel.setText(f"{self._b_limits[0]}°")
    if hasattr(self.b_pose, 'upLimLabel'): self.b_pose.upLimLabel.setText(f"{self._b_limits[1]}°")
    if hasattr(self.c_pose, 'lowLimLabel'): self.c_pose.lowLimLabel.setText(f"{self._c_limits[0]}°")
    if hasattr(self.c_pose, 'upLimLabel'): self.c_pose.upLimLabel.setText(f"{self._c_limits[1]}°")

    # LineEdits
    self.x_pose.lineEdit.min = self._x_limits[0]
    self.x_pose.lineEdit.max = self._x_limits[1]
    self.y_pose.lineEdit.min = self._y_limits[0]
    self.y_pose.lineEdit.max = self._y_limits[1]
    self.z_pose.lineEdit.min = self._z_limits[0]
    self.z_pose.lineEdit.max = self._z_limits[1]
    self.a_pose.lineEdit.min = self._a_limits[0]
    self.a_pose.lineEdit.max = self._a_limits[1]
    self.b_pose.lineEdit.min = self._b_limits[0]
    self.b_pose.lineEdit.max = self._b_limits[1]
    self.c_pose.lineEdit.min = self._c_limits[0]
    self.c_pose.lineEdit.max = self._c_limits[1]

    # Sliders
    self.x_pose.sliderWidget.min = self._x_limits[0]
    self.y_pose.sliderWidget.min = self._y_limits[0]
    self.y_pose.sliderWidget.max = self._y_limits[1]
    self.z_pose.sliderWidget.min = self._z_limits[0]
    self.z_pose.sliderWidget.max = self._z_limits[1]
    self.x_pose.sliderWidget.max = self._x_limits[1]
    self.a_pose.sliderWidget.min = self._a_limits[0]
    self.a_pose.sliderWidget.max = self._a_limits[1]
    self.b_pose.sliderWidget.min = self._b_limits[0]
    self.b_pose.sliderWidget.max = self._b_limits[1]
    self.c_pose.sliderWidget.min = self._c_limits[0]
    self.c_pose.sliderWidget.max = self._c_limits[1]

  def _update_cartesian_pose_locally(self, pose: str, value: float) -> None:
    """
    Method to update the cartesian pose based on local widgets.

    Arguments:
      pose: str
        pose identifier
      values: float
        pose value
    """

    if not pose:
      self._logger.warning("Not a valid pose identifier!!!")
      return

    if pose == 'x': self._x_pose = value
    elif pose == 'y': self._y_pose = value
    elif pose == 'z': self._z_pose = value
    elif pose == 'a': self._a_pose = value
    elif pose == 'b': self._b_pose = value
    elif pose == 'c': self._c_pose = value

    self.cart_jog_ctrl_update_pose.emit('',
      glm.array(
        glm.vec3(self._x_pose / 1000, self._y_pose / 1000, self._z_pose / 1000),
        glm.vec3(self._c_pose, self._b_pose, self._a_pose)
      )
    )

  def _update_line_edits_on_cartesian_pose_changed(self) -> None:
    """
    Method called when cartesian pose get updated to update the LineEdits.
    """

    # LineEdits
    self.x_pose.lineEdit.setText(f"{self._x_pose:.2f}")
    self.y_pose.lineEdit.setText(f"{self._y_pose:.2f}")
    self.z_pose.lineEdit.setText(f"{self._z_pose:.2f}")
    self.a_pose.lineEdit.setText(f"{self._a_pose:.2f}")
    self.b_pose.lineEdit.setText(f"{self._b_pose:.2f}")
    self.c_pose.lineEdit.setText(f"{self._c_pose:.2f}")

  def _update_sliders_on_cartesian_pose_changed(self) -> None:
    """
    Method called when cartesian pose get updated to update the Sliders.
    """

    # Sliders
    self.x_pose.sliderWidget.set_value(self._x_pose)
    self.y_pose.sliderWidget.set_value(self._y_pose)
    self.z_pose.sliderWidget.set_value(self._z_pose)
    self.a_pose.sliderWidget.set_value(self._a_pose)
    self.b_pose.sliderWidget.set_value(self._b_pose)
    self.c_pose.sliderWidget.set_value(self._c_pose)

  def _on_cart_pose_changed_using_line_edits(self, pose: str, value: float) -> None:
    """
    Slot/Method called when the cartesian pose changed using the LineEdits.

    Arguments:
      pose: str
        pose identifier
      values: float
        pose value
    """

    self._update_cartesian_pose_locally(pose=pose, value=value)

    self._update_sliders_on_cartesian_pose_changed()

  def _on_cart_pose_changed_using_sliders(self, pose: str, value: float) -> None:
    """
    Slot/Method called when the cartesian pose changed using the Sliders.

    Arguments:
      pose: str
        pose identifier
      values: float
        pose value
    """

    self._update_cartesian_pose_locally(pose=pose, value=value)

    self._update_line_edits_on_cartesian_pose_changed()

  def update_cartesian_pose_limits(self, **pose_limits: Dict) -> None:
    """
    Method to update the cartesian pose limits.

    Keyword Arguments:
      x_limits: List
        x pose limits (in mm)
      y_limits: List
        y pose limits (in mm)
      z_limits: List
        z pose limits (in mm)
      a_limits: List
        a pose limits (in mm)
      b_limits: List
        b pose limits (in mm)
      c_limits: List
        c pose limits (in mm)
    """

    self._x_limits = pose_limits.get('x_limits', [-2000, 2000])
    self._y_limits = pose_limits.get('y_limits', [-2000, 2000])
    self._z_limits = pose_limits.get('z_limits', [-2000, 2000])
    self._a_limits = pose_limits.get('a_limits', [-180, 180])
    self._b_limits = pose_limits.get('b_limits', [-180, 180])
    self._c_limits = pose_limits.get('c_limits', [-180, 180])

    # Apply limit values
    self._on_pose_limits_changed()

  def update_current_cartesian_pose(self, **pose) -> None:
    """
    Slot/Mathod to update the current value of the cartesian pose of the robot.

    Keyword Arguments:
      x_pose: float
        x pose value (in mm)
      y_pose: float
        y pose value (in mm)
      z_pose: float
        z pose value (in mm)
      a_pose: float
        a pose value (in mm)
      b_pose: float
        b pose value (in mm)
      c_pose: float
        c pose value (in mm)
    """

    self._x_pose = pose.get('x_pose', 0.0) * 1000 # in mm
    self._y_pose = pose.get('y_pose', 0.0) * 1000 # in mm
    self._z_pose = pose.get('z_pose', 0.0) * 1000 # in mm
    self._a_pose = pose.get('a_pose', 0.0) # in degrees
    self._b_pose = pose.get('b_pose', 0.0) # in degrees
    self._c_pose = pose.get('c_pose', 0.0) # in degrees

    self._update_line_edits_on_cartesian_pose_changed()
    self._update_sliders_on_cartesian_pose_changed()


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed Widget
  sim_robot_ctrl_widget = SimRobotCtrlWidget()
  # Show the widget
  sim_robot_ctrl_widget.show()
  # execute the program
  sys.exit(app.exec())