## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various functions to compute robot's jacobian matrices.
##
##############################################################################################
##
import os
import sys
import glm
import numpy as np

from typing import Any, List, Union

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings.Logger import Logger


class DummyLogger(Logger):

  pass


def compute_jacobian_tcp(logger: Logger, robot: Any, thetas: Union[List[float], np.ndarray], tool: Any) -> np.ndarray:
  """
  Function to compute Jacobian of the Robot's TCP or Flange coordinate system.

  Arguments:
    logger: Logger
      logger class
    robot: Any
      robot class
    thetas: Union[List[float], np.ndarray]
      current joint angles of the robot
    tool: Any
      tool class
  """

  jac_tcp = np.zeros((6, len(thetas)))
  if tool is None:
    tool_trans = glm.mat4() # 4x4 tranformation matrix
  else:
    tool_trans = tool.matrix()

  try:
    col = -1
    for theta in reversed(thetas):
      delta = glm.vec3(0,0,1) @ glm.mat3(tool_trans)
      d = glm.cross(glm.vec3(0,0,1), glm.vec3(tool_trans[3])) @ glm.mat3(tool_trans)
      jac_tcp[:, col] = np.hstack((d, delta))
      curr_trans = None # put the frame transformation here
      tool_trans = curr_trans @ tool_trans
      col -= 1
  except Exception:
    logger.exception("Unable to compute flange/tcp Jacobian because:")
  finally:
    return jac_tcp

def compute_jacobian_world(logger: Logger, robot: Any, thetas: Union[List[float], np.ndarray], tool: Any) -> np.ndarray:
  """
  Function to compute Jacobian of the Robot's in world coordinate system.

  Arguments:
    logger: Logger
      logger class
    robot: Any
      robot class
    thetas: Union[List[float], np.ndarray]
      current joint angles of the robot
    tool: Any
      tool class
  """

  jac_w = np.zeros((6, len(thetas)))
  try:
    j_tcp = compute_jacobian_tcp(logger=logger, robot=robot, thetas=thetas, tool=tool)
    pose = robot.fk(thetas=thetas)
    j_tr = np.zeros((6, len(thetas)))
    j_tr[:3, :3] = glm.mat3(pose)
    j_tr[3:, 3:] = glm.mat3(pose)
    jac_w = np.dot(j_tr, j_tcp)
  except Exception:
    logger.exception("Unable to compute world Jacobian because:")
  finally:
    return jac_w


if __name__ == '__main__':
  """ For development purpose only"""
  jacobian_tcp = compute_jacobian_tcp(
                  logger=DummyLogger, robot=None,
                  thetas=[11.362655, -57.260661, 40.404452, 32.218713, 61.237143, 15.947327],
                  tool=None
                )
  print(f"Jacobian tcp:\n{jacobian_tcp}")
  jacobian_world = compute_jacobian_world(
                    logger=DummyLogger, robot=None,
                    thetas=[11.362655, -57.260661, 40.404452, 32.218713, 61.237143, 15.947327],
                    tool=None
                  )
  print(f"Jacobian world:\n{jacobian_world}")
  DummyLogger.remove_log_files()