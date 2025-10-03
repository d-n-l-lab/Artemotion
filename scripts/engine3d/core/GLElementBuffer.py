## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
##
##############################################################################################
##
import os
import sys
import glm

from OpenGL import GL as pygl
from typing import Any

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger


class DummyLogger(Logger):

  pass


class GLElementBuffer:

  def __init__(self, data: Any, size: Any, logger: Logger=DummyLogger) -> None:

    self._logger = logger
    try:
      self.ib_id = pygl.glGenBuffers(1)
      pygl.glBindBuffer(pygl.GL_ELEMENT_ARRAY_BUFFER, self.ib_id)
      pygl.glBufferData(pygl.GL_ELEMENT_ARRAY_BUFFER, size, data, pygl.GL_STATIC_DRAW)
    except Exception:
      self._logger.exception("Unable to create a Index Buffer because:")

  def bind(self) -> None:
    try:
      pygl.glBindBuffer(pygl.GL_ELEMENT_ARRAY_BUFFER, self.ib_id)
    except Exception:
      self._logger.exception(f"Unable to bind Index Buffer with id={self.ib_id}")

  def unbind(self) -> None:
    try:
      pygl.glBindBuffer(pygl.GL_ELEMENT_ARRAY_BUFFER, 0)
    except Exception:
      self._logger.exception(f"Unable to unbind Index Buffer with id={self.ib_id}")

  def __delete__(self):
    try:
      pygl.glDeleteBuffers(1, self.ib_id)
    except Exception:
      self._logger.exception(f"Unable to delete Index Buffer with id={self.ib_id}")


if __name__ == '__main__':
  """For development purpose only"""
  # Data
  data = glm.array(glm.int32,
                   0, 1, 2,
                   2, 3, 0)
  index_buffer = GLElementBuffer(data=data.ptr, size=data.nbytes)
  index_buffer._logger.remove_log_files()