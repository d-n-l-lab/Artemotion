## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the OpenGL program to render 3D.
##
##############################################################################################
##
import glm

from OpenGL import GL as pygl
from typing import Any


class GLProgram:

  """
  Class to manage OpenGL program to render 3D.

  Arguments:
    logger: Logger
      logger class
  """

  def __init__(self, logger: Any) -> None:

    # logger
    self._logger = logger

    # Attributes
    self.shaders = ()
    self._id = 0

  def __del__(self):
    self.delete()

  @staticmethod
  def _check_program_status(program: pygl.GL_UNSIGNED_INT, logger: Any) -> Any:
    """
    Method to check the status of the program for any errors.

    Arguments:
      program: pygl.GL_UNSIGNED_INT
        id of the program
      logger: Any
        logger
    """

    if pygl.glGetProgramiv(program, pygl.GL_LINK_STATUS) != pygl.GL_TRUE:
      program_info_log = pygl.glGetProgramInfoLog(program)
      logger.info(f"Program link status: {program_info_log}")
      return program_info_log

  @staticmethod
  def _validation(program: pygl.GL_UNSIGNED_INT, logger: Any) -> bool:
    """
    Method to validate the created program.

    Arguments:
      program: pygl.GL_UNSIGNED_INT
        id of the created program
      logger: Any
        logger
    """

    try:
      GLProgram._check_program_status(program=program, logger=logger)
    except Exception:
      logger.exception("Failed to create program because:")
      return False

    return True

  def attach_shader(self, shader: pygl.GL_UNSIGNED_INT) -> None:
    """
    Method to cache the created shaders.

    Arguments:
      shader: pygl.GL_UNSIGNED_INT
        shader id
    """

    self.shaders += (shader,)

  def link(self) -> None:
    """
    Method to link a program to a shader.
    """

    try:
      self._id = pygl.glCreateProgram()
      for sh_id in self.shaders:
        pygl.glAttachShader(self._id, sh_id)
      pygl.glLinkProgram(self._id)
    except Exception:
      self._logger.exception("Unable to create & link program because:")

    if not GLProgram._validation(program=self._id, logger=self._logger):
      self._logger.warning(f"Could not link GL program!")

  @property
  def id(self) -> pygl.GL_UNSIGNED_INT:
    """
    Property: Program ID.
    """

    return self._id

  def delete(self) -> None:
    """
    Method to delete the GLProgram.
    """

    try:
      pygl.glDeleteProgram(self._id)
      self._id = 0
    except Exception:
      self._logger.exception("Unable to delete the GL program because:")
      pass

  def use(self) -> None:
    """
    Method to use/bind the GLProgram.
    """

    try:
      pygl.glUseProgram(self._id)
    except Exception:
      self._logger.exception("Unable to use the GL program because:")

  def release(self) -> None:
    """
    Method to release/unbind the GLProgram.
    """

    try:
      pygl.glUseProgram(0)
    except Exception:
      self._logger.exception("Unable to release the GL program because:")

  def get_attribute_location(self, name: str) -> Any:
    """
    Returns the attribute location i.e. position in the shader program.

    Arguments:
      name: str
        name of the attribute
    """

    return pygl.glGetAttribLocation(self._id, name)

  def set_attribute(self, name: str='', stride: int=0, offset: int=None) -> None:
    """
    Method to bind/set data to the relevant attribute.

    Arguments:
      name: str
        name of the attribute
      stride: int
        number of bytes in each record
      offset: int
        offset of the given attribute
    """

    if not name:
      return

    try:
      attr_loc = self.get_attribute_location(name=name)
      pygl.glVertexAttribPointer(attr_loc, 3, pygl.GL_FLOAT, pygl.GL_FALSE, stride, offset)
      pygl.glEnableVertexAttribArray(attr_loc)
    except Exception:
      self._logger.exception(f"Unable to bind/set data to the {name} attribute because:")

  def get_uniform_location(self, name: str) -> Any:
    """
    Returns the uniform location i.e. position in the shader program.

    Arguments:
      name: str
        name of the uniform
    """

    return pygl.glGetUniformLocation(self._id, name)

  def set_bool(self, name: str, value: bool) -> Any:
    """
    Method to set the value of a uniform of a boolean type.

    Arguments:
      name: str
        name of the uniform
      value: bool
        value to be set
    """

    if not isinstance(value, bool):
      return
    return pygl.glUniform1i(self.get_uniform_location(name=name), int(value))

  def set_int(self, name: str, value: int) -> Any:
    """
    Method to set the value of a uniform of a integer type.

    Arguments:
      name: str
        name of the uniform
      value: int
        value to be set
    """

    if not isinstance(value, int):
      return
    return pygl.glUniform1i(self.get_uniform_location(name=name), value)

  def set_float(self, name: str, value: float) -> Any:
    """
    Method to set the value of a uniform of a float type.

    Arguments:
      name: str
        name of the uniform
      value: float
        value to be set
    """

    if not isinstance(value, float):
      return
    return pygl.glUniform1f(self.get_uniform_location(name=name), value)

  def set_vec2(self, name: str, vec: glm.vec2) -> Any:
    """
    Method to set the value of a uniform of a vec2 type.

    Arguments:
      name: str
        name of the uniform
      value: glm.vec2
        value to be set
    """

    if not isinstance(vec, glm.vec2):
      return
    return pygl.glUniform2fv(self.get_uniform_location(name=name), 1, glm.value_ptr(vec))

  def set_vec3(self, name: str, vec: glm.vec3) -> Any:
    """
    Method to set the value of a uniform of a vec3 type.

    Arguments:
      name: str
        name of the uniform
      value: glm.vec3
        value to be set
    """

    if not isinstance(vec, glm.vec3):
      return
    return pygl.glUniform3fv(self.get_uniform_location(name=name), 1, glm.value_ptr(vec))

  def set_vec4(self, name: str, vec: glm.vec4) -> Any:
    """
    Method to set the value of a uniform of a vec4 type.

    Arguments:
      name: str
        name of the uniform
      value: glm.vec4
        value to be set
    """

    if not isinstance(vec, glm.vec4):
      return
    return pygl.glUniform4fv(self.get_uniform_location(name=name), 1, glm.value_ptr(vec))

  def set_mat2(self, name: str, mat: glm.mat2) -> Any:
    """
    Method to set the value of a uniform of a matrx2x2 type.

    Arguments:
      name: str
        name of the uniform
      value: glm.mat2
        value to be set
    """

    if not isinstance(mat, glm.mat2):
      return
    return pygl.glUniformMatrix2fv(self.get_uniform_location(name=name), 1, pygl.GL_FALSE,
                                   glm.value_ptr(mat))

  def set_mat3(self, name: str, mat: glm.mat3) -> Any:
    """
    Method to set the value of a uniform of a matrix3x3 type.

    Arguments:
      name: str
        name of the uniform
      value: glm.mat3
        value to be set
    """

    if not isinstance(mat, glm.mat3):
      return
    return pygl.glUniformMatrix3fv(self.get_uniform_location(name=name), 1, pygl.GL_FALSE,
                                   glm.value_ptr(mat))

  def set_mat4(self, name: str, mat: glm.mat4) -> Any:
    """
    Method to set the value of a uniform of a matrix4x4 type.

    Arguments:
      name: str
        name of the uniform
      value: glm.mat4
        value to be set
    """

    if not isinstance(mat, glm.mat4):
      return
    return pygl.glUniformMatrix4fv(self.get_uniform_location(name=name), 1, pygl.GL_FALSE,
                                   glm.value_ptr(mat))


if __name__ == '__main__':
  """For development purpose only"""
  program = GLProgram()
  print(f"GLProgram: {program}")
  program.link()