## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Migrated to PyVista
## Year: 2024
## Description: PyVista-based 3D visualization widget for robot rendering
##
##############################################################################################
##
import os
import sys
import numpy as np

from typing import Dict, List
from collections import deque

import pyvista as pv
from pyvistaqt import QtInteractor

from PySide6.QtCore import QObject, QThread, Signal, Qt, QPoint
from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtGui import QKeyEvent, QEnterEvent, QWheelEvent, QMouseEvent

try:
  from scripts.settings.Logger import Logger
except:
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger


class PyVistaLogger(Logger):
  FILE_NAME = "ui_pyvista_3d"
  LOGGER_NAME = "UIPyVista3D"


class PyVistaWorker(QObject):
  """
  Worker class to manage the renderables parsing in background thread.
  """

  renderable_ready = Signal(str)
  
  def __init__(self) -> None:
    super(PyVistaWorker, self).__init__()
    self.robots = {}
    self.room_data = None
    self.curves_data = None

  def parse_room(self, room_params: Dict) -> None:
    """Parse room parameters."""
    PyVistaLogger.info(f"Worker: Parsing room parameters")
    self.room_data = room_params
    self.renderable_ready.emit("room")

  def parse_robot(self, robot_name: str, robot_data: Dict) -> None:
    """Parse robot configuration."""
    PyVistaLogger.info(f"Worker: Parsing robot {robot_name}")
    self.robots[robot_name] = robot_data
    self.renderable_ready.emit(robot_name)

  def parse_curves(self, curve_points: np.ndarray) -> None:
    """Parse curve data."""
    PyVistaLogger.info(f"Worker: Parsing curves with {len(curve_points)} points")
    self.curves_data = curve_points
    self.renderable_ready.emit("curves")


class PyVistaWidget(QFrame):
  """
  PyVista-based 3D widget for robot visualization.
  
  This replaces the old OpenGL-based Main3DGLWidget with a modern,
  robust VTK/PyVista rendering system.
  
  Signals:
    parse_room: Signal(dict) - Request to parse room
    parse_robot: Signal(str, dict) - Request to parse robot
    parse_curves: Signal(np.ndarray) - Request to parse curves
  """

  # Signals
  parse_room = Signal(dict)
  parse_robot = Signal(str, dict)
  parse_curves = Signal(np.ndarray)

  # Constants
  DEFAULT_WIDTH = 1024
  DEFAULT_HEIGHT = 768

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(PyVistaWidget, self).__init__(parent=self._parent)

    if not self.objectName():
      self.setObjectName("pyVistaWidget")

    self._settings = kwargs.get('settings', None)
    
    # Widget properties
    if self._parent is None:
      self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

    # Ambient color
    self.bg_color = [0.098, 0.098, 0.137]  # Match old (25, 25, 35)/255
    
    # Keyboard state
    self.shift_pressed = False

    # Initialize PyVista plotter
    self._init_pyvista()

    # Renderables tracking
    self.robots = {}
    self.robot_actors = {}
    self.room_actor = None
    self.curves_actor = None

    # Worker thread for background processing
    self._create_worker_thread()

    # Create default room
    self.create_room()

    # Cleanup log files
    PyVistaLogger.remove_log_files()

  def _init_pyvista(self) -> None:
    """Initialize PyVista plotter."""
    # Create layout
    layout = QVBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Create PyVista plotter widget
    self.plotter = QtInteractor(self)
    self.plotter.set_background(self.bg_color)
    layout.addWidget(self.plotter.interactor)

    # Setup lighting
    self.plotter.add_light(pv.Light(position=(10, 10, 10), light_type='scene light'))
    self.plotter.add_light(pv.Light(position=(-10, 10, -10), light_type='scene light'))
    
    # Setup camera
    self.plotter.camera_position = [(8, 6, 8), (0, 0, 0), (0, 1, 0)]
    self.plotter.camera.zoom(1.0)

    # Enable anti-aliasing
    self.plotter.enable_anti_aliasing('ssaa')

    PyVistaLogger.info(f"PyVista initialized with VTK {pv.vtk_version_info}")

  def _create_worker_thread(self) -> None:
    """Create worker thread for background processing."""
    self.worker_thread = QThread(self)
    self.worker = PyVistaWorker()
    self.worker.moveToThread(self.worker_thread)

    # Connect signals
    self.parse_room.connect(self.worker.parse_room)
    self.parse_robot.connect(self.worker.parse_robot)
    self.parse_curves.connect(self.worker.parse_curves)
    self.worker.renderable_ready.connect(self.on_renderable_ready)

    # Start thread
    self.worker_thread.start()

  def create_room(self, **kwargs) -> None:
    """
    Create a room/grid in the 3D scene.
    
    Keyword Arguments:
      width: float - Width of the room (cm)
      depth: float - Depth of the room (cm)
      height: float - Height of the room (cm)
    """
    # Default room parameters
    room_params = {
      'width': kwargs.get('width', 1000.0) / 100.0,
      'depth': kwargs.get('depth', 1500.0) / 100.0,
      'height': kwargs.get('height', 500.0) / 100.0,
      'w_spacing': kwargs.get('w_spacing', 50.0) / 100.0,
      'd_spacing': kwargs.get('d_spacing', 50.0) / 100.0,
      'h_spacing': kwargs.get('h_spacing', 50.0) / 100.0,
    }
    
    self.parse_room.emit(room_params)

  def _render_room(self, room_params: Dict) -> None:
    """Render the room grid."""
    # Remove old room if exists
    if self.room_actor is not None:
      self.plotter.remove_actor(self.room_actor)

    # Create grid floor
    width = room_params['width']
    depth = room_params['depth']
    height = room_params['height']
    
    # Floor grid
    floor = pv.Plane(center=(0, 0, 0), direction=(0, 1, 0), 
                     i_size=width, j_size=depth, 
                     i_resolution=int(width/room_params['w_spacing']),
                     j_resolution=int(depth/room_params['d_spacing']))
    
    # Add coordinate axes
    axes = pv.Axes(show_actor=False, actor_scale=2.0)
    axes.origin = (0, 0, 0)
    
    # Add floor
    self.room_actor = self.plotter.add_mesh(
      floor, style='wireframe', color='lightgray', 
      line_width=1, opacity=0.3, name='room_floor'
    )
    
    # Add coordinate axes
    self.plotter.add_actor(axes.axes_actor)
    
    # Add bounding box
    bounds = [-width/2, width/2, 0, height, -depth/2, depth/2]
    outline = pv.Box(bounds=bounds).extract_all_edges()
    self.plotter.add_mesh(outline, color='gray', line_width=1, opacity=0.3)

    PyVistaLogger.info(f"Room rendered: {width}x{depth}x{height}")

  def create_robot_3d(self, robot_config, axes_transforms: List = None) -> None:
    """
    Create or update a 3D robot.
    
    Arguments:
      robot_config: Robot configuration object  
      axes_transforms: List of transformation matrices
    """
    PyVistaLogger.info(f"create_robot_3d called with robot_config type: {type(robot_config)}, axes_transforms: {axes_transforms is not None}")
    
    # Handle empty dict (happens when signal type conversion fails)
    if isinstance(robot_config, dict) and len(robot_config) == 0:
      PyVistaLogger.warning("create_robot_3d received empty dict - ignoring (robot not ready yet)")
      return
    
    if not robot_config or robot_config is None:
      PyVistaLogger.warning(f"create_robot_3d called with no robot_config (value: {robot_config})")
      return

    # Handle case where robot_config might be a dict
    if isinstance(robot_config, dict):
      PyVistaLogger.warning("robot_config is a dict, trying to extract config")
      if 'config' in robot_config:
        robot_config = robot_config['config']
      else:
        PyVistaLogger.error(f"robot_config dict doesn't have 'config' key, keys: {robot_config.keys()}")
        return

    try:
      robot_name = robot_config.Name
      PyVistaLogger.info(f"create_robot_3d for robot: {robot_name} with {len(axes_transforms) if axes_transforms else 0} transforms")
    except AttributeError as e:
      PyVistaLogger.exception(f"robot_config doesn't have Name attribute: {e}")
      return
    
    if robot_name not in self.robots:
      self.robots[robot_name] = {
        'config': robot_config,
        'transforms': axes_transforms or []
      }
      PyVistaLogger.info(f"Emitting parse_robot signal for {robot_name}")
      self.parse_robot.emit(robot_name, self.robots[robot_name])
    else:
      # Update existing robot
      PyVistaLogger.info(f"Updating existing robot {robot_name}")
      self.on_update_robot_model(robot_name, axes_transforms)

  def _render_robot(self, robot_name: str) -> None:
    """Render a robot from its configuration."""
    if robot_name not in self.robots:
      return

    robot_data = self.robots[robot_name]
    robot_config = robot_data['config']
    transforms = robot_data.get('transforms', [])

    # Remove old robot actors if they exist
    if robot_name in self.robot_actors:
      for actor in self.robot_actors[robot_name]:
        try:
          self.plotter.remove_actor(actor)
        except:
          pass

    # Create robot links
    actors = []
    
    # Color palette for robot links (RGB tuples)
    colors = [
      [1.0, 0.42, 0.42],  # Red
      [0.31, 0.80, 0.77], # Cyan
      [0.27, 0.72, 0.82], # Blue
      [1.0, 0.63, 0.48],  # Orange
      [0.60, 0.85, 0.78], # Teal
      [0.97, 0.86, 0.44], # Yellow
      [0.73, 0.56, 0.81]  # Purple
    ]
    
    links_dict = robot_config.Links
    for idx, (link_name, link_config) in enumerate(links_dict.items()):
      try:
        import numpy as np
        from scripts.settings.STLFilesManager import STL
        from scripts.settings import PathManager
        from scripts.settings.ProceduralGeometry import create_robot_link_geometry
        
        vertices = None
        indices = None
        
        # Try to load STL file first
        try:
          stl_file = STL(logger=PyVistaLogger,
                        file_name=os.path.join(robot_config.Name, link_config['mesh']))
          stl_file.parse_stl()
          # Convert glm arrays to numpy
          vertices = np.array(stl_file.stl_data.vertices).reshape(-1, 3)
          indices = np.array(stl_file.stl_data.indices, dtype=np.int32)
          PyVistaLogger.info(f"Loaded STL for {link_name}")
        except Exception as e:
          PyVistaLogger.warning(f"STL not found for {link_name}, using procedural geometry: {e}")
          # Fall back to procedural geometry
          try:
            v, i = create_robot_link_geometry(link_config)
            vertices = v  # Already numpy array
            indices = i   # Already numpy array
            PyVistaLogger.info(f"Created procedural geometry for {link_name}")
          except Exception as e2:
            PyVistaLogger.exception(f"Unable to create procedural geometry for {link_name}: {e2}")
            continue
        
        # Check if we have valid mesh data
        if vertices is None or indices is None:
          PyVistaLogger.warning(f"No mesh data for {link_name}, skipping")
          continue
          
        # Ensure vertices are in correct shape
        if vertices.ndim == 1:
          vertices = vertices.reshape(-1, 3)
          
        # Flatten indices if needed (procedural geometry returns Nx3 array)
        if indices.ndim == 2:
          indices = indices.flatten()
          
        if len(vertices) == 0 or len(indices) == 0:
          PyVistaLogger.warning(f"Empty mesh data for {link_name}, skipping")
          continue
        
        # Create PyVista mesh from vertices and indices
        # Indices need to be in format: [n_points, idx1, idx2, ..., n_points, idx1, idx2, ...]
        faces = []
        for i in range(0, len(indices), 3):
          if i + 2 < len(indices):
            faces.extend([3, int(indices[i]), int(indices[i+1]), int(indices[i+2])])
        
        if len(faces) == 0:
          PyVistaLogger.warning(f"No faces created for {link_name}")
          continue
          
        faces = np.array(faces, dtype=np.int32)
        mesh = pv.PolyData(vertices, faces)
        
        # Apply cumulative transform for kinematic chain
        # Each link's transform should be: base * link1 * link2 * ... * linkN
        if idx > 0 and len(transforms) >= idx:
          # Accumulate transforms from base to current link
          cumulative_transform = np.eye(4)
          for i in range(idx):
            if i < len(transforms):
              link_transform = np.array(transforms[i]).reshape(4, 4).T  # Transpose for VTK
              cumulative_transform = cumulative_transform @ link_transform
          mesh.transform(cumulative_transform)
        
        # Add mesh to scene with color
        color = colors[idx % len(colors)]
        actor = self.plotter.add_mesh(
          mesh, 
          color=color,
          opacity=0.9,
          smooth_shading=True,
          name=f'{robot_name}_{link_name}'
        )
        actors.append(actor)
        
        PyVistaLogger.info(f"Rendered link {link_name} with {len(vertices)} vertices")
        
      except Exception as e:
        PyVistaLogger.exception(f"Unable to create link {link_name}: {e}")

    self.robot_actors[robot_name] = actors
    PyVistaLogger.info(f"Robot {robot_name} rendered with {len(actors)} links")


  def create_curves(self, poses: np.ndarray) -> None:
    """
    Create curve visualization from poses.
    
    Arguments:
      poses: numpy array of 3D points
    """
    if len(poses) == 0:
      return
    
    self.parse_curves.emit(poses)

  def _render_curves(self, curve_points) -> None:
    """Render curves from points."""
    # Remove old curves
    if self.curves_actor is not None:
      self.plotter.remove_actor(self.curves_actor)

    try:
      # Convert glm.array to numpy if needed
      import numpy as np
      if hasattr(curve_points, '__iter__') and not isinstance(curve_points, np.ndarray):
        points = np.array(curve_points, dtype=np.float32)
      else:
        points = curve_points
        
      # Reshape points if needed
      if points.ndim == 1:
        points = points.reshape(-1, 3)
      else:
        points = points

      # Create spline
      spline = pv.Spline(points, n_points=len(points)*2)
      
      # Add curve to scene
      self.curves_actor = self.plotter.add_mesh(
        spline,
        color='yellow',
        line_width=3,
        name='robot_path'
      )
      
      # Add points
      point_cloud = pv.PolyData(points)
      self.plotter.add_mesh(
        point_cloud,
        color='red',
        point_size=8,
        render_points_as_spheres=True,
        name='path_points'
      )

      PyVistaLogger.info(f"Curves rendered with {len(points)} points")
    except Exception as e:
      PyVistaLogger.exception(f"Unable to render curves: {e}")

  def on_renderable_ready(self, renderable_name: str) -> None:
    """Called when a renderable is ready to display."""
    PyVistaLogger.info(f"on_renderable_ready called for: {renderable_name}")
    
    if renderable_name == "room":
      self._render_room(self.worker.room_data)
    elif renderable_name == "curves":
      self._render_curves(self.worker.curves_data)
    elif renderable_name in self.worker.robots:
      PyVistaLogger.info(f"Rendering robot {renderable_name}")
      self._render_robot(renderable_name)
    else:
      PyVistaLogger.warning(f"Unknown renderable: {renderable_name}")

  def on_update_robot_model_req_recvd(self, robot_name: str, axes_transforms: List) -> bool:
    """
    Update robot model with new transforms (compatibility method).
    
    Arguments:
      robot_name: Name of the robot
      axes_transforms: List of transformation matrices
      
    Returns:
      True if update successful
    """
    return self.on_update_robot_model(robot_name, axes_transforms)

  def on_update_robot_model(self, robot_name: str, axes_transforms: List) -> bool:
    """
    Update robot model with new transforms.
    
    Arguments:
      robot_name: Name of the robot
      axes_transforms: List of transformation matrices
      
    Returns:
      True if update successful
    """
    if robot_name not in self.robots:
      return False

    self.robots[robot_name]['transforms'] = axes_transforms
    self._render_robot(robot_name)
    return True

  def on_change_ambient_color_recvd(self, amb_color: List) -> None:
    """Change background color (compatibility method)."""
    self.bg_color = [amb_color[0]/255, amb_color[1]/255, amb_color[2]/255]
    self.plotter.set_background(self.bg_color)
  
  def on_change_ambient_color(self, amb_color: List) -> None:
    """Change background color."""
    self.on_change_ambient_color_recvd(amb_color)

  def save_state(self) -> None:
    """Save widget state before closing."""
    try:
      if self.worker_thread.isRunning():
        self.worker_thread.quit()
        self.worker_thread.wait()
    except Exception:
      PyVistaLogger.exception("Unable to stop worker thread")

  def cleanup(self) -> None:
    """Cleanup resources."""
    try:
      self.plotter.close()
    except Exception:
      PyVistaLogger.exception("Unable to close plotter")

  def keyPressEvent(self, event: QKeyEvent) -> None:
    """Handle key press events."""
    if event.key() == Qt.Key_Shift:
      self.shift_pressed = True
    return super(PyVistaWidget, self).keyPressEvent(event)

  def keyReleaseEvent(self, event: QKeyEvent) -> None:
    """Handle key release events."""
    if event.key() == Qt.Key_Shift:
      self.shift_pressed = False
    return super(PyVistaWidget, self).keyReleaseEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  from PySide6.QtWidgets import QApplication
  import sys
  
  app = QApplication(sys.argv)
  widget = PyVistaWidget()
  widget.show()
  sys.exit(app.exec())

