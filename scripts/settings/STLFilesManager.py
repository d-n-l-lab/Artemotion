## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to parse the STL files and make parsed data ready for
##              3D rendering.
##
##############################################################################################
##
import os
import sys
import glm
import struct

import numpy as np

from io import BufferedReader

from typing import AnyStr, List, Tuple, Optional
from dataclasses import dataclass, field

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger


class DummyLogger(Logger):

  pass


def read_float(logger: Logger, file_obj: BufferedReader) -> None:
  """
  Function to read float data from the given file.

  Argument:
    file_path: BufferedReader
      file buffer object
  """

  try:
    float_bytes = file_obj.read(4)
    return struct.unpack('f', float_bytes)[0]
  except Exception:
    logger.exception("Unable to read float data from the file because:")
    return None

def read_unsigned_int(logger: Logger, file_obj: BufferedReader) -> Optional[int]:
  """
  Function to read unsigned int data from the given file.

  Argument:
    file_path: BufferedReader
      file buffer object
  """

  try:
    uint_bytes = file_obj.read(4)
    return struct.unpack('I', uint_bytes)[0]
  except Exception:
    logger.exception(f"Unable to read unsigned integer from the file because:")

def read_unsigned_short(logger: Logger, file_obj: BufferedReader) -> None:
  """
  Function to read unsigned short int data from the given file.

  Argument:
    file_path: BufferedReader
      file buffer object
  """

  try:
    uint16_bytes = file_obj.read(2)
    return struct.unpack('H', uint16_bytes)[0]
  except Exception:
    logger.exception(f"Unable to read unsigned short from the file because:")


@dataclass
class STLVec3D:

  """
  DataClass representing a 3D vector parsed from an STL file.

  Arguments:
    vector: glm.vec3
      3D vector (x, y, z)
  """

  vector: glm.vec3


@dataclass
class STLTriangle:

  """
  DataClass representing a traingle/facet in 3D space parsed from an STL file.

  Arguments:
    normal: STLVec3D
      normal vector
    vec0: STLVec3D
      first 3D coordinate vector
    vec1: STLVec3D
      second 3D coordinate vector
    vec2: STLVec3D
      third 3D coordinate vector
    attr: int
      attribute of a triangle
  """

  normal: STLVec3D
  vec0: STLVec3D
  vec1: STLVec3D
  vec2: STLVec3D
  attr: int


@dataclass
class STLData:

  """
  DataClass managing the parsed data from an STL file.

  Arguments:
    vertices: glm.array
      array containing the vertices
    indices: glm.array
      array containing the indices
    normals: glm.array
      array containing the normals
  """

  vertices: glm.array = field(default=glm.array(glm.float32), init=False)
  indices: glm.array = field(default=glm.array(glm.int32), init=False)
  normals: glm.array = field(default=glm.array(glm.float32), init=False)


class STLEOFException(Exception):

  """
  Exception class raised when reaching end of the STL file while reading.
  """

  pass


class STLBadLineException(Exception):

  """
  Exception class for bad lines found while reading an STL file.
  """

  pass


@dataclass
class STL:

  """
  Dataclass computing the vertex, indices & other attributes from a given STL file.

  Keyword Argument:
    logger: Logger
      logger class
    file_name: str
      name of the file to be parsed
  """

  logger: Logger = field(default_factory=DummyLogger, repr=False)
  file_name: str = field(default_factory='')

  name: str = field(default='', init=False)
  stl_data: STLData = field(default_factory=STLData, init=False)

  def __post_init__(self) -> None:
    self._file_path = PathManager.get_3d_file_path(logger=self.logger, file_name=self.file_name)
    self._file_format = self._get_file_format(stl_file=self._file_path)
    if self._file_format == "invalid":
      raise TypeError(f"STL file: {self.file_name} is not a valid/supported format")
    self.name = os.path.basename(self._file_path).split('.')[0]

  def _get_file_format(self, stl_file: os.PathLike[AnyStr]) -> str:
    """
    Method to check if the given stl file is an ASCII or Binary file.

    Argument:
      stl_file: os.PathLike[AnyStr]
        stl file path

    Returns:
      format: str
        invalid, ascii, binary
    """

    format = "invalid"
    try:
      file_size = os.path.getsize(stl_file)
      if file_size < 15:
        self.logger.warning(f"STL file is not long enough, file size: {file_size}")
        return format
      with open(stl_file, 'rb') as f:
        # Check for ascii format
        first_line_words = f.readline().split()
        if first_line_words[0] == b"solid":
          next_line_words = f.readline().split()
          if next_line_words[0] == b"facet":
            format = "ascii"
          if next_line_words[0] == b"endsolid":
            format = "ascii"

        # Check for binary format
        if format == "invalid":
          if file_size < 84:
            self.logger.warning(f"STL file is not long enough, file size: {file_size}")
            return format
          if not f.seek(80):
            self.logger.warning("Cannot seek the byte in the header)")
            return format
          num_triangles = read_unsigned_int(logger=self.logger, file_obj=f)
          if file_size == (84 + (num_triangles * 50)):
            format = "binary"
    except Exception:
      self.logger.exception("Unable to open stl file because:")
    finally:
      return format

  def _compute_vertices_indices(self, points: np.ndarray) -> None:
    """
    Method to determine unique vertices and the respective indices in the parsed STL points/
    triangles.

    Arguments:
      points: np.ndarray
        points/faces/triangles array
    """

    vertices = np.array([])
    indices = np.array([])
    try:
      # determine uniques
      p_uniques, p_indices, p_inverse = np.unique(points, return_index=True,
                                                  return_inverse=True, axis=0)
      # permutations
      sort_permut = np.argsort(p_indices)
      # vertices
      vertices = p_uniques[sort_permut]
      # indices
      inv_sort = np.empty_like(sort_permut)
      inv_sort[sort_permut] = np.arange(len(inv_sort))
      indices = inv_sort[p_inverse]
    except Exception:
      self.logger.exception("Unable to compute vertices & indices because:")
    finally:
      self.stl_data.vertices = glm.array(np.array(vertices)).reinterpret_cast(glm.float32)
      self.stl_data.indices = glm.array(np.array(indices)).reinterpret_cast(glm.int32)

  def _parse_ascii_stl(self, stl_file: BufferedReader) -> None:
    """
    Nethod to parse the binary stl file.

    Argument:
      stl_file: BufferedReader
        stl file buffer object
    """

    try:
      lines = [l.strip() for l in stl_file.readlines()]
    except Exception:
      self.logger.exception("Unable to readlines because:")
    else:
      # normals
      normals = np.array([np.array(line.replace(b'facet normal ', b'').split()).astype(np.float32)
                          for line in lines if b'facet normal ' in line])
      self.stl_data.normals = glm.array(np.array(normals)).reinterpret_cast(glm.float32)
      # points
      points = np.array([np.array(line.replace(b'vertex ', b'').split()).astype(np.float32)
                         for line in lines if b'vertex ' in line])
      # vertices & indices
      self._compute_vertices_indices(points=points)

  def _parse_binary_stl(self, stl_file: BufferedReader) -> None:
    """
    Nethod to parse the binary stl file.

    Argument:
      stl_file: BufferedReader
        stl file buffer object
    """

    num_triangles = read_unsigned_int(logger=self.logger, file_obj=stl_file)
    record_dtype = np.dtype([
                    ('normals', np.float32, (3,)),
                    ('vertex1', np.float32, (3,)),
                    ('vertex2', np.float32, (3,)),
                    ('vertex3', np.float32, (3,)),
                    ('attr', '<i2', (1,)),
                  ])
    data = np.fromfile(stl_file, dtype=record_dtype, count=num_triangles)

    normals = data['normals']
    vertex1 = data['vertex1']
    vertex2 = data['vertex2']
    vertex3 = data['vertex3']

    p = np.hstack((vertex1, vertex2, vertex3)).reshape(-1, 3)

    # normals
    self.stl_data.normals = glm.array(np.array(normals)).reinterpret_cast(glm.float32)

    # compute vertices & indices
    self._compute_vertices_indices(points=p)

  def parse_stl(self) -> None:
    """
    Method to parse stl file.
    """

    with open(self._file_path, 'rb') as stl_file:
      line = stl_file.readline(80).strip(b' ')
      if line == "":
        return # end of line
      if self._file_format == "ascii":
        self._parse_ascii_stl(stl_file=stl_file)
      elif self._file_format == "binary":
        self._parse_binary_stl(stl_file=stl_file)


if __name__ == '__main__':
  """For development purpose only"""
  try:
    robot_name = "KR16-R2010-2"
    stl_1 = STL(file_name=os.path.join(robot_name, "base.stl"))
    stl_2 = STL(file_name=os.path.join(robot_name, "link1.stl"))
    stl_3 = STL(file_name=os.path.join(robot_name, "link2.stl"))
    stl_4 = STL(file_name=os.path.join(robot_name, "link3.stl"))
    stl_5 = STL(file_name=os.path.join(robot_name, "link4.stl"))
    stl_6 = STL(file_name=os.path.join(robot_name, "link5.stl"))
    stl_7 = STL(file_name=os.path.join(robot_name, "link6.stl"))
    stl_1.logger.remove_log_files()
    stl_2.logger.remove_log_files()
    stl_3.logger.remove_log_files()
    stl_4.logger.remove_log_files()
    stl_5.logger.remove_log_files()
    stl_6.logger.remove_log_files()
    stl_7.logger.remove_log_files()
  except TypeError as err:
    print(err)
  else:
    stl_1.parse_stl()
    stl_2.parse_stl()
    stl_3.parse_stl()
    stl_4.parse_stl()
    stl_5.parse_stl()
    stl_6.parse_stl()
    stl_7.parse_stl()
    print(f"STL name: {stl_1.name}")
    print(f"STL Data normals: {stl_1.stl_data.normals[:5]}")
    print(
      f"STL Data vertices: {stl_1.stl_data.vertices[:24]} with length: {len(stl_1.stl_data.vertices)}")
    print(f"STL Data indices: {stl_1.stl_data.indices[:50]} with length: {len(stl_1.stl_data.indices)}")
    stl_2.parse_stl()
    print(f"STL name: {stl_2.name}")
    print(f"STL Data normals: {stl_2.stl_data.normals[:5]}")
    print(f"STL Data vertices: {stl_2.stl_data.vertices[:5]}")
    print(f"STL Data indices: {stl_2.stl_data.indices[:5]}")