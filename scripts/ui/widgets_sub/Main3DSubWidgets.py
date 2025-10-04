## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
##
##############################################################################################
##
import os
import sys
import glm

from OpenGL import GL as pygl
from collections import deque
from typing import Any, List, Dict

from PySide6.QtGui import QCloseEvent, QKeyEvent, QEnterEvent, QWheelEvent, QMouseEvent
from PySide6.QtCore import QObject, QEvent, QPoint, QThread, Signal, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget

try:
  from scripts.settings.Logger import Logger
  from scripts.engine3d.renderables.Room import Room
  from scripts.engine3d.renderables.Curves import Curves
  from scripts.engine3d.renderables.Robot3D import Robot3D
  from scripts.engine3d.core.GLCamera import GLTargetCamera
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.engine3d.renderables.Room import Room
  from scripts.engine3d.renderables.Curves import Curves
  from scripts.engine3d.renderables.Robot3D import Robot3D
  from scripts.engine3d.core.GLCamera import GLTargetCamera


class Main3DSubUILogger(Logger):

  FILE_NAME = "ui_main_3d_sub"
  LOGGER_NAME = "UIMain3DSub"


class NavController:

  # Constants
  MOUSE_FILTER_WEIGHT = 0.75
  MOUSE_HISTORY_BUFF_SIZE = 10
  VIEWPORT_X = 0
  VIEWPORT_Y = 1
  VIEWPORT_W = 2
  VIEWPORT_H = 3

  def __init__(self, logger, **kwargs) -> None:
    super(NavController, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = logger

    # parameters
    self._fov = 60.0  # Wider field of view
    self._depth = 0.0
    self._viewport = glm.vec4(0)
    self.cam_pos = kwargs.get('cam_pos', glm.vec3(8, 6, 8))  # Further back
    self.cam_target = kwargs.get('cam_target', glm.vec3(0, 0, 0))

    # Mouse Filtering
    self.mouse_x = 0
    self.mouse_y = 0
    self.use_filtering = True
    self.mouse_history = deque(maxlen=self.MOUSE_HISTORY_BUFF_SIZE)

    # Views
    self.target_cam_rot_x = 0.0
    self.target_cam_rot_y = 0.0
    self.target_cam = GLTargetCamera(logger=self._logger)

  def setup_target_cam(self) -> None:
    # Camera View
    self.target_cam.update_cam_pos(self.cam_pos)
    self.target_cam.update_target_pos(self.cam_target)
    self.target_cam.update_view_space()

    #Projection
    self.target_cam.set_perspective_projection(
      fov=self._fov, width=self._viewport[self.VIEWPORT_W], height=self._viewport[self.VIEWPORT_H]
    )

  def filter_mouse_moves(self, dx: float, dy: float) -> None:
    average_x = 0.0
    average_y = 0.0
    average_total = 0.0
    current_weight = 1.0

    # Store current mouse deltas at the start
    self.mouse_history.appendleft(glm.vec2(dx, dy))
    for history in self.mouse_history:
      temp_vec2 = history
      average_x += temp_vec2.x * current_weight
      average_y += temp_vec2.y * current_weight
      average_total += 1.0 * current_weight
      current_weight *= self.MOUSE_FILTER_WEIGHT

    self.mouse_x = average_x/average_total
    self.mouse_y = average_y/average_total

  def update_perspective(self, proj: glm.mat4) -> None:
    pass

  def update_view(self, view: glm.mat4) -> None:
    pass

  def setup_viewport(self) -> None:
    self._viewport = glm.vec4(pygl.glGetIntegerv(pygl.GL_VIEWPORT))

  def setup_depth(self, cursor_pos: QPoint) -> Any:
    w = self._viewport[self.VIEWPORT_W]
    h = self._viewport[self.VIEWPORT_H]
    depth_buffer = pygl.glReadPixels(
      cursor_pos.x(), h-cursor_pos.y(), 1, 1, pygl.GL_DEPTH_COMPONENT, pygl.GL_FLOAT
    )
    depth = depth_buffer[0][0]

    if depth == 1:
      d_buffer = pygl.glReadPixels(0, 0, w, h, pygl.GL_DEPTH_COMPONENT, pygl.GL_FLOAT)
      d_vals = [float(d_buffer[i][j]) for i in range(w) for j in range(h) if d_buffer[i][j] != 1]
      if len(d_vals) > 0:
        depth = (min(d_vals) + max(d_vals)) / 2

    if depth == 1:
      pt_drag = glm.vec3(0)
      clip_pos = self.target_cam.perspective * self.target_cam.view * glm.vec4(pt_drag, 1)
      ndc_pos = glm.vec3(clip_pos) / clip_pos.w
      if ndc_pos.z > -1 and ndc_pos.z < 1:
        depth = ndc_pos.z * 0.5 + 0.5

    self._depth = depth

  def zoom_target_cam_mouse_drag(self, new_pos: QPoint, old_pos: QPoint) -> None:
    dist = (new_pos.y() - old_pos.y())/5.0
    self.target_cam.zoom(amount=dist)
    self.update_view(view=self.target_cam.view)

  def zoom_target_cam_mouse_wheel(self, yDelta: float) -> None:
    dist = yDelta // 120
    self.target_cam.zoom(amount=dist)
    self.update_view(view=self.target_cam.view)

  def zoom_trgt_cam_towards_cursor_mouse_wheel(self, pos: QPoint, yDelta: float) -> None:
    delta = yDelta // 120
    self.target_cam.zoom_towards_cursor(x=pos.x(), y=pos.y(), v=self._viewport, delta=delta)
    self.update_view(view=self.target_cam.view)

  def rotate_target_cam(self, new_pos: QPoint, old_pos: QPoint) -> None:
    self.target_cam_rot_x = (old_pos.x() - new_pos.x()) * 0.005
    self.target_cam_rot_y = (old_pos.y() - new_pos.y()) * 0.005
    if self.use_filtering:
      self.filter_mouse_moves(dx=self.target_cam_rot_x, dy=self.target_cam_rot_y)
    else:
      self.mouse_x = self.target_cam_rot_x
      self.mouse_y = self.target_cam_rot_y
    self.target_cam.rotate_around_origin(dx=self.mouse_x, dy=self.mouse_y)
    self.target_cam.rotate_around_target(target=glm.vec3(0), dx=self.mouse_x, dy=self.mouse_y)
    self.update_view(view=self.target_cam.view)

  def pan_target_cam(self, new_pos: QPoint, old_pos: QPoint) -> None:
    self._depth = 0.95 # TO-DO: Fix the issue with actual depth computation
    n_pos = glm.vec2(new_pos.x(), self._viewport[self.VIEWPORT_Y]-new_pos.y())
    o_pos = glm.vec2(old_pos.x(), self._viewport[self.VIEWPORT_Y]-old_pos.y())
    self.target_cam.pan(new_pos=n_pos, old_pos=o_pos, depth=self._depth)
    self.update_view(view=self.target_cam.view)


class Main3DGLWidgetWorker(QObject):

  """
  Worker class to manage the renderables and other long processing tasks.

  Signals:
    renderable_parsing_done: Signal(str)
      Signal emitted when the parsing of renderables done
    update_curves_data: Signal()
      Signal emitted when the curves data update is required
  """

  renderable_parsing_done = Signal(str)
  update_curves_data = Signal()

  def __init__(self) -> None:
    super(Main3DGLWidgetWorker, self).__init__()

    # Renderables
    self._renderables = ()
    self.room = None
    self.robot = None
    self.curves = None

  def parse_room(self, room: Room=None) -> None:
    """
    Method to parse the studio room's attributes.

    Arguments:
      room: Room
        instance of room class
    """

    if room is None:
      return

    room.vertices, room.indices = room.construct_room()
    self.renderable_parsing_done.emit("room")

  def parse_curves(self, curves: Curves=None, poses: glm.array=None) -> None:
    """
    Method to parse the bezier curve path.

    Arguments:
      curves: Curves
        instance of Curves class
      poses: glm.array | None
        array path data to render the curve
    """

    if curves is None:
      return

    if poses is None:
      return

    try:
      curves.vertices = poses
      if not curves.initialized:
        self.renderable_parsing_done.emit("curves")
      else:
        self.update_curves_data.emit()
    except Exception:
      Main3DSubUILogger.exception("Unable to create curves because:")

  def parse_robot(self, robot_name: str, robots: dict={}) -> None:
    """
    Method to parse/compute the robot's attributes in the 3D scene.

    Arguments:
      robot_name: str
        name of the robot
      robot: dict
        instances of Robot3D
    """

    if not robot_name:
      return

    if not robots:
      return

    robots[robot_name].parse_links()
    self.renderable_parsing_done.emit(robot_name)


class Main3DGLWidget(NavController, QOpenGLWidget):

  """
  Class to manage the Main 3D GL Widget.

  Constants:
    VIEW_PORT_H_MARGIN: int
      viewport height margin
    DEFAULT_WIDTH: int
      default widget width
    DEFAULT_HEIGHT: int
      default widget height

  Signals:
    parse_room = Signal(Room)
      Signal emitted to parse the room
    parse_robot: Signal(str, dict)
      signal emitted to parse the robot
    parse_curves: Signal(Curves, list)
      signal emitted to parse the curves
  """

  # Constants
  VIEW_PORT_H_MARGIN = 25
  DEFAULT_WIDTH = 1024
  DEFAULT_HEIGHT = 768

  # Signals
  # to widget worker
  parse_room = Signal(Room)
  parse_robot = Signal(str, dict)
  parse_curves = Signal(Curves, glm.array)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(Main3DGLWidget, self).__init__(logger=Main3DSubUILogger, **kwargs)

    if not self.objectName():
      self.setObjectName(u"main3DGLWidget")

    # self._parent = parent
    if self._parent is None:
      self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

    self._settings = kwargs.get('settings', None)

    # widget ambience
    self.red = 25
    self.green = 25
    self.blue = 35
    self.alpha = 1

    self.shift_pressed = False
    self.cursor_pos = QPoint()

    self.viewport_h = 0

    # Renderables
    self.room = None
    self.robots = {}
    self.curves = None
    self._renderables = ()

    # Widget worker thread
    self._create_main_3d_gl_widget_worker_thread()

    # Create Room
    self.create_room()

    # It helps to delete old/empty log files
    Main3DSubUILogger.remove_log_files()

  @staticmethod
  def _get_gl_info() -> str:
    """Get OpenGL Info"""
    return f"""
      Vendor: {pygl.glGetString(pygl.GL_VENDOR).decode()}
      Renderer: {pygl.glGetString(pygl.GL_RENDERER).decode()}
      OpenGL Version: {pygl.glGetString(pygl.GL_VERSION).decode()}
      Shader Version: {pygl.glGetString(pygl.GL_SHADING_LANGUAGE_VERSION).decode()}
      Max Vertex Attributes: {pygl.glGetIntegerv(pygl.GL_MAX_VERTEX_ATTRIBS)}
      Max Geometry Vertices: {pygl.glGetIntegerv(pygl.GL_MAX_GEOMETRY_OUTPUT_VERTICES)}
    """

  def _update_ambience(self, **kwargs: float) -> None:
    self.makeCurrent()
    pygl.glClear(pygl.GL_COLOR_BUFFER_BIT | pygl.GL_DEPTH_BUFFER_BIT)
    pygl.glClearColor(kwargs['red']/255, kwargs['green']/255, kwargs['blue']/255, kwargs['alpha'])
    self.update()

  def create_room(self) -> None:
    """
    Method to create room.
    """

    if self.room is not None:
      Main3DSubUILogger.warning("Room is already created!!!")
      return

    try:
      if self.room is None:
        self.room = Room(sh_file='room', logger=Main3DSubUILogger)
    except Exception:
      Main3DSubUILogger.exception("Unable to create room because:")
    else:
      self.parse_room.emit(self.room)

  def create_robot_3d(self, robot_config: Dict={}, axes_transforms: List=[]) -> None:
    """
    Method to create a 3D Robot.

    Arguments:
      robot_config: Dict
        robot configuration parameters
    """

    if not robot_config:
      return

    # if self.robots is not None:
    #   Main3DSubUILogger.warning("Only Single robot is allowed in the scene, for now!!!")
    #   return

    if robot_config.Name not in self.robots:
      try:
        self.robots[robot_config.Name] = Robot3D(
                                          logger=Main3DSubUILogger, robot_config=robot_config,
                                          sh_file='link', axes_transforms=axes_transforms
                                        )
      except Exception:
        Main3DSubUILogger.exception("Unable to create 3D robot because:")
      else:
        self.parse_robot.emit(robot_config.Name, self.robots)
    else:
      self.on_update_robot_model_req_recvd(robot_config.Name, axes_transforms=axes_transforms)

  def create_curves(self, poses: glm.array) -> None:
    """
    Slot/Method to create curves.

    Arguments:
      poses: gm.array
        array containing robot path data
    """

    if len(poses) == 0:
      return

    try:
      if self.curves is None:
        self.curves = Curves(sh_file='curves', logger=Main3DSubUILogger)
    except Exception:
      Main3DSubUILogger.exception("Unable to create Curves because:")
    else:
      self.parse_curves.emit(self.curves, poses)

  def initialize_renderables(self) -> None:
    """
    Slot/Method to initialize renderables.
    """

    self.makeCurrent()
    for rend in self._renderables:
      if rend is not None and not rend.initialized:
        rend.init_gl()
        rend.set_model()
        rend.set_view(view=self.target_cam.view)
        rend.set_projection(projection=self.target_cam.perspective)
    self.update()

  def _create_main_3d_gl_widget_worker_thread(self) -> None:
    """
    Method to create Main3DGLWidgetWorker & the respective thread.
    """

    # Create the Worker & Thread
    self.main_3d_gl_widget_worker_thread = QThread(self)
    self.main_3d_gl_widget_worker = Main3DGLWidgetWorker()
    self.main_3d_gl_widget_worker.moveToThread(self.main_3d_gl_widget_worker_thread)

    # Create connections
    self.parse_room.connect(self.main_3d_gl_widget_worker.parse_room)
    self.parse_robot.connect(self.main_3d_gl_widget_worker.parse_robot)
    self.parse_curves.connect(self.main_3d_gl_widget_worker.parse_curves)

    self.main_3d_gl_widget_worker.renderable_parsing_done.connect(self.on_renderables_parsing_done)
    self.main_3d_gl_widget_worker.update_curves_data.connect(self.on_update_curves_data_req_recvd)

    # Start the thread
    self.main_3d_gl_widget_worker_thread.start()

  def update_perspective(self, proj: glm.mat4) -> None:
    self.makeCurrent()
    [rend.set_projection(projection=proj) for rend in self._renderables if rend is not None]
    self.update()

  def update_view(self, view: glm.mat4) -> None:
    self.makeCurrent()
    [rend.set_view(view=view) for rend in self._renderables if rend is not None]
    self.update()

  def on_renderables_parsing_done(self, solid: str) -> None:
    """
    Slot/Method called after the setup of 3D objects done.

    Arguments:
      solid: str
        solid/object name
    """

    if solid == '':
      return
    elif solid == 'room':
      self._renderables += (self.room,)
    elif solid in self.robots:
      self._renderables += (self.robots[solid],)
    elif solid == 'curves':
      self._renderables += (self.curves,)
    self.initialize_renderables()

  def on_change_ambient_color_recvd(self, amb_color: List) -> None:
    if amb_color[0] != self.red:
      self.red = amb_color[0]/255
    if amb_color[1] != self.green:
      self.green = amb_color[1]/255
    if amb_color[2] != self.blue:
      self.blue = amb_color[2]/255
    if amb_color[3] != self.alpha:
      self.alpha = amb_color[3]
    self._update_ambience(red=self.red, green=self.green, blue=self.blue, alpha=self.alpha)

  def on_update_robot_model_req_recvd(self, robot_name: str, axes_transforms: List[glm.mat4]) -> bool:
    """
    Method to update the robot (renderable) model matrix when updated thetas of axes received.

    Arguments:
      robot_name: str
        name of the robot
      axes_transforms: List[glm.mat4]
        list containing updated tranformation matrices of the robot axes

    Returns:
      model_set: bool
        model set success flag
    """

    model_set = False
    if self.robots[robot_name] is not None and self.robots[robot_name].initialized:
      # Compute pose
      self.robots[robot_name].axes_transforms = axes_transforms

      # update 3D
      self.makeCurrent()
      self.robots[robot_name].set_model()
      self.update()
      model_set = True

    return model_set

  def on_update_curves_data_req_recvd(self) -> None:
    """
    Slot/method called to update the data of the curves.
    """

    if self.curves is not None and self.curves.initialized:
      self.makeCurrent()
      self.curves.update_data()
      self.update()

  def initializeGL(self) -> None:
    """Set up the rendering context, define and display"""
    if self._parent is None:
      Main3DSubUILogger.info(f"OpenGL information: {Main3DGLWidget._get_gl_info()}")
    self._update_ambience(red=self.red, green=self.green, blue=self.blue, alpha=self.alpha)
    pygl.glEnable(pygl.GL_DEPTH_TEST)
    self.context().aboutToBeDestroyed.connect(self.cleanup)

    # View Port
    self.setup_viewport()

    # Setup Cam
    self.setup_target_cam()

  def paintGL(self) -> None:
    pygl.glClear(pygl.GL_COLOR_BUFFER_BIT | pygl.GL_DEPTH_BUFFER_BIT)

    try:
      rendered_count = 0
      for rend in self._renderables:
        if rend is not None and rend.initialized:
          rend.render()
          rendered_count += 1
      # Debug: print render count occasionally
      if rendered_count > 0 and not hasattr(self, '_render_logged'):
        Main3DSubUILogger.info(f"Rendering {rendered_count} objects")
        self._render_logged = True
    except Exception:
      Main3DSubUILogger.exception("Unable to render because:")

  def resizeGL(self, w: int, h: int) -> None:
    if h >= self.VIEW_PORT_H_MARGIN:
      self.viewport_h = h - self.VIEW_PORT_H_MARGIN
    pygl.glViewport(0, 0, w, self.viewport_h)
    self.setup_viewport()

  def cleanup(self) -> None:
    self.makeCurrent()
    for rend in self._renderables:
      if rend is not None:
        del rend
        rend = None
    self.doneCurrent()

  def save_state(self) -> None:
    """
    Method to save the widget state before exiting.
    """

    try:
      if self.main_3d_gl_widget_worker_thread.isRunning():
        self.main_3d_gl_widget_worker_thread.quit()
        self.main_3d_gl_widget_worker_thread.wait()
    except Exception:
      Main3DSubUILogger.exception("Unable to close main 3D GL widget worker thread because:")

  def keyPressEvent(self, event: QKeyEvent) -> None:
    key = event.key()
    if key == Qt.Key_Shift:
      self.shift_pressed = True
    event.accept()
    return super(Main3DGLWidget, self).keyPressEvent(event)

  def keyReleaseEvent(self, event: QKeyEvent) -> None:
    key = event.key()
    if key == Qt.Key_Shift:
      self.shift_pressed = False
    Main3DSubUILogger.info(f"Alt Pressed: {self.shift_pressed}")
    return super(Main3DGLWidget, self).keyReleaseEvent(event)

  def enterEvent(self, event: QEnterEvent) -> None:
    self._update_ambience(red=self.red+5, green=self.green+5, blue=self.blue+5, alpha=self.alpha)
    return super(Main3DGLWidget, self).enterEvent(event)

  def leaveEvent(self, event: QEvent) -> None:
    self._update_ambience(red=self.red, green=self.green, blue=self.blue, alpha=self.alpha)
    return super(Main3DGLWidget, self).leaveEvent(event)

  def mousePressEvent(self, event: QMouseEvent) -> None:
    self.cursor_pos = event.globalPosition().toPoint()
    if event.buttons() == Qt.RightButton:
      self.setup_depth(cursor_pos=self.cursor_pos)
    return super(Main3DGLWidget, self).mousePressEvent(event)

  def mouseMoveEvent(self, event: QMouseEvent) -> None:
    if event.buttons() == Qt.LeftButton:
      self.zoom_target_cam_mouse_drag(new_pos=event.globalPosition().toPoint(),
        old_pos=self.cursor_pos)
    if event.buttons() == Qt.MiddleButton:
      self.rotate_target_cam(new_pos=event.globalPosition().toPoint(), old_pos=self.cursor_pos)
    if event.buttons() == Qt.RightButton:
      self.pan_target_cam(new_pos=event.globalPosition().toPoint(), old_pos=self.cursor_pos)
    self.cursor_pos = event.globalPosition().toPoint()
    return super(Main3DGLWidget, self).mouseMoveEvent(event)

  def wheelEvent(self, event: QWheelEvent) -> None:
    if self.shift_pressed:
      self.zoom_trgt_cam_towards_cursor_mouse_wheel(
        pos=event.globalPosition().toPoint(), yDelta=event.angleDelta().y()
      )
    else:
      self.zoom_target_cam_mouse_wheel(yDelta=event.angleDelta().y())
    return super(Main3DGLWidget, self).wheelEvent(event)

  def closeEvent(self, event: QCloseEvent) -> None:
    self.cleanup()
    self.save_state()
    return super(Main3DGLWidget, self).closeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
  app = QApplication(sys.argv)
  # Create an instance of 3D widget
  _main_3d = Main3DGLWidget()
  # Show the 3D widget
  _main_3d.show()
  # execute the program
  sys.exit(app.exec())