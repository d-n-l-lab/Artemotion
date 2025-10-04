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

import numpy as np

from OpenGL import GL as pygl
from typing import Tuple
from scipy.spatial import KDTree
from dataclasses import dataclass, field

try:
  from scripts.settings.Logger import Logger
  from scripts.engine3d.renderables.Renderable import Renderable
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.engine3d.renderables.Renderable import Renderable


class DummyLogger(Logger):

  pass


@dataclass
class RoomConstructor:

  """
  Class to construct the Room.

  Keyword Argument:
    logger: Logger
      logger class
    width: float
      width of the room
    depth: float
      depth of the room
    height: float
      height of the room
    w_spacing: float
      width spacing
    d_spacing: float
      depth spacing
    h_spacing: float
      height spacing
  """

  # logger
  logger: Logger

  # Dimensions
  width: float = 1000.0/100.0
  depth: float = 1500.0/100.0
  height: float = 500.0/100.0
  w_spacing: float = 50.0/100.0
  d_spacing: float = 50.0/100.0
  h_spacing: float = 50.0/100.0

  # arrays
  w_verts: np.ndarray = field(init=False)
  d_verts: np.ndarray = field(init=False)
  h_verts: np.ndarray = field(init=False)

  def __post_init__(self) -> None:
    pass

  def __str__(self) -> str:
    return f"Room with width: {self.width}, depth: {self.depth}, height: {self.height}"

  def _setup_dimensions(self, **kwargs) -> None:
    """
    Method to compute vertices & indices of the Room.

    Keyword Argument:
      width: float
        width of the room
      depth: float
        depth of the room
      height: float
        height of the room
      w_spacing: float
        width spacing
      d_spacing: float
        depth spacing
      h_spacing: float
        height spacing
    """

    # Room sizes (in centimeters)
    if 'width' in kwargs: self.width = kwargs['width']/100.0
    if 'depth' in kwargs: self.depth = kwargs['depth']/100.0
    if 'height' in kwargs: self.height = kwargs['height']/100.0

    # Spacings (in centimeters)
    if 'w_spacing' in kwargs: self.w_spacing = kwargs['w_spacing']/100.0
    if 'd_spacing' in kwargs: self.d_spacing = kwargs['d_spacing']/100.0
    if 'h_spacing' in kwargs: self.h_spacing = kwargs['h_spacing']/100.0

  def _create_vertices_arrays(self) -> Tuple[np.ndarray]:
    """
    Method to compute vertices arrays based room dimensions.

    Returns:
      indices: Tuple[np.ndarray]
        Tuple containing vertices arrays
    """

    # width array (over OpenGL X Axis)
    self.w_verts = np.arange(-self.width/2, (self.width + 0.01)/2, self.w_spacing, dtype=np.float32)
    # depth array (over OpenGL Z Axis)
    self.d_verts = np.arange(-self.depth/2, (self.depth + 0.01)/2, self.d_spacing, dtype=np.float32)
    # height array (over OpenGL Y Axis)
    self.h_verts = np.arange(0, (self.height + 0.01), self.h_spacing, dtype=np.float32)

    return (self.w_verts, np.flip(self.w_verts), self.h_verts, np.flip(self.h_verts),
            self.d_verts, np.flip(self.d_verts))

  def _create_vertices(self, w: np.ndarray, h: np.ndarray, d: np.ndarray) -> np.ndarray:
    """
    Method to compute vertices of the room as a meshgrid.

    Argument:
      w: np.ndarray
        width vertices
      d: np.ndarray
        depth vertices
      h: np.ndarray
        height vertices

    Returns:
      vertices: np.ndarray
        vertices array
    """

    # vertices
    vertices = np.array([], dtype=np.float32)
    try:
      vertices = np.vstack(np.meshgrid(w, h, d)).reshape(3, -1).T.flatten().astype(glm.float32)
    except Exception:
      self._logger.exception("Unable to create vertices because:")

    return vertices

  def _create_indices(self, vertices: np.ndarray, radius: float) -> np.ndarray:
    """
    Method to compute indices pairs of vertices of the room.

    Argument:
      vertices: np.ndarray
        vertices of room
      radius: float
        radius to compute pairs

    Returns:
      indices: np.ndarray
        indices pairs array
    """

    # indices
    indices = np.array([], dtype=np.int32)
    try:
      tree = KDTree(vertices.reshape((-1, 3)))
      pairs = tree.query_pairs(r=radius, output_type='ndarray')
      indices = pairs.flatten().astype(np.int32)
    except Exception:
      self._logger.exception("Unable to create indices because:")

    return indices

  def construct_room(self, **kwargs: float) -> Tuple[glm.array]:
    """
    Method to compute vertices & indices of the Room.

    Keyword Argument:
      width: float
        width of the room
      depth: float
        depth of the room
      height: float
        height of the room
      w_spacing: float
        width spacing
      d_spacing: float
        depth spacing
      h_spacing: float
        height spacing
    """

    # setup
    self._setup_dimensions(**kwargs)

    # Vertices
    vertices_arrays = self._create_vertices_arrays()

    floor = self._create_vertices(w=vertices_arrays[0], h=0.0, d=vertices_arrays[4])
    roof = self._create_vertices(w=vertices_arrays[1][1:], h=self.height, d=vertices_arrays[4])
    r_wall = self._create_vertices(w=self.width/2, h=vertices_arrays[2][1:],
                                   d=vertices_arrays[4])
    l_wall = self._create_vertices(w=-self.width/2, h=vertices_arrays[3][1:-1],
                                   d=vertices_arrays[4])
    f_wall = self._create_vertices(w=vertices_arrays[0][1:-1], h=vertices_arrays[2][1:-1],
                                   d=self.depth/2)
    b_wall = self._create_vertices(w=vertices_arrays[0][1:-1], h=vertices_arrays[2][1:-1],
                                   d=-self.depth/2)
    vertices = np.concatenate((floor, r_wall, roof, l_wall, f_wall, b_wall))

    # Indices
    indices = self._create_indices(vertices=vertices, radius=self.w_spacing)

    return glm.array(vertices), glm.array(indices)


class Room(Renderable, RoomConstructor):

  def __init__(self, sh_file: str, **kwargs) -> None:
    super(Room, self).__init__(sh_file, **kwargs)

    self._logger = kwargs['logger']
    # self.vertices, self.indices = self.construct_room()

  def init_gl(self) -> None:
    """
    Method to initialize the OpenGL to render.
    """

    super(Room, self).init_gl()

    try:
      # Position
      self.program.set_attribute(name='aPos')
      self.vbo.unbind()
    except Exception:
      self._logger.exception("Unable to assign room pose because:")
    else:
      # Setup the grid
      self.set_grid_ranges(x_verts=self.w_verts, y_verts=self.h_verts, z_verts=self.d_verts)
      self.set_grid_color()
      self.vao.unbind()
      self._initialized = True

  def render(self, primitive: pygl.GLenum=pygl.GL_LINES) -> None:
    """
    Method to render 3D. Re-implement this method in subclass.

    Argument:
      primitive: pygl.GLenum
        OpenGL drawing primitive
    """

    if primitive is None:
      primitive = pygl.GL_LINES
    super(Room, self).render(primitive)

  def set_grid_ranges(self, x_verts: np.ndarray, y_verts: np.ndarray, z_verts: np.ndarray) -> None:
    """
    Method to setup the grid ranges.

    Argument:
      x_verts: np.ndarray
        veritces at x axis
      y_verts: np.ndarray
        vertices at y axis
      z_verts: np.ndarray
        vertices at z axis
    """

    self.program.use()
    self.program.set_vec3(name='uX_Range', vec=glm.vec3(x_verts[0], x_verts.mean(), x_verts[-1]))
    self.program.set_vec3(name='uY_Range', vec=glm.vec3(y_verts[0], y_verts[0], y_verts[-1]))
    self.program.set_vec3(name='uZ_Range', vec=glm.vec3(z_verts[0], z_verts.mean(), z_verts[-1]))
    self.program.release()

  def set_grid_color(self, grid_color: glm.vec3=glm.vec3(0.8, 0.8, 0.8)) -> None:
    """
    Method to setup the grid color.

    Argument:
      grid_color: glm.vec3
        color of the grid color
    """

    self.program.use()
    self.program.set_vec3(name='uGridColor', vec=grid_color)
    self.program.release()


if __name__ == '__main__':
  """For development purpose only"""
  room = Room(sh_file='room', logger=DummyLogger)
  room._logger.remove_log_files()