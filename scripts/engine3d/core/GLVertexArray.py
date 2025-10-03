## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including class managing the Vertex Array Object to render 3D.
##
##############################################################################################
##
from OpenGL import GL as pygl
from typing import Any


class GLVertexArray:

  """
  Class to manage OpenGL Vertex Buffer.

  Arguments:
    logger: Any
      logger class
  """

  def __init__(self, logger: Any) -> None:

    self._logger = logger

    try:
      self._va_id = pygl.glGenVertexArrays(1)
    except Exception:
      self._logger.exception("Unable to create a Vertex Array because:")
    else:
      self.bind()

  def bind(self) -> None:
    """
    Method to unbind the vertex array.    
    """

    try:
      pygl.glBindVertexArray(self._va_id)
    except Exception:
      self._logger.exception(f"Unable to bind Vertex Array with id={self._va_id}")

  def unbind(self):
    """
    Method to unbind the vertex array.    
    """

    try:
      pygl.glBindVertexArray(0)
    except Exception:
      self._logger.exception(f"Unable to unbind Vertex Array with id={self._va_id}")

  @property
  def id(self) -> int:
    """
    Vertex Array ID property.

    Arguments:
      id: int
        vertex array id
    """

    return self._va_id

  def __delete__(self):
    """
    Magic method to delete the vertex array.
    """

    try:
      pygl.glDeleteVertexArrays(1, self._va_id)
    except Exception:
      self._logger.exception(f"Unable to delete Vertex Array with id={self._va_id}")


if __name__ == '__main__':
  """For development purpose only"""
  vertex_array = GLVertexArray()