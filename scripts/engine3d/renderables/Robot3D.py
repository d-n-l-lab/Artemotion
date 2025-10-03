## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including Robot class to render a Manipulator arm in the 3D viewport.
##
##############################################################################################
##
import os
import sys
import glm

from typing import Dict, List

try:
  from scripts.settings.Logger import Logger
  from scripts.maths.Transforms import y_is_up
  from scripts.engine3d.renderables.Link import Link
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.maths.Transforms import y_is_up
  from scripts.engine3d.renderables.Link import Link


class DummyLogger(Logger):

  pass


class Robot3D:

  """
  Class to create a complete Robot 3D geometry for rendering.

  Arguments:
    robot_name: str (default = Staubli-RX160)
      name of the robot to be rendered

  Keyword Arguments:
    logger: Logger
      logger class
    robot_config: Dict
      robot configuration parameters
    sh_file: str
      name of the shader file
  """

  def __init__(self, robot_config: Dict, **kwargs) -> None:

    self.robot_config = robot_config
    self._logger = kwargs.get('logger', DummyLogger)
    self._sh_file = kwargs.get('sh_file', 'link')
    self._axes_transforms = kwargs.get('axes_transforms', [])

    # Create robot's links
    self._links = {}
    if self.robot_config:
      self._create_links()
      pass
    else:
      return None

  def _create_links(self) -> None:
    """
    Method to initialize and create the links of the robot.
    """

    self.base = Link(sh_file=self._sh_file,
                     robot=self.robot_config.Name,
                     config=self.robot_config.Links['base'],
                     logger=self._logger)
    self.link1 = Link(sh_file=self._sh_file,
                      robot=self.robot_config.Name,
                      config=self.robot_config.Links['link1'],
                      logger=self._logger)
    self.link2 = Link(sh_file=self._sh_file,
                      robot=self.robot_config.Name,
                      config=self.robot_config.Links['link2'],
                      logger=self._logger)
    self.link3 = Link(sh_file=self._sh_file,
                      robot=self.robot_config.Name,
                      config=self.robot_config.Links['link3'],
                      logger=self._logger)
    self.link4 = Link(sh_file=self._sh_file,
                      robot=self.robot_config.Name,
                      config=self.robot_config.Links['link4'],
                      logger=self._logger)
    self.link5 = Link(sh_file=self._sh_file,
                      robot=self.robot_config.Name,
                      config=self.robot_config.Links['link5'],
                      logger=self._logger)
    self.link6 = Link(sh_file=self._sh_file,
                      robot=self.robot_config.Name,
                      config=self.robot_config.Links['link6'],
                      logger=self._logger)
    self._links = {'base': self.base, 'link1': self.link1, 'link2': self.link2,
                   'link3': self.link3, 'link4': self.link4, 'link5': self.link5,
                   'link6': self.link6}

  def parse_links(self) -> None:
    """
    Method to create links of the robot as per the parsed robot configuration.
    """

    [link.parse_mesh_data() for link in self._links.values()]

  def init_gl(self) -> None:
    """
    Method to initialize the OpenGL to render.
    """

    [link.init_gl() for link in self._links.values()]

  @property
  def initialized(self) -> bool:
    """
    Property: initialized
    """

    return all(link.initialized for link in self._links.values())

  @property
  def axes_transforms(self) -> List:
    """
    Property: axes transforms
    """

    return self._axes_transforms

  @axes_transforms.setter
  def axes_transforms(self, mats: List) -> List:
    """
    Property: axes transforms

    Arguments:
      mats: List[glm.mat4]
        list of transformation matrices
    """

    self._axes_transforms = mats

  def render(self) -> None:
    """
    Method to render 3D.
    """

    [link.render() for link in self._links.values()]

  def set_model(self) -> None:
    """
    Method to set the model matrix.
    """

    try:
      assert len(self.axes_transforms) == len(self._links) - 1
    except AssertionError:
      self._logger.exception("Invalid axes transformations")
      return

    for idx, link in enumerate(self._links.values()):
      if idx > 0:
        link.model = y_is_up(logger=self._logger) @ self.axes_transforms[idx - 1]
      else:
        link.model = y_is_up(logger=self._logger)
      link.set_model()

  def set_view(self, view: glm.mat4) -> None:
    """
    Method to set the view matrix.

    Argument:
      model: glm.mat4
        view matrix
    """

    [link.set_view(view=view) for link in self._links.values()]

  def set_projection(self, projection: glm.mat4) -> None:
    """
    Method to set the projection matrix.

    Argument:
      model: glm.mat4
        projection matrix
    """

    [link.set_projection(projection=projection) for link in self._links.values()]

  def delete(self) -> None:
    """
    Method to delete vertex buffer objects.
    """

    [link.delete() for link in self._links.values()]


if __name__ == '__main__':
  """For development purpose only"""
  robot_3d = Robot3D(robot_name="Staubli-RX160")
  robot_3d.parse_links()
  # robot_3d._logger.remove_log_files()