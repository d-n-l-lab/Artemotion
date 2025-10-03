## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes & functions to generate Bezier curves.
##
##############################################################################################
##
import os
import sys
import glm
import numpy as np

from dataclasses import dataclass, field
from typing import List

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings.Logger import Logger


class DummyLogger(Logger):

  pass


# Maximum number of points in a curve
MAX_POINTS_LINEAR = 2
MAX_POINTS_QUADRATIC = 3
MAX_POINTS_CUBIC = 4

# Interval (0 ≤ t ≤ 1)
INTERVAL_START = 0
INTERVAL_END = 1


def _points_check(logger: Logger, points: glm.array, max_points: int) -> bool:
  """
  Function to assert the number of points against maximum points.

  Arguments:
    logger: Logger
      Logger class
    points: glm.array
      coordinate points to create the curve
    max_points: int
      Maximum points

  Returns:
    valid: bool
      validity of the number of points
  """

  valid = True
  try:
    assert(len(points) == max_points)
  except AssertionError:
    valid = False
    logger.exception(f"Number of points are not equal to {max_points}.")

  return valid

def _num_samples_check(logger: Logger, num_samples: int) -> bool:
  """
  Function to assert the number of points against maximum points.

  Arguments:
    logger: Logger
      Logger class
    num_samples: int
      Number of samples to be generated, it must be non-negative

  Returns:
    valid: bool
      validity of the number of points
  """

  valid = True
  try:
    assert(num_samples >= 0)
  except AssertionError:
    valid = False
    logger.exception("Number of samples less than zero.")

  return valid

def binomial_coefficient(deg: int, elem: int) -> int:
  """
  Function to compute Binomial Coefficient from the pair of integers n ≥ k ≥ 0 and is represented
  as (n , k). The binomial integers are coefficients in a binomial theorem.

  (n k) = n! / (k! * (n - k)!)

  Arguments:
    deg: int
      degree of polynomial
    elem: int
      index

  Returns:
    coeff: int
      binomial coefficient of element
  """

  if elem < 0 or elem > deg:
    return 0
  coeff = 1
  for i in range(min(elem, deg - elem)):
    coeff = coeff * (deg - elem)//(i + 1)

  return coeff

def compute_look_up(deg: int) -> List[list]:
  """
  Function to generate Pascal's Triangle.

  Argument:
    deg: int
      degree of polynomial

  Returns:
    lut: List[list]
      Pascal's triangle
  """

  row_1, row_2 = [1], [1, 1]
  lut = [row_1]
  while len(lut) <= deg:
    row_1, row_2 = row_2, [1] + [sum(pair) for pair in zip(row_2, row_2[1:])] + [1]
    lut.append(row_1)

  return lut

def bezier_linear(logger: Logger, points: glm.array, num_samples: int) -> glm.array:
  """
  Function to compute linear Bezier curve with two control points p{0} and p{1} to be parameterized
  by:

  b(t) = (1 - t)*p{0} + t*p{1}, 0 ≤ t ≤ 1

  p (2D space) => glm.array(glm.vec3(p{0}_x, p{0}_y), glm.vec3(p{1}_x, p{1}_y))
  p (3D space) => glm.array(glm.vec3(p{0}_x, p{0}_y, p{0}_z), glm.vec3(p{1}_x, p{1}_y, p{1}_z))

  Arguments:
    logger: Logger
      Logger class
    points: glm.array
      coordinate points to create the curve
    num_samples: int
      Number of samples to be generated, it must be non-negative

  Returns:
    bezier: glm.array
      Multiple points(x, y, z) to create the curve
  """

  bezier = None
  if _points_check(logger=logger, points=points, max_points=MAX_POINTS_LINEAR) and \
    _num_samples_check(logger=logger, num_samples=num_samples):
    try:
      t = np.linspace(INTERVAL_START, INTERVAL_END, num_samples)
      bezier = [np.round_((1 - t) * p[0] + t * p[1], decimals=3) for p in np.transpose(points)]
    except Exception:
      logger.exception("Unable to compute linear Bezier curve because:")
      return bezier
    else:
      try:
        return glm.array(np.stack(bezier, axis=1).flatten().astype(glm.float32))
      except Exception:
        logger.exception(f"Unable to stack Bezier Curve because:")
  else:
    return bezier

def bezier_quadratic(logger: Logger, points: glm.array, num_samples: int) -> glm.array:
  """
  Function to compute quadratic Bezier curve with three control points p{0}, p{1} and p{2} to be
  parameterized by:

  b(t) = ((1 - t)^2)*p{0} + 2*t*(1 - t)*p{1} + (t^2)*p{2}, 0 ≤ t ≤ 1

  p (2D space) => glm.array(glm.vec3(p{0}_x, p{0}_y), glm.vec3(p{1}_x, p{1}_y))
  p (3D space) => glm.array(glm.vec3(p{0}_x, p{0}_y, p{0}_z), glm.vec3(p{1}_x, p{1}_y, p{1}_z))

  Arguments:
    logger: Logger
      Logger class
    points: glm.array
      coordinate points to create the curve
    num_samples: int
      Number of samples to be generated, it must be non-negative

  Returns:
    bezier: glm.array
      Multiple points(x, y, z) to create the curve
  """

  bezier = None
  if _points_check(logger=logger, points=points, max_points=MAX_POINTS_QUADRATIC) and \
    _num_samples_check(logger=logger, num_samples=num_samples):
    try:
      t = np.linspace(INTERVAL_START, INTERVAL_END, num_samples)
      bezier = [np.round_(
                  ((1 - t)**2) * p[0] + 2 * t * (1 - t) * p[1] + (t**2) * p[2],
                  decimals=3
                )
                for p in np.transpose(points)]
    except Exception:
      logger.exception("Unable to compute quadratic Bezier curve because:")
      return bezier
    else:
      try:
        return glm.array(np.stack(bezier, axis=1).flatten().astype(glm.float32))
      except Exception:
        logger.exception(f"Unable to stack Bezier Curve because:")
  else:
    return bezier

def bezier_cubic(logger: Logger, points: glm.array, num_samples: int) -> glm.array:
  """
  Function to compute quadratic Bezier curve with three control points p{0}, p{1} and p{2} to be
  parameterized by:

  b(t) = ((1 - t)^3)*p{0} + 3*t*((1 - t)^2)*p{1} + (3*t^2)*(1 - t)*p{2} + (t^3)*p{3}, 0 ≤ t ≤ 1

  p (2D space) => glm.array(glm.vec3(p{0}_x, p{0}_y), glm.vec3(p{1}_x, p{1}_y))
  p (3D space) => glm.array(glm.vec3(p{0}_x, p{0}_y, p{0}_z), glm.vec3(p{1}_x, p{1}_y, p{1}_z))

  Arguments:
    logger: Logger
      Logger class
    points: glm.array
      array of coordinate points to create the curve
    num_samples: int
      Number of samples to be generated, it must be non-negative

  Returns:
    bezier: glm.array
      Multiple points(x, y, z) to create the curve
  """

  bezier = None
  if _points_check(logger=logger, points=points, max_points=MAX_POINTS_CUBIC) and \
    _num_samples_check(logger=logger, num_samples=num_samples):
    try:
      t = np.linspace(INTERVAL_START, INTERVAL_END, num_samples)
      bezier = [np.round_(
                  ((1 - t)**3) * p[0] + 3 * t * ((1 - t)**2) * p[1] +
                  3 * (t**2) * (1 - t) * p[2] +
                  (t**3) * p[3],
                  decimals=3
                ) for p in np.transpose(points)]
    except Exception:
      logger.exception("Unable to compute cubic Bezier curve because:")
      return bezier
    else:
      try:
        return glm.array(np.stack(bezier, axis=1).flatten().astype(glm.float32))
      except Exception:
        logger.exception(f"Unable to stack Bezier Curve because:")
  else:
    return bezier

def double(logger: Logger, p: glm.quat, q: glm.quat) -> glm.quat:
  """
  Function to compute the arc double. This method is based on the suggestions made by
  Ken Shoemake.

  https://dl.acm.org/doi/pdf/10.1145/325334.325242

  Arguments:
    logger: Logger
      logger class
    p: glm.quat
      first quaternion
    q: glm.quat
      second quaternion

  Returns:
    double: glm.quat
      arc double
  """

  double = glm.quat()
  try:
    double = 2 * glm.dot(p, q) @ q - p
  except Exception:
    logger.exception("Unable to compute arc double because:")
  finally:
    return double

def bisect(logger: Logger, p: glm.quat, q: glm.quat) -> glm.quat:
  """
  Function to compute the normalized quaternion of the summation of the two given quaternions.
  This method is based on the suggestions made by Ken Shoemake.

  https://dl.acm.org/doi/pdf/10.1145/325334.325242

  Arguments:
    logger: Logger
      logger class
    p: glm.quat
      first quaternion
    q: glm.quat
      second quaternion

  Returns:
    bisect: glm.quat
      normalized quaternion of p + q
  """

  bisect = glm.quat()
  try:
    bisect = glm.normalize(p + q)
  except Exception:
    logger.exception("Unable to compute normal because:")
  finally:
    return bisect


@dataclass(kw_only=True)
class Bezier_N_Deg:
  """
  Class to efficiently compute N-Degree Bezier Curve.

  p (2D space) => glm.array(glm.vec3(p{0}_x, p{0}_y), glm.vec3(p{1}_x, p{1}_y))
  p (3D space) => glm.array(glm.vec3(p{0}_x, p{0}_y, p{0}_z), glm.vec3(p{1}_x, p{1}_y, p{1}_z))

  Arguments:
    logger: Logger
      Logger class
    points: glm.array
      2D/3D points in space
    num_samples: int
      Number of samples to be generated, it must be non-negative
  """

  _logger: Logger = field(default_factory=DummyLogger, repr=False)
  _lut: List = field(default_factory=list, init=False, repr=False)

  _num_samples: int = field(default=100, init=False)
  ratios: List[int] = field(default_factory=list, init=False)
  points: glm.array | np.ndarray = glm.array(np.array([])).reinterpret_cast(glm.vec3)

  def __post_init__(self) -> None:
    """
    Post init method.
    """

    # num_samples >= 0
    if not _num_samples_check(logger=self._logger, num_samples=self.num_samples):
      self.delete()
      return None

    self._setup_bezier()

  @staticmethod
  def _summation(samples: List[np.ndarray]) -> List[np.ndarray]:
    """
    Method to compute the summation of the sampled points.

    Argument:
      samples: List[np.ndarray]
        Array of sampled values for a given point (weighted &/or rational)
    """

    result = samples[0]
    for i in range(len(samples) - 1):
        for j in range(len(result)):
            result[j] += samples[i + 1][j]

    return result

  def _setup_bezier(self) -> glm.array | None:
    """
    Method to compute the parameters required to finally compute the Bezier curve.

    Returns:
      points: glm.array | None
        return points back if only one point
    """

    # At least 1 point are there
    try:
      assert(len(self.points) > 0)
      if len(self.points) == 1:
        return self.points.reinterpret_cast(glm.float32)
    except AssertionError:
      self.delete()
      return

    self._t = np.linspace(INTERVAL_START, INTERVAL_END, self.num_samples)
    self._total_points = len(self.points) - 1
    self._lut = compute_look_up(deg=self._total_points)
    self.ratios = [1 for i in range(len(self.points))]

  def _basis_polynomial(self, point_idx: int) -> np.ndarray:
    """
    Method to compute the basis polynomial term in the Bezier function.

    p(t) = sum(i = 0 -> n) ((t^i) * (1 - t)^(n - i)) * r{i}, 0 ≤ t ≤ 1

    wehere:
      r{i}: ratios to rationalize the points

    Arguments:
      point_idx: int
        point index

    Returns:
      result: np.ndarray
        calculated polynomial term
    """

    return (self._t ** point_idx) * ((1 - self._t)**(self._total_points - point_idx))

  def _n_index_weighted_bezier_point(self, point_idx: int,
                                     point: glm.vec2 | glm.vec3) -> List[np.ndarray]:
    """
    Method to compute the Bezier curve point at nth index given n + 1 control points p{0}, p{1},
    ..., p{n} and can be parameterized by De Casteljau's algorithm:

    B(t) = sum(i = 0 -> n) (C(n i) * (t^i) * ((1 -t)^(n - i)) * p{i}), 0 ≤ t ≤ 1

    where C(n i) is a binomial coefficient.

    Arguments:
      point_idx: int
        point index
      point:
        2D/3D point in space

    Returns:
      result: List[np.ndarray]
        Array of sampled values for a given point
    """

    basis_poly = self._basis_polynomial(point_idx=point_idx)

    return [np.round_(self._lut[self._total_points][point_idx] * basis_poly * p, decimals=3)
            for p in point]

  def _n_degree_weighted_bezier_curve(self) -> glm.array:
    """
    Method to compute the Bezier curve of n degree.

    Returns:
      result: glm.array
        Bezier curve of n dimension ([0...(Number of dimensions - 1)])
    """

    samples = [self._n_index_weighted_bezier_point(point_idx=idx, point=point)
               for idx, point in enumerate(self.points)]

    return glm.array(
      np.stack(Bezier_N_Deg._summation(samples=samples), axis=1).flatten().astype(glm.float32)
    )

  def _n_index_weighted_rational_bezier_point(self, point_idx: int,
                                              point: glm.vec2 | glm.vec3) -> List[np.ndarray]:
    """
    Method to compute the Bezier curve point at nth index given n + 1 control points p{0}, p{1},
    ..., p{n} and can be parameterized by the ratios:

    B(t) = sum(i = 0 -> n) ((C(n i) * (t^i) * ((1 -t)^(n - i)) * p{i} * r{i})/
                            (C(n i) * (t^i) * ((1 -t)^(n - i)) * r{i})), 0 ≤ t ≤ 1

    where C(n i) is a binomial coefficient.
          r{i} is a ratio of the point

    Arguments:
      point_idx: int
        point index
      point:
        2D/3D point in space

    Returns:
      result: List[np.ndarray]
        Array of sampled values for a given point (weighted & rational)
    """


    basis_poly = self._basis_polynomial(point_idx=point_idx)

    # Denominator based on ratios
    basis = [
      np.round_(
        self._lut[self._total_points][point_idx] * basis_poly * self.ratios[point_idx],
        decimals=3
      ) for p in point
    ]

    # Numerator based on the weight of the coordinates
    weighted = [np.round_(b * point[idx], decimals=3) for idx, b in enumerate(basis)]

    return weighted, basis

  def _n_degree_rational_bezier_curve(self) -> glm.array:
    """
    Method to compute the rational Bezier curve of n degree.

    Returns:
      result: glm.array
        Bezier curve of n dimension ([0...(Number of dimensions - 1)])
    """

    samples = [self._n_index_weighted_rational_bezier_point(point_idx=idx, point=point)
               for idx, point in enumerate(self.points)]

    weighted, basis = zip(*[s for s in samples])

    w_result = Bezier_N_Deg._summation(samples=weighted)

    b_result = Bezier_N_Deg._summation(samples=basis)

    return glm.array(
      np.stack(
        [np.round_(w/b, decimals=3) for w, b in zip(w_result, b_result)],
        axis=1
      ).flatten().astype(glm.float32)
    )

  def compute(self, rationalize: bool=False) -> glm.array:
    """
    Method to compute Bezier Curve points.

    Arguments:
      rationalize: bool
        Flag to compute rationalized or Weighted Bezier Curve

    Returns:
      points: glm.array
        array containing points (XYZ) of the curves
    """

    points = self._setup_bezier()
    if points is not None:
      return points

    if rationalize:
      return self._n_degree_rational_bezier_curve()
    else:
      return self._n_degree_weighted_bezier_curve()

  def delete(self) -> None:
    """
    Delete Method.
    """

    self._lut = []
    self.num_samples = 100
    self.points = glm.array(np.array([])).reinterpret_cast(glm.vec3)

  @property
  def num_samples(self) -> int:
    """
    Property: Number of samples.

    Returns:
      num_samples: int
        number of samples
    """

    return self._num_samples

  @num_samples.setter
  def num_samples(self, value: int) -> None:
    """
    Property setter: Number of samples.

    Arguments:
      value: int
    """

    self._num_samples = value


@dataclass(kw_only=True)
class SphericalBezier:
  """
  Class to efficiently compute N-Degree Spherical Bezier Curve. This uses De-Casteljau's
  algorithm with Slerp (Spherical Linear Interpolation).

  Arguments:
    logger: Logger
      Logger class
    angles: glm.array(glm.vec3)
      array containing 2D/3D angles in space
    num_samples: int
      Number of samples to be generated, it must be non-negative
  """

  _logger: Logger = field(default_factory=DummyLogger, repr=False)

  num_samples: int = 100
  angles: glm.array | np.ndarray = glm.array(np.array([])).reinterpret_cast(glm.vec3)

  def __post_init__(self) -> None:
    """
    Post init method.
    """

    # num_samples >= 0
    if not _num_samples_check(logger=self._logger, num_samples=self.num_samples):
      self.delete()
      return None

    self._u = np.linspace(INTERVAL_START, INTERVAL_END, self.num_samples)
    self._setup_bezier()

  def _setup_bezier(self) -> glm.array | None:
    """
    Method to compute the parameters required to finally compute the Bezier curve.

    Returns:
      points: glm.array | None
        return points back if only one point
    """

    # At least 1 angle vector are there
    try:
      assert len(self.angles) > 0
    except AssertionError:
      self.delete()
      return
    else:
      # convert to quaternions
      angles = [glm.quat(glm.radians(ang)) for ang in self.angles]
      if len(self.angles) == 1:
        return self.angles.reinterpret_cast(glm.float32)
      elif len(self.angles) == 2:
        return [glm.slerp(angles[0], angles[1], u) for u in self._u]

    self._total_angles = len(self.angles) - 1

  def _compute_angle_at_curve(self, angles: List, u: float) -> glm.quat:
    """
    Method to compute the angle at the interpolated angle based on the theory proposed by
    Ken Shoemake.

    Arguments:
      angles: List
        list of quaternions
      u: float
        sample

    Returns:
      quat: glm.quat
        angle/quaternion at the curve
    """

    an = bisect(logger=self._logger,
                p=double(logger=self._logger, p=angles[0], q=angles[1]),
                q=angles[2])
    b_n_1 = double(logger=self._logger, p=an, q=angles[2])

    p_1 = glm.slerp(angles[1], an, u)
    p_2 = glm.slerp(an, b_n_1, u)
    p_3 = glm.slerp(b_n_1, angles[2], u)
    p_1_2 = glm.slerp(p_1, p_2, u)
    p_2_3 = glm.slerp(p_2, p_3, u)
    p = glm.slerp(p_1_2, p_2_3, u)

    return p

  def _compute_n_degree_bezier_angles(self) -> glm.array:
    """
    Method to compute the Bezier angles of n degree. The computation is as proposed by
    Ken Shoemake.

    https://dl.acm.org/doi/pdf/10.1145/325334.325242

    Returns:
      angles: glm.array
        Bezier angles of n dimension
    """

    angles = [glm.quat(ang) for ang in self.angles]
    quats = [self._compute_angle_at_curve(angles=angles, u=u) for u in self._u]
    return quats

  def compute(self) -> glm.array:
    """
    Method to compute Bezier Curve angles.

    points: glm.array
      array containing points (XYZ) of the curves
    """

    slerps = glm.array(np.array([])).reinterpret_cast(glm.vec3)
    quats = self._setup_bezier()
    if quats is not None:
      for q in quats:
        slerps = glm.array(slerps).concat(
          glm.array(glm.eulerAngles(q))
        )
      return slerps

    return self._compute_n_degree_bezier_angles()

  def delete(self) -> None:
    """
    Delete method.
    """

    self.num_samples = 100
    self.angles = glm.array(np.array([])).reinterpret_cast(glm.vec3)


@dataclass(kw_only=True)
class BezierSpline:
  """
  Class to compute Spline Curve using Bezier Interpolation.

  This class takes robot poses as arguments and interpolates through them to create curves/path.

  Arguments:
    logger: Logger
      Logger class
    poses: glm.array
      robot pose comprises of cartesian pose (XYZ) & angles (ABC)
    num_samples: int
      Number of samples to be generated, it must be non-negative
  """

  _num_samples: int = 100
  logger: Logger = field(default_factory=DummyLogger, repr=False)
  poses: glm.array | np.ndarray = glm.array(np.array([])).reinterpret_cast(glm.vec3)

  def __post_init__(self):
    # Coordinates interpolation
    self._trans_curve = Bezier_N_Deg(_logger=self.logger)
    # Orientation interpolation
    self._orien_curve = Bezier_N_Deg(_logger=self.logger)

  def _setup_spline(func: object) -> None:
    """
    Method to compute the parameters required to finally compute the Bezier curve.

    Returns:
      points: glm.array | None
        return points back if only one point
    """

    def wrapper_setup_spline(self, *args, **kwargs):
      if len(self.poses) < 1:
        return

      self._trans_curve.points = self.poses[0::2] # 0,2,4,...
      self._orien_curve.points = self.poses[1::2] # 1,3,5,...

      return func(self, *args, **kwargs)

    return wrapper_setup_spline

  @property
  def num_samples(self) -> int:
    """
    Property: Number of samples.

    Returns:
      num_samples: int
        number of samples
    """

    return self._num_samples

  @num_samples.setter
  def num_samples(self, value: int) -> None:
    """
    Property setter: Number of samples.

    Arguments:
      value: int
    """

    self._num_samples = value
    self._trans_curve.num_samples = self._num_samples
    self._orien_curve.num_samples = self._num_samples

  @property
  @_setup_spline
  def coords(self) -> glm.array:
    """
    Interpolated Coordinates of the computed curve.

    Returns:
      coords: glm.array
        array containing the interpolated coordinates (XYZ) of the Bezier Curve
    """

    self._trans_curve.num_samples = self.num_samples
    return self._trans_curve.compute()

  @property
  @_setup_spline
  def angles(self) -> glm.array:
    """
    Interpolated Angles of the computed curve.

    Returns:
      coords: glm.array
        array containing the interpolated angles (ABC) of the Bezier Curve
    """

    self._orien_curve.num_samples = self.num_samples
    return self._orien_curve.compute()

  @property
  @_setup_spline
  def spline_poses(self) -> glm.array:
    """
    Interpolated poses of the computed curve.

    Returns:
      poses: glm.array
        array containing the interpolated poses (XYZABC) of the Bezier Curve
    """

    self._trans_curve.num_samples = self.num_samples
    self._orien_curve.num_samples = self.num_samples
    coords = self._trans_curve.compute().reinterpret_cast(glm.vec3)
    angles = self._orien_curve.compute().reinterpret_cast(glm.vec3)
    return glm.array(
            np.hstack((coords, angles)).flatten().astype(glm.float32)
          ).reinterpret_cast(glm.vec3)


if __name__ == '__main__':
  """For development purpose only"""
  DummyLogger.remove_log_files()
  import random
  num_points = 5
  points = glm.array(np.array([])).reinterpret_cast(glm.vec3)
  for point in range(num_points):
    points = glm.array(points).concat(
              glm.array(
                glm.radians(
                  glm.vec3(
                    random.uniform(-180, 180), random.uniform(-180, 180), random.uniform(-180, 180)
                  )
                )
              )
            )
  num_samples = 10
  # DummyLogger.info(
  #   f"Linear Bezier Curve: {bezier_linear(logger=DummyLogger, points=points[:2], num_samples=num_samples)}"
  # )
  # DummyLogger.info(
  #   f"Quadratic Bezier curve: {bezier_quadratic(logger=DummyLogger, points=points[:3], num_samples=num_samples)}"
  # )
  # DummyLogger.info(
  #   f"Cubic Bezier curve: {bezier_cubic(logger=DummyLogger, points=points[:4], num_samples=num_samples)}"
  # )
  DummyLogger.info(f"Points: {points}")
  # DummyLogger.info(f"Pascal's Triangle: {compute_look_up(deg=(len(points) - 1))}")
  # bezier_dc = Bezier_N_Deg(_logger=DummyLogger, points=points, num_samples=num_samples)
  bezier_dc = Bezier_N_Deg(_logger=DummyLogger, num_samples=num_samples)
  # bezier_dc.points = glm.array(
  #                     glm.vec3(random.uniform(-10, 10), random.uniform(0, 5), random.uniform(-15, 15))
  #                    )
  bezier_dc.points = points
  DummyLogger.info(f"Bezier N Deg dataclass: {bezier_dc}")
  result = bezier_dc.compute(rationalize=True)
  DummyLogger.info(f"Bezier Curve: {result} with type: {type(result[0])}")
  num_angles = 3
  angles = glm.array(np.array([])).reinterpret_cast(glm.vec3)
  for angle in range(num_angles):
    angles = glm.array(angles).concat(
      glm.array(
        glm.vec3(random.uniform(-180, 180), random.uniform(-180, 180), random.uniform(-180, 180))
      )
    )
  bezier_ang = SphericalBezier(_logger=DummyLogger, num_samples=num_samples)
  bezier_ang.angles = angles
  result = bezier_ang.compute()
  DummyLogger.info(f"Bezier Angles: {result} with type: {len(result)}")

  num_poses = 10
  poses = glm.array(np.array([])).reinterpret_cast(glm.vec3)
  for p in range(num_poses):
    poses = glm.array(poses).concat(
              glm.array(
                glm.vec3(
                  random.uniform(-10, 10), random.uniform(0, 5), random.uniform(-15, 15)
                ),
                glm.radians(
                  glm.vec3(
                    random.uniform(-180, 180), random.uniform(-180, 180), random.uniform(-180, 180)
                  )
                )
              )
            )
  num_samples = 10
  spline = BezierSpline(logger=DummyLogger, num_samples=num_samples)
  spline.poses = poses
  DummyLogger.info(f"{spline.coords=}")
  DummyLogger.info(f"{spline.angles=}")
  DummyLogger.info(f"{spline.spline_poses=}")