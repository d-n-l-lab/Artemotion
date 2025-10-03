## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various classes to manage robot's End Effector/Tool.
##
##############################################################################################
##
import os
import sys
import glm

from dataclasses import dataclass, field

try:
  from scripts.settings.Logger import Logger
  from scripts.maths.Transforms import matrix_to_pose
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings.Logger import Logger
  from scripts.maths.Transforms import matrix_to_pose


class DummyLogger(Logger):

  pass


@dataclass
class EF:

  """
  Class to construct robot's end effector/tool.

  Keyword Arguments:
    transform: glm.mat4
      4x4 homogenous transform of ef pose & angle
    mass: int
      mass of the end effector
    cg: glm.vec3
      vector representing center of mass of the end effector
  """

  logger: Logger
  transform: glm.mat4 = field(default=glm.mat4())
  mass: int = 0 # in Kg
  cg: glm.vec3 = field(default=glm.vec3())

  @property
  def position(self) -> glm.array:
    """
    Get the postion XYZABC of the frame.
    """

    return matrix_to_pose(logger=self.logger, matrix=self.transform)

  @property
  def xyz(self) -> glm.vec3:
    """
    Get the vector representation of the frame position XYZ.
    """

    return self.position[0]

  @property
  def angles(self) -> glm.vec3:
    """
    Get the vector representation of the frame as Euler Angles.
    """

    return self.position[1]


if __name__ == '__main__':
  """For development purpose only"""
  DummyLogger.remove_log_files()
  end_effector = EF(logger=DummyLogger)
  end_effector.transform = glm.mat4(-0.815619, -0.324793, -0.478827, 0,
                                    0.0979244, 0.738148, -0.667494, 0,
                                    0.570242, -0.59131, -0.570242, 0,
                                    1528, -380, 1650, 1)
  print(f"Position: {end_effector.position}")
  print(f"EF XYZ: {end_effector.xyz}")
  print(f"EF Angles: {end_effector.angles}")