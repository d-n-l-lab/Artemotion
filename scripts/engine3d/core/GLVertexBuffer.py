## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including class managing the Vertex Buffer to render 3D.
##
##############################################################################################
##
import glm

from OpenGL import GL as pygl
from typing import Any


class GLVertexBuffer:

  """
  Class to manage OpenGL Vertex Buffer.

  Arguments:
    data: Any
      data to be rendered
    size: Any
      size of the data to be rendered in bytes
    logger: Any
      logger class
  """

  def __init__(self, logger: Any=None, data: glm.array=glm.array(glm.float32)) -> None:

    # logger
    self._logger = logger

    # attributes
    self._data = data

    try:
      self._vb_id = pygl.glGenBuffers(1)
      self.bind()
      self.set_data()
    except Exception:
      self._logger.exception("Unable to create a Vertex Buffer because:")

  def bind(self) -> None:
    """
    Method to bind the vertex buffer.
    """

    try:
      pygl.glBindBuffer(pygl.GL_ARRAY_BUFFER, self._vb_id)
    except Exception:
      self._logger.exception(f"Unable to bind Vertex Buffer with id={self._vb_id}")

  def unbind(self) -> None:
    """
    Method to unbind the vertex buffer.
    """

    try:
      pygl.glBindBuffer(pygl.GL_ARRAY_BUFFER, 0)
    except Exception:
      self._logger.exception(f"Unable to unbind Vertex Buffer with id={self._vb_id}")

  def set_data(self) -> None:
    """
    Method to populate vertex buffer with the data.
    """

    try:
      pygl.glBufferData(
        pygl.GL_ARRAY_BUFFER, self._data.nbytes, self._data.ptr, pygl.GL_STATIC_DRAW
      )
    except Exception:
      self._logger.exception(f"Unable to assign data to Vertex Buffer with id={self._vb_id}")

  @property
  def id(self) -> int:
    """
    Vertex Buffer ID property.

    Arguments:
      id: int
        vertex buffer id
    """

    return self._vb_id

  @property
  def data(self) -> glm.array:
    """
    Vertex Buffer data property.

    Returns:
      vertex buffer data array
    """

    return self._data

  @data.setter
  def data(self, value: glm.array) -> None:
    """
    Vertex Buffer data property.

    Returns:
      vertex buffer data array
    """

    if not isinstance(value, glm.array):
      return

    self._data = value

  def __delete__(self):
    """
    Magic method to delete the vertex buffer.
    """

    try:
      pygl.glDeleteBuffers(1, self._vb_id)
    except Exception:
      self._logger.exception(f"Unable to delete Vertex Buffer with id={self._vb_id}")


if __name__ == '__main__':
  """For development purpose only"""
  # Data
  _data = glm.array(glm.float32,
                   -0.5, -0.5, 0.0,
                   0.5, -0.5, 0.0,
                   0.5, 0.5, 0.0,
                   -0.5, 0.5, 0.0)
  vertex_buffer = GLVertexBuffer(data=_data, logger=None)