## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Scripts including class to render curves in the 3D viewport.
##
##############################################################################################
##
import os
import sys
import glm

from typing import List, Dict

from OpenGL import GL as pygl
from dataclasses import dataclass, field

try:
  from scripts.settings.Logger import Logger
  from scripts.maths.Transforms import y_is_up
  from scripts.engine3d.renderables.Renderable import Renderable
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.maths.Transforms import y_is_up
  from scripts.engine3d.renderables.Renderable import Renderable


class DummyLogger(Logger):

  pass


@dataclass
class CurvesConstructor:

  """
  Class to construct the Bezier Curves.

  Keyword Arguments:
    logger: Logger
      logger class
    coords: glm.array
      array containing the coordinates
    num_samples: int
      number of samples of Bezier points to be generated. Default is 100.
  """

  logger: Logger


class Curves(Renderable, CurvesConstructor):

  def __init__(self, sh_file: str, **kwargs) -> None:
    super(Curves, self).__init__(sh_file, **kwargs)

    self._logger = kwargs['logger']

  def init_gl(self) -> None:
    """
    Method to initialize the OpenGL to render.
    """

    super(Curves, self).init_gl()

    try:
      # Position
      self.program.set_attribute(name='aCurvePos')
      self.vbo.unbind()
    except Exception:
      self._logger.exception("Unable to assign curves pos because:")
    else:
      self.vao.unbind()
      self._initialized = True

  def render(self, primitive: pygl.GLenum = pygl.GL_LINE_STRIP) -> None:
    """
    Method to render 3D.

    Argument:
      primitive: pygl.GLenum
        OpenGL drawing primitive
    """

    if primitive is None:
      primitive = pygl.GL_LINES
    return super(Curves, self).render(primitive)

  def set_model(self) -> None:
    """
    Method to set the model matrix.
    """

    self.model = y_is_up(logger=self._logger)
    super(Curves, self).set_model()


if __name__ == '__main__':
  """For development purpose only"""
  import random
  num_points = 4
  num_samples = 100
  points = glm.array(
    glm.vec3(random.uniform(-10, 10), random.uniform(0, 5), random.uniform(-15, 15))
  )
  for point in range(1, num_points):
    points = glm.array(points).concat(
      glm.array(glm.vec3(random.uniform(-10, 10), random.uniform(0, 5), random.uniform(-15, 15)))
    )
  curves = Curves(sh_file='curves', logger=DummyLogger,
                  coords={'index': 0, 'x_pose': 1234.56, 'y_pose': -4321.65, 'z_pose': 7890.12, 'roll': -69.25})
  curves.coords = {'index': 1, 'x_pose': 1234.56, 'y_pose': -4321.65, 'z_pose': 7890.12, 'roll': -69.25}
  curves.construct_curve(rationalize=True)
  print(f"{curves.coords=}")
  curves._logger.remove_log_files()