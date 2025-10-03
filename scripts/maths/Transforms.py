## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various functions to perform matrix and maths operations
##              related to OpenGL 3D grphics pipeline.
##
##############################################################################################
##
import os
import sys
import glm

from typing import List

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings.Logger import Logger


class DummyLogger(Logger):

  pass

def normalize(logger: Logger, debug: bool=False, nx: float=0.0, ny:float=0.0,
              nz: float=0.0) -> glm.vec3:
  """
  Returns a unit vector in 3D space.

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
    nx: float
      x coordinate of the vector
    ny: float
      y coordinate of the vector
    nz: float
      z coordinate of the vector

  Returns:
    norm: glm.vec3
      3-dimensional normalized vector
  """

  norm = glm.normalize(glm.vec3(nx, ny, nz))
  if debug: logger.info(f"Normalized vector: {norm}")
  return norm

def get_rotation_matrix(logger: Logger, debug: bool=False, deg: float=0.0, rx: float=0.0,
                        ry: float=0.0, rz: float=0.0) -> glm.mat4x4:
  """
  Returns a rotational matrix of dimension 4x4.

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
    deg: float
      rotation angle in degrees
    rx: float
      rotation w.r.t X axis if value = 1.0
    ry: float
      rotation w.r.t Y axis if value = 1.0
    rz: float
      rotation w.r.t Z axis if value = 1.0

  Returns:
    out: glm.mat4x4): a 4x4 rotational matrix
  """

  out = glm.rotate(deg_to_rad(logger=logger, deg=deg), glm.vec3(rx, ry, rz))
  if debug: logger.info(f"Rotation matrix: {out} with type: {type(out)}")
  return out

def get_translation_matrix(logger: Logger, debug: bool=False, tx: float=0.0, ty: float=0.0,
                           tz: float=0.0) -> glm.mat4x4:
  """
  Returns a translational matrix of dimension 4x4.

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
    tx: float
      value to translate a vector w.r.t X coordinate
    ty: float
      value to translate a vector w.r.t Y coordinate
    tz: float
      value to translate a vector w.r.t Z coordinate

  Returns:
    out: glm.mat4x4
      a 4x4 translational matrix
  """

  out = glm.translate(glm.vec3(tx, ty, tz))
  if debug: logger.info(f"Translated matrix: {out} with type: {type(out)}")
  return out

def get_scale_matrix(logger: Logger, debug: bool=False, sx: float=1.0, sy: float=1.0,
                     sz: float=1.0) -> glm.mat4x4:
  """
  Returns a matrix of dimension 4x4 to scale a vector.

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
    sx: float
      value to scale a vector w.r.t X coordinate
    sy: float
      value to scale a vector w.r.t Y coordinate
    sz: float
      value to scale a vector w.r.t Z coordinate

  Returns:
    out: glm.mat4x4
      a 4x4 scale matrix
  """

  out = glm.scale(glm.vec3(sx, sy, sz))
  if debug: logger.info(f"Scaled matrix: {out} with type: {type(out)}")
  return out

def deg_to_rad(logger: Logger, deg: float, debug: bool=False) -> float:
  """
  Converts degrees to radians.

  Arguments:
    logger: Logger
      logger class
    deg: float:
      angle value in degrees
    debug: bool
      flag to print log message

  Returns:
    rad: float
      angle value in radians
  """

  rad = round(glm.radians(deg), 3)
  if debug: logger.info(f"Converted {deg} degrees to {rad} radians.")
  return rad

def rad_to_deg(logger: Logger, rad: float, debug: bool=False) -> float:
  """
  Converts radians to degrees.

  Arguments:
    logger: Logger
      logger class
    rad: float
      angle value in radians
    debug: bool
      flag to print log message

  Returns:
    deg: float
      angle value in degrees
  """

  deg = round(glm.degrees(rad), 3)
  if debug: logger.info(f"Converted {rad} radians to {deg} degrees.")
  return deg

def y_is_up(logger: Logger, debug: bool=False) -> glm.mat4:
  """
  Returns rotation matrix making Y axis in up direction.

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
  """

  y_is_up = get_rotation_matrix(logger=logger, debug=debug, deg=-90.0, rx=1)
  if debug: logger.info(f"Y is Up matrix: {y_is_up}")
  return y_is_up

def euler_to_mat(logger: Logger, Θx: float, Θy: float, Θz: float, order: str='zyx',
                 debug: bool=False) -> glm.mat4:
  """
  Function to compute rotation matrix (ZYX rotation order) from given Euler Angles.

  Arguments:
    logger: Logger
      logger class
    Θx: float
      angle of rotation along X axis (in deg)
    Θy: float
      angle of rotation along Y axis (in deg)
    Θz: float
      angle of rotation along Z axis (in deg)
    order: str
      order of rotation, default to zyx
    debug: bool
      flag to print log message

  Returns:
    rot_mat: glm.mat4
      4x4 rotation matrix
  """

  rot_mat = glm.mat4()

  if order.lower() == 'zyx':
    rot_mat = (get_rotation_matrix(logger=logger, deg=Θz, rz=1.0) @
               get_rotation_matrix(logger=logger, deg=Θy, ry=1.0) @
               get_rotation_matrix(logger=logger, deg=Θx, rx=1.0))
  elif order.lower() == 'xyz':
    rot_mat = (get_rotation_matrix(logger=logger, deg=Θx, rx=1.0) @
               get_rotation_matrix(logger=logger, deg=Θy, ry=1.0) @
               get_rotation_matrix(logger=logger, deg=Θz, rz=1.0))
  elif order.lower() == 'zyz':
    rot_mat = (get_rotation_matrix(logger=logger, deg=Θz, rz=1.0) @
               get_rotation_matrix(logger=logger, deg=Θy, ry=1.0) @
               get_rotation_matrix(logger=logger, deg=Θz, rz=1.0))
  elif order.lower() == 'zxz':
    rot_mat = (get_rotation_matrix(logger=logger, deg=Θz, rz=1.0) @
               get_rotation_matrix(logger=logger, deg=Θx, rx=1.0) @
               get_rotation_matrix(logger=logger, deg=Θz, rz=1.0))
  if debug: logger.info(f"Computed rotation matrix from Euler ({order}) angles: \n{rot_mat}")

  return rot_mat

def _euler_angles_xyz(mat: glm.mat3) -> glm.vec3:
  """
  Function to compute Euler Angles of XYZ rotation order.

  Arguments:
    rot_mat: glm.mat3
      3x3 rotation matrix

  Returns:
    euler_angles: glm.vec3
      vector containing ABC/RPY Euler angles (XYZ) in radians
  """

  if mat[2,0] < 1:
      if mat[2,0] > -1:
          Θ_x = glm.atan2(-mat[2,1], mat[2,2])
          Θ_y = glm.asin(mat[2,0])
          Θ_z = glm.atan2(-mat[1,0], mat[0,0])
      else: # rot_mat[2,0] = -1
          Θ_x = -glm.atan2(mat[0,1], mat[1,1])
          Θ_y = -glm.pi() / 2
          Θ_z = 0.0
  else: # rot_mat[2,0] = +1
      Θ_x = glm.atan2(mat[0,1], mat[1,1])
      Θ_y = glm.pi() / 2
      Θ_z = 0.0

  return glm.degrees(glm.vec3(round(Θ_x, 3), round(Θ_y, 3), round(Θ_z, 3)))

def _euler_angles_zyx(mat: glm.mat3) -> glm.vec3:
  """
  Function to compute Euler Angles of ZYX rotation order.

  Arguments:
    rot_mat: glm.mat3
      3x3 rotation matrix

  Returns:
    euler_angles: glm.vec3
      vector containing ABC/RPY Euler angles (ZYX) in radians
  """

  if mat[0,2] < 1:
      if mat[0,2] > -1:
          Θ_x = glm.atan2(mat[1,2], mat[2,2])
          Θ_y = glm.asin(-mat[0,2])
          Θ_z = glm.atan2(mat[0,1], mat[0,0])
      else: # rot_mat[0,2] = -1
          Θ_x = 0.0
          Θ_y = glm.pi() / 2
          Θ_z = -glm.atan2(-mat[2,1], mat[1,1])
  else: # rot_mat[0,2] = +1
      Θ_x = 0.0
      Θ_y = -glm.pi() / 2
      Θ_z = glm.atan2(-mat[2,1], mat[1,1])

  return glm.degrees(glm.vec3(round(Θ_x, 3), round(Θ_y, 3), round(Θ_z, 3)))

def _euler_angles_zxz(mat: glm.mat3) -> glm.vec3:
  """
  Function to compute Euler Angles of ZXZ rotation order.

  Arguments:
    rot_mat: glm.mat3
      3x3 rotation matrix

  Returns:
    euler_angles: glm.vec3
      vector containing ABC/RPY Euler angles (ZXZ) in radians
  """

  if mat[2,2] < 1:
      if mat[2,2] > -1:
          Θ_x = glm.acos(mat[2,2])
          Θ_z_0 = glm.atan2(mat[2,0], -mat[2,1])
          Θ_z_1 = glm.atan2(mat[0,2], mat[1,2])
      else: # rot_mat[2,2] = -1
          Θ_x = -glm.pi()
          Θ_z_0 = -glm.atan2(-mat[1,0], mat[0,0])
          Θ_z_1 = 0.0
  else: # rot_mat[2,2] = +1
      Θ_x = 0.0
      Θ_z_0 = glm.atan2(-mat[1,0], mat[0,0])
      Θ_z_1 = 0.0

  return glm.degrees(glm.vec3(round(Θ_z_0, 3), round(Θ_x, 3), round(Θ_z_1, 3)))

def _euler_angles_zyz(mat: glm.mat3) -> glm.vec3:
  """
  Function to compute Euler Angles of ZYZ rotation order.

  Arguments:
    rot_mat: glm.mat3
      3x3 rotation matrix

  Returns:
    euler_angles: glm.vec3
      vector containing ABC/RPY Euler angles (ZYZ) in radians
  """

  if mat[2,2] < 1:
      if mat[2,2] > -1:
          Θ_y = glm.acos(mat[2,2])
          Θ_z_0 = glm.atan2(mat[2,1], mat[2,0])
          Θ_z_1 = glm.atan2(mat[1,2], -mat[0,2])
      else: # rot_mat[2,2] = -1
          Θ_y = -glm.pi()
          Θ_z_0 = -glm.atan2(-mat[0,1], mat[1,1])
          Θ_z_1 = 0.0
  else: # rot_mat[2,2] = +1
      Θ_y = 0.0
      Θ_z_0 = glm.atan2(mat[0,1], mat[1,1])
      Θ_z_1 = 0.0

  return glm.degrees(glm.vec3(round(Θ_z_0, 3), round(Θ_y, 3), round(Θ_z_1, 3)))

def mat_to_euler_angles(logger: Logger, debug: bool=False,
                        mat: glm.mat3 | glm.mat4=glm.mat3(0), order: str='zyx') -> glm.vec3:
  """
  Function to compute Euler Angles (ABC/RPY) from a given 3x3 rotation matrix or a 4x4
  transformation matrix.

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
    rot_mat: glm.mat3 | glm.mat4
      3x3 rotation matrix or 4x4 transformation matrix

  Returns:
    euler_angles: glm.vec3
      vector containing ABC/RPY Euler angles in radians
  """

  euler_angles = None
  if len(mat) < 3:
    logger.warning("Invalid matrix!!!")
    return None

  if len(mat) > 3:
    mat = glm.mat3(mat) # retrieve rotation matrix from transformation matrix

  try:
    if order.lower() == 'zyx':
      euler_angles = _euler_angles_zyx(mat=mat)
    elif order.lower() == 'xyz':
      euler_angles = _euler_angles_xyz(mat=mat)
    elif order.lower() == 'zyz':
      euler_angles = _euler_angles_zyz(mat=mat)
    elif order.lower() == 'zxz':
      euler_angles = _euler_angles_zxz(mat=mat)
  except Exception:
    logger.exception("Unable to compute Euler Angles because:")
  finally:
    return euler_angles

def matrix_to_pose(logger: Logger, debug: bool=False,
                   matrix: glm.mat4=glm.mat4(0), rot_order: str='zyx') -> glm.array:
  """
  Function to convert a 4x4 transformation matrix into a pose (XYZ & ABC/RPY angles).

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
    matrix: glm.mat4
      4x4 transformation matrix
    rot_order: str
      order of rotation

  Returns:
    pose: glm.array(glm.vec3)
      array containing position & euler angles
  """

  pose = None
  if len(matrix) < 4:
    logger.warning("Invalid transformation matrix!!!")
    return pose

  try:
    xyz = glm.vec3(matrix[3])
    rpy = mat_to_euler_angles(logger=logger, debug=debug, mat=matrix, order=rot_order)
    pose = glm.array(xyz, rpy)
  except Exception:
    logger.exception("Unable to compute pose because:")
  finally:
    if debug: logger.info(f"Pose: {pose}")
    return pose

def pose_to_matrix(logger: Logger, debug: bool=False,
                   pose: glm.array=glm.array.from_numbers(
                                    glm.float32, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                   rot_order: str='zyx') -> glm.mat4:
  """
  Function to convert a 4x4 transformation matrix into a pose (XYZ & ABC/RPY angles).

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
    pose: glm.array(glm.vec3)
      array containing position & euler angles
    rot_order: str
      order of rotation

  Returns:
    matrix: glm.mat4
      4x4 transformation matrix
  """

  matrix = glm.mat4()
  try:
    rot_mat = euler_to_mat(logger=logger, Θx=pose[3], Θy=pose[4], Θz=pose[5], order=rot_order)
    matrix = glm.mat4(rot_mat)
    for i in range(3):
      matrix[3,i] = pose[i]
  except Exception:
    logger.exception("Unable to create tranformation matrix because:")
  finally:
    if debug: logger.info(f"Transformation matrix:\n{matrix}")
    return matrix

def bound_angles(logger: Logger, debug: bool=False, angles: List=[]) -> List:
  """
  Function to limit the angles within ±π.

  Arguments:
    logger: Logger
      logger class
    debug: bool
      flag to print log message
    angles: List
      list containing angles in radians

  Returns:
    angles: List
      list of angles limited within ±π
  """

  if not angles:
    return

  for idx, ang in enumerate(angles):
    if glm.abs(ang) > glm.pi():
      sign = glm.abs(ang)/ang
      angles[idx] = ang - (sign * 2 * glm.pi())

  if debug: logger.info(f"Bounded angles: {angles}")
  return angles


if __name__ == '__main__':
  """For development purpose only"""
  DummyLogger.remove_log_files()
  deg_to_rad(logger=DummyLogger, deg=45.0)
  rad_to_deg(logger=DummyLogger, rad=0.35)
  get_translation_matrix(logger=DummyLogger, ty=0.75)
  get_scale_matrix(logger=DummyLogger, sx=0.2)
  get_rotation_matrix(logger=DummyLogger, deg=45.0, rx=1.0)
  normalize(logger=DummyLogger, nx=0.25, ny=0.12, nz=0.35)
  euler_to_mat(logger=DummyLogger, Θx=-90.0, Θy=47.5, Θz=-90.0, debug=True, order='zyx')
  matrix_to_pose(logger=DummyLogger, debug=True, matrix=glm.mat4(0))
  pose_to_matrix(logger=DummyLogger,
                 pose=glm.array.from_numbers(
                        glm.float32, 1183.00, -188.005, 1822.275, -90.00, 47.50, -90.00),
                 debug=True)
  bound_angles(logger=DummyLogger, debug=True,
               angles=[-3.141592653589793, -0.3457885648068931, -1.1571028281070295,
                       6.2831853071795845, -0.06810828305471094, -3.141592653589795])