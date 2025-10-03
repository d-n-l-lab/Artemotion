## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various classes to optimize various Kinematic & Dynamic
##              solutions of the robots.
##
##############################################################################################
##
import os
import sys
import glm

import numpy as np

from typing import List, Tuple

try:
  from scripts.settings.Logger import Logger
  from scripts.artebotics.Kinematics import Forward
  from scripts.artebotics.Kinematics import SphericalWristInverse
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from config import ConfigRobot
  from scripts.settings.Logger import Logger
  from scripts.artebotics.Kinematics import Forward
  from scripts.artebotics.Kinematics import SphericalWristInverse


class DummyLogger(Logger):

  pass


class OptimizedSolver:

  """
  This class manages the optimization of the forward & Inverse kinematics of the robot.

  Keyword Arguments:
    logger: Logger
      logger class
    robot_config: Dict
      robot name/model
  """

  def __init__(self, **kwargs) -> None:

    # logger
    self._logger = kwargs.get('logger', DummyLogger)

    # Robot config
    self._config = kwargs.get('robot_config', {})

    # Last valid target pose
    self._last_valid_tg_pose = glm.array(glm.vec3(), glm.vec3())

    # Forward Kinematics
    self.fk = Forward(logger=self._logger, robot_config=self._config)

    # Inverse Kinematics
    if self._config.Solver == 'Spherical':
      self.ik = SphericalWristInverse(logger=self._logger, robot_config=self._config)

  def _check_ik_solution_within_limits(self, angles: List) -> List | None:
    """
    Method to check the computed IK solutions against the rotation limits of the axes
    of the robot.

    Arguments:
      angles: List
        list of angles to be checked against limits

    Returns:
      sols_within_limits: List
        list containing the list of angles within the limits of the robot
    """

    angles_out_of_limits = [i for i in range(len(angles))]
    if not angles:
      return

    try:
      assert len(angles) == len(self.ik.axes_pos_limits)
    except AssertionError:
      self._logger.warning("Inconsistent angles data to check against the limits")
      return

    try:
      for idx, ang in enumerate(angles):
        if self.ik.axes_pos_limits[idx][0] <= ang <= self.ik.axes_pos_limits[idx][1]:
          angles_out_of_limits.remove(idx)
    except Exception:
      self._logger.exception("Unable to check the angles against limits because:")
    finally:
      return angles_out_of_limits

  def _compare_poses(self, solutions: List) -> List:
    """
    Method to check the computed IK solutions against the target pose of the robot.
    This method computes FK solution based on all the computed solutions and compare
    them against the required target pose and yield matching solution.

    Arguments:
      solutions: List
        list containing list of the computed angles of the axes of the robot

    Returns:
      angles: List
        list of angles that generates pose close to the target pose
    """

    angles = []
    if not solutions:
      return angles

    try:
      for sol in solutions:
        self.fk.compute_using_axes_offsts(axes_angles=sol)
        if np.allclose(
            self.ik.target_pose, self.fk.robot_pose.reinterpret_cast(glm.float32), atol=1e-6
          ):
          angles = sol
          break
    except Exception:
      self._logger.exception("Unable to compare target pose against computed pose because:")
    finally:
      return angles

  def _compare_angles(self, solutions: List, axes_angles: List) -> None:
    """
    Method to check the computed IK solutions against the current angles of the robot.
    This method finds the IK solution closest to the current angles of the axes of the
    robot.

    Arguments:
      solutions: List
        list containing list of the computed angles of the axes of the robot
      axes_angles: List
        list containing the angles of the robot's axes

    Returns:
      angles: List
        list of angles that generates pose close to the target pose
    """

    angles = axes_angles.copy()
    if not solutions:
      return angles

    try:
      for sol in solutions:
        if np.allclose(axes_angles, sol, atol=1e1):
          angles = sol
          break
    except Exception:
      self._logger.exception(
        "Unable to compare current axes angles against computed angles because:"
      )
    finally:
      return angles

  def compute_fk(self, axes_angles: List=[]) -> None:
    """
    Method to compute Forward Kinematic solution.

    Arguments:
      axes_angles: List
        list containing the angles of the robot's axes
    """

    self.fk.compute_using_axes_offsts(axes_angles=axes_angles)

  def compute_ik(self, tg_pose: List | glm.array, axes_angles: List) -> Tuple[glm.array | List]:
    """
    Method to compute Inverse Kinematic Solution.

    Arguments:
      tg_pose: List | glm.array
        list or array containing the target pose of the robot
      axes_angles: List
        list containing the current angles of the robot's axes

    Returns:
      angles: List
        list containing the computed angles of the robot axes
    """

    angles = axes_angles.copy()
    if len(tg_pose) == 0:
      return angles

    try:
      self.ik.target_pose = tg_pose
      self.ik.solve()
      angles_out_of_limits = self._check_ik_solution_within_limits(angles=self.ik.solutions[0])
      if not angles_out_of_limits:
        angles = self.ik.solutions[0]
        self._last_valid_tg_pose = tg_pose.reinterpret_cast(glm.vec3)
      else:
        for axis in angles_out_of_limits:
          self._logger.warning(f"Axis-{axis+1} angles out of the limits.")
    except Exception:
      self._logger.exception("Unable to compute IK solution because:")
    finally:
      return self._last_valid_tg_pose, angles, angles_out_of_limits


if __name__ == '__main__':
  """ For development purpose only"""
  robot_config = ConfigRobot(config_file='KR16-R2010-2.yaml')
  optim_solver = OptimizedSolver(robot_config=robot_config)
  optim_solver.compute_ik(tg_pose=[1.063, 0.07,  1.595, 0.00, 90.00, 0.00])