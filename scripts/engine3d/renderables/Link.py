## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to parse data from STL files & create meshes i.e.
##              links of the robot.
##
##############################################################################################
##
import os
import sys
import glm

from typing import List, Dict, Union
from OpenGL import GL as pygl
from dataclasses import dataclass, field

try:
  from scripts.settings.Logger import Logger
  from scripts.settings.STLFilesManager import STL
  from scripts.settings.ProceduralGeometry import create_robot_link_geometry
  from scripts.engine3d.renderables.Renderable import Renderable
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from config import ConfigRobot
  from scripts.settings.Logger import Logger
  from scripts.settings.STLFilesManager import STL
  from scripts.settings.ProceduralGeometry import create_robot_link_geometry
  from scripts.engine3d.renderables.Renderable import Renderable


class DummyLogger(Logger):

  pass


@dataclass
class LinkConstructor:

  """
  DataClass to construct the imported 3D link.

  Keyword Arguments:
    logger: Logger
      logger class
    robot: str
      name of the robot
    config: Dict
      link configuration
  """

  logger: Logger
  robot: str
  config: Dict = field(default_factory=dict)

  # Robot Link
  link: STL = field(default=None, init=False)

  def __post_init__(self) -> None:
    if len(self.config) == 0:
      self.logger.warning("No configuration data of the link to be parsed")
      return

    self.link = None
    file_type = os.path.splitext(self.config['mesh'])[1][1:].strip().lower()
    if file_type == 'stl':
      try:
        self.link = STL(logger=self.logger,
                        file_name=os.path.join(self.robot, self.config['mesh']))
      except (TypeError, FileNotFoundError) as err:
        self.logger.warning(f"STL file not found, using procedural geometry: {err}")


class Link(Renderable, LinkConstructor):

  """
  Class to render an imported 3D link.

  Keyword Arguments:
    sh_file: str
      name of the shader file
    logger: Logger
      logger class
  """

  def __init__(self, sh_file: str, **kwargs) -> None:
    super(Link, self).__init__(sh_file, **kwargs)

    self._logger = kwargs['logger']

  def parse_mesh_data(self) -> None:
    """
    Method to parse stl file or generate procedural geometry.
    """

    if self.link is not None:
      try:
        self.link.parse_stl()
        self.indices = glm.array(self.link.stl_data.indices)
        self.vertices = glm.array(self.link.stl_data.vertices)
        return
      except Exception:
        self._logger.warning("Unable to parse STL file, using procedural geometry")

    # Fallback to procedural geometry
    try:
      import numpy as np
      vertices, indices = create_robot_link_geometry(self.config)
      self.vertices = glm.array(vertices.flatten().tolist(), glm.float32)
      self.indices = glm.array(indices.flatten().tolist(), glm.uint32)
      self._logger.info(f"Created procedural geometry for {self.config.get('name', 'link')}")
    except Exception:
      self._logger.exception("Unable to create procedural geometry:")

  def init_gl(self) -> None:
    """
    Method to initialize the OpenGL to render.
    """

    super(Link, self).init_gl()

    try:
      # Position
      self.program.set_attribute(name='aMeshPos')
      self.vbo.unbind()
    except Exception:
      self._logger.exception("Unable to assign mesh pos because:")
    else:
      # Setup the link
      self.set_link_color(link_color=self.config['color'])
      self.vao.unbind()
      self._initialized = True

  def render(self, primitive: pygl.GLenum=pygl.GL_TRIANGLES) -> None:
    """
    Method to render 3D.

    Argument:
      primitive: pygl.GLenum
        OpenGL drawing primitive
    """

    if primitive is None:
      primitive = pygl.GL_TRIANGLES
    super(Link, self).render(primitive)

  def set_link_color(self, link_color: Union[glm.vec4, glm.array, List]) -> None:
    """
    Method to setup the color of the link.

    Argument:
      link_color: Union[glm.vec4, glm.array, List]
        color of the link
    """

    if isinstance(link_color, list):
      link_color = glm.vec4(link_color)

    self.program.use()
    self.program.set_vec4(name='uLinkColor', vec=link_color)
    self.program.release()


if __name__ == '__main__':
  """For development purpose only"""
  robot_name = "Staubli-RX160"
  robot_config = ConfigRobot(config_file=f"{robot_name}.yaml")
  link = Link(sh_file='link',
              robot=robot_name,
              config=robot_config.Robot['Links']['base'],
              logger=DummyLogger
            )
  link.parse_mesh_data()
  link._logger.remove_log_files()