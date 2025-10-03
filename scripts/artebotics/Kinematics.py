## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various classes to compute robot's Kinematics.
##
##############################################################################################
##
import os
import sys
import glm

import numpy as np
import scipy.optimize

from typing import Dict, List, Tuple

try:
  from scripts.settings.Logger import Logger
  from scripts.maths.Transforms import (get_translation_matrix, get_rotation_matrix,
                                        matrix_to_pose, pose_to_matrix, bound_angles)
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from config import ConfigRobot
  from scripts.settings.Logger import Logger
  from scripts.maths.Transforms import (get_translation_matrix, get_rotation_matrix,
                                        matrix_to_pose, pose_to_matrix, bound_angles)


class DummyLogger(Logger):

  pass


class Kinematics:

  """
  This class manages the computation of basic kinematics of the robot required to further compute
  Forward & Inverse Kinematics equations.

  Keyword Arguments:
    logger: Logger
      logger class
    robot_config: Dict
      robot name/model
    axes_angles: List
      list containing angles of all the robot's axes
    tg_pose: List | glm.array
      list or array containing the target pose of the robot
  """

  def __init__(self, **kwargs) -> None:

    self._logger = kwargs.get('logger', DummyLogger)
    self._config = kwargs.get('robot_config', {})
    if not self._config:
      self._logger.exception("No robot configuraion, unable to compute transformation")
      return

    self.axes_angles = kwargs.get('axes_angles', self.home)
    self.target_pose = kwargs.get('tg_pose', glm.array.from_numbers(
                        glm.float32, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
                      ))

    # Axes transformations
    self.axes_transforms = []

    # Robot Pose - Flange Vector & Euler angles
    self.robot_pose = glm.array(glm.vec3(0.0), glm.vec3(0.0))

  def _update_axes_angs(self, axes_angles: List[float]=[]) -> bool:
    """
    Method to update the axes angles.

    Arguments:
      axes_angles: List[float]
        angles of the axes
    """

    if isinstance(axes_angles, np.ndarray):
      axes_angles = axes_angles.tolist()

    if not axes_angles:
      axes_angles = self.axes_angles
    else:
      self.axes_angles = axes_angles

  def compute_axis_transform_using_dh_params(self, dh_params: Dict, axis_ang: float) -> glm.mat4:
    """
    Method to compute tranformation matrix betweem two successive frames based on the
    DH parameters of the robot.

    https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters#Modified_DH_parameters

    Explanation:
      T{n-1 -> n} = Rot(x{n-1}, α{n-1}) @ Trans(a{n - 1}, 0, 0) @ Rot(z{n}, Θ{n}) @
                    Trans(0, 0, d{n})

    Arguments:
      dh_params: Dict
        DH parameters of a robot axis
      axis_ang: float
        current angle of the axis

    Returns:
      mat: glm.mat4
        4x4 individual transformation matrix
    """

    mat = glm.mat4(1)
    try:
      rx = get_rotation_matrix(logger=self._logger, deg=dh_params['alpha'], rx=1.0)
      tx = get_translation_matrix(logger=self._logger, tx=dh_params['a'])
      rz = get_rotation_matrix(logger=self._logger, deg=dh_params['theta']+axis_ang, rz=1.0)
      tz = get_translation_matrix(logger=self._logger, tz=dh_params['d'])
      mat = rx @ tx @ rz @ tz
    except Exception:
      self._logger.exception(
        f"Unable to compute transformation matrix for given angle: {axis_ang} because:"
      )
    finally:
      # transpose because glm matrix representation
      return mat

  def compute_kinematic_transform_using_dh_params(self, axes_angles: List=[]) -> glm.mat4:
    """
    Method to compute the tranformation of the robot's flange relative to the base frame.

    Arguments:
      axes_angles: List
        theta values of all the robot axes (axes > 6 if external axis/es is/are included)

    Returns:
      tr_mat_final: glm.mat4
        transformation matrix of Frame B (normally Robot's flange) relative to Frame A
        (normally Robot's base)
    """

    self._update_axes_angs(axes_angles=axes_angles)

    tr_mat = {}
    angles_copy = list(self.axes_angles)
    for i in range(len(angles_copy)):
      if self._config.Axes[f'a{i+1}']['home']['inverted']:
        angles_copy[i] = -1 * angles_copy[i]
      tr_mat[f'{i}_{i+1}'] = self.compute_axis_transform_using_dh_params(
                              dh_params=self._config.Axes[f'a{i+1}']['dh-params'],
                              axis_ang=angles_copy[i]
                             )

    # Frames 0 -> 6
    tr_mat_final = glm.mat4(1)
    for name, mat in tr_mat.items():
      # self._logger.info(f"tr_mat_{name} matrix:\n{mat}")
      tr_mat_final @= mat

    return tr_mat_final

  def _compute_axis_transform_using_offst(self, idx: int, ang: float) -> glm.mat4:
    """
    Method to compute the transformation of a given axis using the offsets defined in the robot's
    configuration file.

    Arguments:
      ang: float
        angle of rotation of the axis

    Returns:
      idx: int
        index of the axis
      mat: glm.mat4
        4x4 individual transformation matrix
    """

    mat = glm.mat4(1)
    axes_origs = self.axes_origins
    axis_of_rot = self.axis_of_rot
    try:
      mat = (get_translation_matrix(
              logger=self._logger, tx=axes_origs[idx]['x'], ty=axes_origs[idx]['y'],
              tz=axes_origs[idx]['z']
            ) @
            get_rotation_matrix(
              logger=self._logger, deg=ang, rx=axis_of_rot[idx].x, ry=axis_of_rot[idx].y,
              rz=axis_of_rot[idx].z
            ))
    except Exception:
      self._logger.exception("Unable to compute axis tranform because:")
    finally:
      return mat

  def compute_kinematic_transform_using_axes_offsts(self, axes_angles: List[float]) -> glm.mat4:
    """
    Method to compute the transformation of kinematic chain using the offsets defined in the
    robot's configuration file.

    Arguments:
      axes_angles: List[float]
        list of the angles of the axes of the robot
    """

    self._update_axes_angs(axes_angles=axes_angles)

    transformation = glm.mat4(1)
    self.axes_transforms = []
    try:
      for idx, tht in enumerate(self.axes_angles):
        transformation = transformation @ \
                         self._compute_axis_transform_using_offst(idx=idx, ang=tht)
        self.axes_transforms.append(transformation)
    except Exception:
      self._logger.exception("Unable to compute transformation because:")

  def compute_jacobian_world(self, axes_angles: List[float]) -> np.ndarray:
    """
    Method to compute the Jacobian Matrix in the world frame.

    https://automaticaddison.com/the-ultimate-guide-to-jacobian-matrices-for-robotics/

    Arguments:
      axes_angles: List[float]
        list of the angles of the axes of the robot

    Returns:
      jac_w: np.ndarray
        Jacobian Matrix in world frame
    """

    self.compute_kinematic_transform_using_axes_offsts(axes_angles=axes_angles)

    jac_w = np.zeros((6, len(self.axes_angles)))
    try:
      for i, _ in enumerate(self.axes_angles):
        z_i = glm.vec3(self.axes_transforms[i][2])
        p_i = glm.vec3(self.axes_transforms[i][3])
        jac_w[0:3, i] = glm.cross(z_i, (glm.vec3(self.axes_transforms[-1][3]) - p_i))
        jac_w[3:6, i] = z_i
    except Exception:
      self._logger.exception("Unable to compute Jacobian w.r.t world frame because:")
    finally:
      return jac_w

  def compute_jacobian_eef(self, axes_angles: List[float]) -> np.ndarray:
    """
    Method to compute the Jacobian Matrix in the end-effector frame.

    https://github.com/jhavl/dkt

    Arguments:
      axes_angles: List[float]
        list of the angles of the axes of the robot

    Returns:
      jac_e: np.ndarray
        Jacobian Matrix in end_effector frame
    """

    jac_e = np.zeros((6, len(axes_angles)))
    try:
      # Calculate Jacobian in World Frame
      jac_w = self.compute_jacobian_world(axes_angles=axes_angles)
      # Extract rotation matrix from final transformation & transpose
      r = glm.transpose(glm.mat3(self.axes_transforms[-1]))
      # velocity tranform matrix
      tr = np.zeros((6, len(axes_angles)))
      # Put rotation in the top left & bottom right of the matrix
      tr[:3, :3] = r
      tr[3:, 3:] = r
      # Matrix multiplication to compute Jacobian in End-Effector frame
      jac_e = tr @ jac_w
    except Exception:
      self._logger.exception("Unable to compute Jacobian in end-effector frame because:")
    finally:
      return jac_e

  @property
  def axes_origins(self) -> List:
    """
    Axes origins property.

    Returns:
      axes_origins: List
        list containing origin values of all the axes
    """

    return [axis['origin'] for axis in self._config.Axes.values()]

  @property
  def axes_pos_limits(self) -> None:
    """
    Axes position limits property.

    Returns:
      axes_pos_limits: List
        list containing position limits values of all the axes
    """

    return [[axis['limits']['min'], axis['limits']['max']] for axis in self._config.Axes.values()]

  @property
  def axis_of_rot(self) -> None:
    """
    Rotation axis property.

    Returns:
      axis_of_rot: List
        list containing axis of rotation of all the axes
    """

    return [glm.vec3(axis['axis']) for axis in self._config.Axes.values()]

  @property
  def axes_angles(self) -> List:
    """
    Axes angles property.

    Returns:
      axes_angles: List
        list containing angles of all the axes
    """

    return self._axes_angles

  @axes_angles.setter
  def axes_angles(self, angles: List) -> None:
    """
    Axes angles property setter.

    Arguments:
      angles: List
        list containing angles of all the axes
    """

    self._axes_angles = angles

  @property
  def pose(self) -> glm.array:
    """
    Robot current pose property.

    Arguments:
      pose: glm.array
        array containing current pose of the robot
    """

    return self._pose

  @pose.setter
  def pose(self, pose: glm.array | List) -> None:
    """
    Robot current pose property setter.

    Arguments:
      pose: glm.array | List
        array or list containing current pose (XYZABC) of the robot
    """

    if isinstance(pose, list):
      pose = glm.array.from_numbers(
              glm.float32, pose[0], pose[1], pose[2], pose[3], pose[4], pose[5]
            )
    if not isinstance(pose, glm.array):
      return

    self._pose = pose

  @property
  def target_pose(self) -> glm.array:
    """
    Robot target pose property.

    Arguments:
      pose: glm.array
        array containing target pose of the robot
    """

    return self._tg_pose

  @target_pose.setter
  def target_pose(self, pose: glm.array | List) -> None:
    """
    Robot target pose property setter.

    Arguments:
      pose: glm.array | List
        array or list containing target pose (XYZABC) of the robot
    """

    if isinstance(pose, list):
      pose = glm.array.from_numbers(
              glm.float32, pose[0], pose[1], pose[2], pose[3], pose[4], pose[5]
            )
    if not isinstance(pose, glm.array):
      return

    self._tg_pose = pose

  @property
  def target_pose_mat(self) -> glm.mat4:
    """
    Robot target pose matrix property.

    Arguments:
      pose_mat: glm.mat4
        target pose matrix of the robot
    """

    return pose_to_matrix(logger=self._logger, pose=self.target_pose, rot_order=self.rot_order)

  @property
  def home(self) -> None:
    """
    Axes angles at home property.

    Returns:
      home: List
        list containing angles of all the axes at robot's home
    """

    return [self._config.Axes['a1']['home']['angle'], self._config.Axes['a2']['home']['angle'],
            self._config.Axes['a3']['home']['angle'], self._config.Axes['a4']['home']['angle'],
            self._config.Axes['a5']['home']['angle'], self._config.Axes['a6']['home']['angle']]

  @property
  def rot_order(self) -> str:
    """
    Rotation Order property.

    Returns:
      rot_roder: str
        rotation order of the robot axes
    """

    rot_order = 'xyz'
    if self._config.Brand.lower() == 'kuka':
      rot_order  = 'zyx'

    return rot_order

  @property
  def robot_flange(self) -> glm.mat4:
    """
    Robot Flange property.

    Returns:
      robot_flange: glm.mat4
        robot flange matrix
    """

    robot_flange = glm.mat4(1)
    try:
      robot_flange = pose_to_matrix(
                      logger=self._logger,
                      pose=glm.array.from_numbers(
                        glm.float32,
                        self._config.Flange['origin']['x'],
                        self._config.Flange['origin']['y'],
                        self._config.Flange['origin']['z'],
                        self._config.Flange['origin']['a'],
                        self._config.Flange['origin']['b'],
                        self._config.Flange['origin']['c']
                      ),
                      rot_order=self.rot_order
                    )
    except Exception:
      self._logger.exception("Unable to parse robot flange because:")
    finally:
      return robot_flange

  @property
  def opw_params(self) -> Dict | None:
    """
    Ortho-parallel wrist parameters property.

    Returns:
      opw_params: Dict | None
        dictionary containing OPW parameters
    """

    try:
      return {
        'l1': self._config.OPW['l1'],
        'l2': self._config.OPW['l2'],
        'l3': self._config.OPW['l3'],
        'l4': self._config.OPW['l4'],
        'o1': self._config.OPW['o1'],
        'o2': self._config.OPW['o2'],
        'oy': self._config.OPW['oy'],
        'signs': self._config.OPW['signs'],
        'ofsts': self._config.OPW['ofsts']
      }
    except AttributeError:
      return None


class Forward(Kinematics):

  """
  This class (derived from Kinematics class) manages the computation of Forward/Direct Kinematics
  of an Industrial Robot.

  Keyword Arguments:
    logger: Logger
      logger class
    robot_config: Dict
      robot name/model
  """

  def __init__(self, **kwargs) -> None:
    super(Forward, self).__init__(**kwargs)

  def compute_using_dh_params(self, axes_angles: List[float]=[]) -> None:
    """
    Method to compute Direct/Forward Kinematics of a 6 DOF robot using DH parameters.

    Argument:
      axes_angles: List
        angle values of all the robot axes (axes > 6 if external axis/es is/are included)
    """

    transformation_matrix = self.compute_kinematic_transform_using_dh_params(
                              axes_angles=axes_angles
                            )
    self.robot_pose = matrix_to_pose(logger=self._logger,
                                     matrix=transformation_matrix,
                                     rot_order=self.rot_order
                      )

  def compute_using_axes_offsts(self, axes_angles: List[float]=[]) -> None:
    """
    Method to compute Direct/Forward Kinematics of a 6 DOF robot using axes offsets.

    Argument:
      axes_angles: List
        angle values of all the robot axes (axes > 6 if external axis/es is/are included)
    """

    self.compute_kinematic_transform_using_axes_offsts(axes_angles=axes_angles)
    self.robot_pose = matrix_to_pose(
                        logger=self._logger,
                        matrix=self.axes_transforms[-1] @ self.robot_flange, # TCP
                        rot_order=self.rot_order
                      )


class NumericalInverse(Kinematics):

  """
  This class (derived from Kinematics class) manages the computation of Inverse/Indirect Kinematics
  of an Industrial Robot.

  Keyword Arguments:
    logger: Logger
      logger class
    robot_config: Dict
      robot configuration
    solver_name: str
      name of the IK solver
    ilimit: int
      number of iterations allowed within a search before a new search is started
    slimit: int
      number of allowed searches before being unsuccessful
    tolerance: float
      maximum allowed residual error E
  """

  def __init__(self, **kwargs) -> None:
    super(NumericalInverse, self).__init__(**kwargs)

    # Solver parameters
    self._solver_name = kwargs.get('solver_name', 'IK Solver')
    self._ilimit = kwargs.get('ilimit', 30)
    self._slimit = kwargs.get('slimit', 100)
    self._tolerance = kwargs.get('tolerance', 1e-6)
    we = np.ones(6) * 0.15
    self._We = np.diag(we) # A 6 vector which assigns weights to Cartesian degrees-of-freedom

    # Solver results
    problems = 1000 # Total number of IK problems within the computation
    self._success = np.zeros(problems)
    self._searches = np.zeros(problems)
    self._iterations = np.zeros(problems)

    # initialize
    self._success[:] = np.nan
    self._searches[:] = np.nan
    self._iterations[:] = np.nan

  @staticmethod
  def pose_error(t: glm.mat4, td: glm.mat4) -> glm.array:
    """
    Method to compute error in the cartesian pose.

    Arguments:
      t: glm.mat4
        transformation matrix of current pose
      td: glm.mat4
        tranformation matrix of desired/target pose

    Returns:
      e: glm.array
        resultant error
    """

    e = glm.array(glm.vec3(0.0,0.0,0.0), glm.vec3(0.0,0.0,0.0))
    e[0] = glm.vec3(td[3] - t[3])
    R = glm.mat3(td) @ glm.transpose(glm.mat3(t))
    li = glm.vec3(R[1,2]-R[2,1], R[2,0]-R[0,2], R[0,1]-R[1,0])
    if np.linalg.norm(li) < 1e-6:
      # diagonal matrix
      if np.trace(R) > 0:
          a = np.zeros(3)
      else:
          a = np.pi / 2 * (np.diag(R) + 1)
    else:
      # non-diagnal matrix case
      ln = np.linalg.norm(li)
      a = glm.atan2(ln, np.trace(R) - 1) * li/ln
      # glm.silence(4)
    e[1] = glm.vec3(a)

    return e.reinterpret_cast(glm.float32)

  def _compute_error(self, t: glm.mat4, td: glm.mat4):
    """
    Method to compute angle axis error between current end-effector pose & the desired end-effector
    pose. It also calculates the quadratci error E that is weighted by the diagonal matrix We.

    Arguments:
      t: glm.mat4
        transformation matrix of current pose
      td: glm.mat4
        tranformation matrix of desired/target pose

    Returns:
      error: Tuple
        e: angle-axis error (glm.array)
        E: The quadratic error weighted by We
    """

    e = NumericalInverse.pose_error(t=t, td=td)
    E = 0.5 * e @ self._We @ e

    return e, E

  def step_nr(self, td: glm.mat4, q: List[float]) -> Tuple:
    """
    Method to implement the step of Newton-Raphson IK algorithm.

    Arguments:
      td: glm.mat4
        tranformation matrix of desired/target pose
      q: List[float]
        list of joint coordinates or axes angles

    Returns:
      res: Tuple
        E: float
          residual error
        q: np.ndarray
          The joint coordinates or axes angles of the solution
    """

    # current pose
    self.compute_kinematic_transform_using_axes_offsts(axes_angs=q)
    # error
    e, E = self._compute_error(t=self.axes_transforms[-1] @ self.robot_flange, td=td)
    # Jacobian
    J = self.compute_jacobian_world(axes_angs=q)

    q += np.linalg.pinv(J) @ e

    return E, q

  def step_gn(self, td: glm.mat4, q: List):
    """
    Method to implement the step of Gauss-Newton IK algorithm.

    Arguments:
      td: glm.mat4
        tranformation matrix of desired/target pose
      q: List[float]
        list of joint coordinates or axes angles

    Returns:
      res: Tuple
        E: float
          residual error
        q: np.ndarray
          The joint coordinates or axes angles of the solution
    """

    # current pose
    self.compute_kinematic_transform_using_axes_offsts(axes_angs=q)
    # error
    e, E = self._compute_error(t=self.axes_transforms[-1] @ self.robot_flange, td=td)
    # Jacobian
    J = self.compute_jacobian_world(axes_angs=q)
    g = J.T @ self._We @ e

    q += np.linalg.pinv(J.T @ self._We @ J) @ g

    return E, q

  def solve_ik(self, pd: glm.array, q0: List[float]) -> Tuple:
    """
    Method to solve the IK problem and obtain joint coordinates or axes angles that result in the
    desired pose.

    Arguments:
      pd: glm.array
        desired end-effector pose
      q0: List[float]
        list containing current joint coordinates or axes angles

    Returns:
      res: Tuple
        q: glm.array
          The joint coordinates or axes angles of the solution, not valid in case solution fails
        success: bool
          Flag if a solution is found
        iterations: int
          number of iterations taken to find the solution
        searches: int
          number of searches it took to find the solution
        residual: float
          the residual error of the solution
    """

    # get tranformation matrix of desired pose
    td = pose_to_matrix(
          logger=self._logger, pose=pd, rot_order=self.rot_order
        )

    # Iteration count
    i = 0
    total_i = 0
    for search in range(self._slimit):
        q = q0.copy()
        while i <= self._ilimit:
            i += 1

            if self._solver_name == 'nr':
                E, q = self.step_nr(td=td, q=q)
            elif self._solver_name == 'gn':
                E, q = self.step_gn(td=td, q=q)
            if E < self._tolerance:
                return q, True, total_i + i, search + 1, E
        total_i += i
        i = 0

    # Failed
    return q, False, total_i + i, search + 1, E

  def solve_ik_lsm(self, pose: glm.array, q: List[float]) -> List:
    """
    Method to solve Inverse Kinematics using Least Mean Square algorithm.

    Arguments:
      pose: glm.array
        desired end-effector pose
      q: List[float]
        list containing current joint coordinates or axes angles

    Returns:
      res.x: List
        list of computed angles
    """

    def obj_fn(x):
      self.compute_kinematic_transform_using_axes_offsts(axes_angles=q)
      init_mat = self.axes_transforms[-1] @ self.robot_flange
      self._logger.info(f"{init_mat=}")
      tg_mat = pose_to_matrix(logger=self._logger, pose=pose, rot_order=self.rot_order)
      self._logger.info(f"{tg_mat=}")
      obj = np.square(
              np.linalg.lstsq(tg_mat, init_mat, rcond=-1)[0] - np.identity(4)).sum()
      # print(f"obj: {obj}")
      return obj

    res = scipy.optimize.minimize(obj_fn, q, method='bfgs')
    self._logger.info(f"{res=}")
    return res.x


class SphericalWristInverse(Kinematics):

  """
  This class (derived from Kinematics class) manages the computation of Inverse/Indirect
  Kinematics of an Industrial Robot (Ortho-Parallel manipulator with Spherical Wrist) based
  on Analytical approach.

  Keyword Arguments:
    logger: Logger
      logger class
    robot_config: Dict
      robot configuration
  """

  ZERO_THRESHOLD = 1e-6

  def __init__(self, **kwargs) -> None:
    super(SphericalWristInverse, self).__init__(**kwargs)

    # Wrist center point
    self._wcp = glm.mat4()

    # geometric parameters
    self._geom_params = {}

    # orientation parameters
    self._orient_params = {}

    # solutions
    self._Θ1_sols = self._Θ2_sols = self._Θ3_sols = [None] * 4
    self._Θ4_sols = self._Θ5_sols = self._Θ6_sols = [None] * 8
    self.solutions = []

    # self._logger.info(f"{self.opw_params=}")

  def _compute_wcp(self) -> None:
    """
    Method to compute Wrist Center Point of a Spherical Robot Arm.
    """

    self._wcp = self.target_pose_mat
    self._wcp[3] = glm.vec4(
                    glm.vec3(self._wcp[3]) -
                    (self.opw_params['l4'] @ glm.mat3(self._wcp) @ glm.vec3(0, 0, 1)),
                    1
                   )
    # self._logger.info(f"WCP:\n{self._wcp}")

  def _compute_geometric_params(self) -> None:
    """
    Method to compute required geometric or positioning parameters to solve the first 3
    angles of the robot i.e. Θ₁, Θ₂ & Θ₃.
    """

    try:
      self._geom_params['nx1'] = glm.sqrt(
                                  glm.pow(self._wcp[3].x, 2) +
                                  glm.pow(self._wcp[3].y, 2) -
                                  glm.pow(self.opw_params['oy'], 2)
                                ) - self.opw_params['o1']
      self._geom_params['s1_sq'] = (glm.pow(self._geom_params['nx1'], 2) +
                                    glm.pow((self._wcp[3].z - self.opw_params['l1']), 2))
      self._geom_params['s2_sq'] = (glm.pow((self._geom_params['nx1'] +
                                             (2 * self.opw_params['o1'])), 2) +
                                    glm.pow((self._wcp[3].z - self.opw_params['l1']), 2))
      self._geom_params['k_sq'] = (glm.pow(self.opw_params['o2'], 2) +
                                   glm.pow(self.opw_params['l3'], 2))
      self._geom_params['s1'] = glm.sqrt(self._geom_params['s1_sq'])
      self._geom_params['s2'] = glm.sqrt(self._geom_params['s2_sq'])
      self._geom_params['k'] = glm.sqrt(self._geom_params['k_sq'])

      # self._logger.info(f"\n{self._geom_params=}")
    except Exception:
      self._logger.exception("Unable to compute geometric parameters because:")

  def _compute_Θ1(self) -> None:
    """
    Method to compute angle of axis 1.

    Θ₁ has two possible solutions.
    """

    self._Θ1_sols = [None] * 4
    try:
      # solution 1 (shoulder front)
      self._Θ1_sols[0] = (glm.atan2(self._wcp[3].y, self._wcp[3].x) -
                          glm.atan2(self.opw_params['oy'],
                                    self._geom_params['nx1'] + self.opw_params['o1'])
                         )
      self._Θ1_sols[1] = self._Θ1_sols[0]
      # solution 2 (shoulder back)
      self._Θ1_sols[2] = (glm.atan2(self._wcp[3].y, self._wcp[3].x) +
                          glm.atan2(self.opw_params['oy'],
                                    self._geom_params['nx1'] + self.opw_params['o1']) -
                          glm.pi()
                         )
      self._Θ1_sols[3] = self._Θ1_sols[2]
    except Exception:
      self._logger.exception("Unable to compute Θ₁ solutions because:")

  def _compute_Θ2(self) -> None:
    """
    Method to compute angle of axis 2.

    Θ₂ has four possible solutions.
    """

    self._Θ2_sols = [None] * 4
    try:
      n1 = ((self._geom_params['s1_sq'] + glm.pow(self.opw_params['l2'], 2) -
             self._geom_params['k_sq']) / (2 * self._geom_params['s1'] * self.opw_params['l2']))
      # if n1 > 1: n1 = 1 # Θ₂ is undefined
      # solution 1 (shoulder front & elbow up)
      self._Θ2_sols[0] = (-glm.acos(n1) +
                          glm.atan2(self._geom_params['nx1'],
                                    (self._wcp[3].z - self.opw_params['l1']))
                         )
      # solution 2 ((shoulder front & elbow down)
      self._Θ2_sols[1] = (glm.acos(n1) +
                          glm.atan2(self._geom_params['nx1'],
                                    (self._wcp[3].z - self.opw_params['l1']))
                         )
      n2 = ((self._geom_params['s2_sq'] + glm.pow(self.opw_params['l2'], 2) -
             self._geom_params['k_sq']) / (2 * self._geom_params['s2'] * self.opw_params['l2']))
      # if n2 > 1: n2 = 1 # Θ₂ is undefined
      # solution 3 (shoulder back & elbow up)
      self._Θ2_sols[2] = (-glm.acos(n2) -
                          glm.atan2(self._geom_params['nx1'] + 2 * self.opw_params['o1'],
                                    (self._wcp[3].z - self.opw_params['l1'])))
      # solution 2 ((shoulder back & elbow down)
      self._Θ2_sols[3] = (glm.acos(n2) -
                          glm.atan2(self._geom_params['nx1'] + 2 * self.opw_params['o1'],
                                    (self._wcp[3].z - self.opw_params['l1'])))
      # self._logger.info(f"{np.round(self._Θ2_sols, 4)=}")
    except Exception:
      self._logger.exception("Unable to compute Θ₂ solutions because:")

  def _compute_Θ3(self) -> None:
    """
    Method to compute angle of axis 3.

    Θ₃ has four possible solutions.
    """

    self._Θ3_sols = [None] * 4
    try:
      n1 = ((self._geom_params['s1_sq'] - glm.pow(self.opw_params['l2'], 2) -
             self._geom_params['k_sq']) / (2  * self._geom_params['k'] * self.opw_params['l2']))
      # if n1 > 1: n1 = 1 # Θ₃ is undefined
      # solution 1 (shoulder front & elbow up)
      self._Θ3_sols[0] = (glm.acos(n1) -
                          glm.atan2(self.opw_params['o2'], self.opw_params['l3']))
      # solution 2 ((shoulder front & elbow down)
      self._Θ3_sols[1] = (-glm.acos(n1) -
                          glm.atan2(self.opw_params['o2'], self.opw_params['l3']))
      n2 = ((self._geom_params['s2_sq'] - glm.pow(self.opw_params['l2'], 2) -
             self._geom_params['k_sq']) / (2 * self._geom_params['k'] * self.opw_params['l2']))
      # if n2 > 1: n2 = 1 # Θ₃ is undefined
      # solution 3 (shoulder back & elbow up)
      self._Θ3_sols[2] = (glm.acos(n2) -
                          glm.atan2(self.opw_params['o2'], self.opw_params['l3']))
      # solution 2 ((shoulder back & elbow down)
      self._Θ3_sols[3] = (-glm.acos(n2) -
                          glm.atan2(self.opw_params['o2'], self.opw_params['l3']))
      # self._logger.info(f"{np.round(self._Θ3_sols, 4)=}")
    except Exception:
      self._logger.exception("Unable to compute Θ₃ solutions because:")

  def _compute_orientation_params(self) -> None:
    """
    Method to compute parameters required to compute the orientation part of the problem i.e.
    the parameters to compute Θ₄, Θ₅ & Θ₆.
    """

    try:
      # sin(Θ₁)
      self._orient_params['sin_Θ1'] = [glm.sin(tht) for tht in self._Θ1_sols]
      # cos(Θ₁)
      self._orient_params['cos_Θ1'] = [glm.cos(tht) for tht in self._Θ1_sols]
      # sin(Θ₂ + Θ₃)
      self._orient_params['sin_Θ2_Θ3'] = [glm.sin(tht2 + tht3) for tht2, tht3
                                          in zip(self._Θ2_sols, self._Θ3_sols)]
      # cos(Θ₂ + Θ₃)
      self._orient_params['cos_Θ2_Θ3'] = [glm.cos(tht2 + tht3) for tht2, tht3
                                          in zip(self._Θ2_sols, self._Θ3_sols)]

      # target pose matrix
      mat = self._wcp
      # m
      self._orient_params['m'] = []
      for i in range(4):
        m = (mat[2,0] * self._orient_params['sin_Θ2_Θ3'][i] * self._orient_params['cos_Θ1'][i]) + \
            (mat[2,1] * self._orient_params['sin_Θ2_Θ3'][i] * self._orient_params['sin_Θ1'][i]) + \
            (mat[2,2] * self._orient_params['cos_Θ2_Θ3'][i])
        self._orient_params['m'].append(m)

      # self._logger.info(f"{self._orient_params}")
    except Exception:
      self._logger.exception("Unable to compute orientation parameters because:")

  def _compute_Θ4(self) -> None:
    """
    Method to compute angle of axis 4.

    Θ₄ has eight possible solutions.
    """

    try:
      mat = self._wcp
      self._Θ4_sols = [None] * 8
      for i in range(4):
        if abs(self._Θ5_sols[i]) < self.ZERO_THRESHOLD:
          sol = 0.0
        else:
          y = ((mat[2,1] * self._orient_params['cos_Θ1'][i]) -
               (mat[2,0] * self._orient_params['sin_Θ1'][i]))
          x = ((mat[2,0] * self._orient_params['cos_Θ2_Θ3'][i] *
                self._orient_params['cos_Θ1'][i]) +
               (mat[2,1] * self._orient_params['cos_Θ2_Θ3'][i] *
                self._orient_params['sin_Θ1'][i]) -
               (mat[2,2] * self._orient_params['sin_Θ2_Θ3'][i]))
          sol = glm.atan2(y, x)
        self._Θ4_sols[i] = sol
        self._Θ4_sols[i + 4] = sol + glm.pi()
      # self._logger.info(f"{np.round(self._Θ4_sols, 4)=}")
    except Exception:
      self._logger.exception("Unable to compute Θ₄ solutions because:")

  def _compute_Θ5(self) -> None:
    """
    Method to compute angle of axis 5.

    Θ₅ has eight possible solutions.
    """

    try:
      self._Θ5_sols = [None] * 8
      for idx, m in enumerate(self._orient_params['m']):
        sol = glm.atan2(glm.sqrt(1 - glm.pow(m, 2)), m)
        self._Θ5_sols[idx] = sol
        self._Θ5_sols[idx + 4] = -sol
      # self._logger.info(f"{np.round(self._Θ5_sols, 4)=}")
    except Exception:
      self._logger.exception("Unable to compute Θ₅ solutions because:")

  def _compute_Θ6(self) -> None:
    """
    Method to compute angle of axis 6.

    Θ₆ has eight possible solutions.
    """

    try:
      mat = self._wcp
      self._Θ6_sols = [None] * 8
      for i in range(4):
        if abs(self._Θ5_sols[i]) < self.ZERO_THRESHOLD:
          xe = glm.vec3(mat[0,0], mat[0,1], mat[0,2])
          rc = glm.mat3()
          rc[1] = glm.vec3(-glm.sin(self._Θ1_sols[i], glm.cos(self._Θ1_sols[i], 0)))
          rc[2] = mat[2]
          rc[0] = glm.cross(rc[1], rc[2])
          xec = glm.transpose(rc) @ xe
          sol = glm.atan2(xec.y, xec.x)
        else:
          y = ((mat[1,0] * self._orient_params['sin_Θ2_Θ3'][i] *
                self._orient_params['cos_Θ1'][i]) +
               (mat[1,1] * self._orient_params['sin_Θ2_Θ3'][i] *
                self._orient_params['sin_Θ1'][i]) +
               (mat[1,2] * self._orient_params['cos_Θ2_Θ3'][i]))
          x = ((-mat[0,0] * self._orient_params['sin_Θ2_Θ3'][i] *
                self._orient_params['cos_Θ1'][i]) -
               (mat[0,1] * self._orient_params['sin_Θ2_Θ3'][i] *
                self._orient_params['sin_Θ1'][i]) -
               (mat[0,2] * self._orient_params['cos_Θ2_Θ3'][i]))
          sol = glm.atan2(y, x)
        self._Θ6_sols[i] = sol
        self._Θ6_sols[i + 4] = sol - glm.pi()
      # self._logger.info(f"{np.round(self._Θ6_sols, 4)=}")
    except Exception:
      self._logger.exception("Unable to compute Θ₆ solutions because:")

  def _tabulate_solutions(self) -> None:
    """
    Mrthod to combine all the eight possible solutions.

                                        Solutions
    Joints     1        2         3         4         5         6         7         8
      Θ₁     Θ₁[i]    Θ₁[i]     Θ₁[ii]    Θ₁[ii]    Θ₁[i]     Θ₁[i]     Θ₁[ii]    Θ₁[ii]
      Θ₂     Θ₂[i]    Θ₂[ii]    Θ₂[iii]   Θ₂[iv]    Θ₂[i]     Θ₂[ii]    Θ₂[iii]   Θ₂[iv]
      Θ₃     Θ₃[i]    Θ₃[ii]    Θ₃[iii]   Θ₃[iv]    Θ₃[i]     Θ₃[ii]    Θ₃[iii]   Θ₃[iv]
      Θ₄     Θ₄[i]    Θ₄[ii]    Θ₄[iii]   Θ₄[iv]    Θ₄[v]     Θ₄[vi]    Θ₄[vii]   Θ₄[viii]
      Θ₅     Θ₅[i]    Θ₅[ii]    Θ₅[iii]   Θ₅[iv]    Θ₅[v]     Θ₅[vi]    Θ₅[vii]   Θ₅[viii]
      Θ₆     Θ₆[i]    Θ₆[ii]    Θ₆[iii]   Θ₆[iv]    Θ₆[v]     Θ₆[vi]    Θ₆[vii]   Θ₆[viii]
    """

    if (not self._Θ1_sols and not self._Θ2_sols and not self._Θ3_sols and not self._Θ4_sols and
        not self._Θ5_sols and not self._Θ6_sols):
       return

    _solutions = [[]] * 8
    self.solutions = []
    try:
      _solutions[0] = bound_angles(
                        logger=self._logger,
                        angles=[self._Θ1_sols[0], self._Θ2_sols[0], self._Θ3_sols[0],
                                self._Θ4_sols[0], self._Θ5_sols[0], self._Θ6_sols[0]]
                      )
      _solutions[1] = bound_angles(
                        logger=self._logger,
                        angles=[self._Θ1_sols[0], self._Θ2_sols[1], self._Θ3_sols[1],
                                self._Θ4_sols[1], self._Θ5_sols[1], self._Θ6_sols[1]]
                      )
      _solutions[2] = bound_angles(
                        logger=self._logger,
                        angles=[self._Θ1_sols[2], self._Θ2_sols[2], self._Θ3_sols[2],
                                self._Θ4_sols[2], self._Θ5_sols[2], self._Θ6_sols[2]]
                      )
      _solutions[3] = bound_angles(
                        logger=self._logger,
                        angles=[self._Θ1_sols[0], self._Θ2_sols[0], self._Θ3_sols[0],
                                self._Θ4_sols[0], self._Θ5_sols[0], self._Θ6_sols[0]]
                      )
      _solutions[4] = bound_angles(
                        logger=self._logger,
                        angles=[self._Θ1_sols[0], self._Θ2_sols[0], self._Θ3_sols[0],
                                self._Θ4_sols[4], self._Θ5_sols[4], self._Θ6_sols[4]]
                      )
      _solutions[5] = bound_angles(
                        logger=self._logger,
                        angles=[self._Θ1_sols[0], self._Θ2_sols[1], self._Θ3_sols[1],
                                self._Θ4_sols[5], self._Θ5_sols[5], self._Θ6_sols[5]]
                      )
      _solutions[6] = bound_angles(
                        logger=self._logger,
                        angles=[self._Θ1_sols[2], self._Θ2_sols[2], self._Θ3_sols[2],
                                self._Θ4_sols[6], self._Θ5_sols[6], self._Θ6_sols[6]]
                      )
      _solutions[7] = bound_angles(
                        logger=self._logger,
                        angles=[self._Θ1_sols[2], self._Θ2_sols[3], self._Θ3_sols[3],
                                self._Θ4_sols[7], self._Θ5_sols[7], self._Θ6_sols[7]]
                      )

      for sol in _solutions:
        _sol = []
        for ofst, sign, ang in zip(self.opw_params['ofsts'], self.opw_params['signs'], sol):
          _sol.append(sign * (glm.radians(ofst) + ang))
        self.solutions.append(_sol)

      self.solutions = np.round(np.degrees(self.solutions), 6).tolist()
    except Exception:
      self._logger.exception("Unable to tabulate the solutions because:")

  def solve(self) -> None:
    """
    Method to solve the Inverse Kinematics of the robot.

    Arguments:
      pose_d: glm.array
        desired pose
    """

    if self.opw_params is None:
      self._logger.warning("No ortho-parallet wrist parameters defined, unable to solve:")
      return

    self._compute_wcp()
    self._compute_geometric_params()
    self._compute_Θ1()
    self._compute_Θ2()
    self._compute_Θ3()
    self._compute_orientation_params()
    self._compute_Θ5()
    self._compute_Θ4()
    self._compute_Θ6()
    self._tabulate_solutions()


if __name__ == '__main__':
  """ For development purpose only"""
  robot_config = ConfigRobot(config_file='KR16-R2010-2.yaml')
  forward_kinematics = Forward(robot_config=robot_config)
  forward_kinematics._logger.info(f"{forward_kinematics.axes_origins=}")
  forward_kinematics._logger.info(f"{forward_kinematics.axes_pos_limits=}")
  forward_kinematics._logger.info(f"{forward_kinematics.axis_of_rot=}")
  forward_kinematics._logger.info(f"{forward_kinematics.rot_order=} for {robot_config.Brand.lower()}")
  forward_kinematics._logger.info(f"Robot Flange:\n{forward_kinematics.robot_flange}")
  forward_kinematics._logger.info(f"{forward_kinematics.axes_angles=}")
  # forward_kinematics._logger.remove_log_files()
  axes_angles = [0.000000, -90.000000, 90.000000, 0.000000, 0.000000, 0.000000]
  # axes_angs = [-1.000000, -91.000000, 89.000000, 1.000000, -1.000000, 1.000000]
  # forward_kinematics.compute_using_dh_params(axes_angs=axes_angs)
  # forward_kinematics._logger.info(f"Robot Pose using DH:\n{forward_kinematics.robot_pose}")
  forward_kinematics.compute_using_axes_offsts(axes_angles=axes_angles)
  forward_kinematics._logger.info(f"Robot Pose using Axes Offsets:\n{forward_kinematics.axes_transforms[-1]}")
  forward_kinematics._logger.info(f"Final:\n{forward_kinematics.axes_transforms[-1] @ forward_kinematics.robot_flange}")
  forward_kinematics._logger.info(
    f"Retrieved:\n{forward_kinematics.axes_transforms[-1] @ forward_kinematics.robot_flange @ glm.inverse(forward_kinematics.robot_flange)}"
  )
  forward_kinematics._logger.info(f"Angle X:\n{glm.degrees(forward_kinematics.robot_pose[1].x)}")
  forward_kinematics._logger.info(f"Angle Y:\n{glm.degrees(forward_kinematics.robot_pose[1].y)}")
  forward_kinematics._logger.info(f"Angle Z:\n{glm.degrees(forward_kinematics.robot_pose[1].z)}")
  # jac = forward_kinematics.compute_jacobian_world(axes_angs=axes_angs)
  # forward_kinematics._logger.info(f"Jacobian world:\n{np.round(jac, 2)}")
  # jac = forward_kinematics.compute_jacobian_eef(axes_angs=axes_angs)
  # forward_kinematics._logger.info(f"Jacobian eef:\n{np.round(jac, 2)}")
  # pose_d = glm.array.from_numbers(
  #           glm.float32, 1.1718, 0.0, 1.64, 0.0, 90.0117, 0.0
  #         )
  # inverse_kinematics = Inverse(robot_config=robot_config, solver_name='gn')
  # inverse_kinematics._logger.remove_log_files()
  # res = inverse_kinematics.solve_ik(pd=pose_d, q0=axes_angs)
  # inverse_kinematics._logger.info(f"IK result:\n{res}")
  # inverse_kinematics._logger.info(f"Angles:\n{res[0]}")
  inverse_kinematics = SphericalWristInverse(robot_config=robot_config)
  inverse_kinematics.target_pose = glm.array.from_numbers(
                                    glm.float32, 1.063, 0.07, 1.595, 0.0, 90.0, 0.0
                                  )
  inverse_kinematics.solve()