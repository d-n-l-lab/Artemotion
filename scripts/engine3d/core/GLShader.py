## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2021
##
##############################################################################################
##
import os
import sys

from OpenGL import GL as pygl
from typing import Any, Dict, List, Union

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger


class GLShaderLogger(Logger):

  FILE_NAME = "gl_shader"
  LOGGER_NAME = "GLShaderLogger"


class GLShader:

  def __init__(self, sh_name: str='') -> None:

    self._shaders = []
    self.shader_code = {}
    self.sh_name = sh_name

    self._parse_shaders_from_file(self.sh_name)

    # It helps to delete old/empty log files
    GLShaderLogger.remove_log_files()

  def __str__(self) -> str:
    return f"Processing Shader from file: {self.sh_name}"

  def __del__(self) -> None:
    self.delete()

  def _parse_shaders_from_file(self, sh_name: str) -> Union[Dict, None]:
    self.shader_code[sh_name] = {}
    try:
      # Get the shader file
      vert_sh_file = PathManager.get_shader_path(logger=GLShaderLogger,
                                                 shader_file=sh_name + '.vert')
      with open(vert_sh_file) as file:
        self.shader_code[sh_name][pygl.GL_VERTEX_SHADER] = file.read()
    except Exception:
      GLShaderLogger.exception(f"Unable to read the {vert_sh_file} vertex shader file because:")
      pass

    try:
      # Get the shader file
      frag_sh_file = PathManager.get_shader_path(logger=GLShaderLogger,
                                                 shader_file=sh_name + '.frag')
      with open(frag_sh_file) as file:
        self.shader_code[sh_name][pygl.GL_FRAGMENT_SHADER] = file.read()
    except Exception:
      GLShaderLogger.exception(f"Unable to read the {frag_sh_file} fragment shader file because:")
      pass

  def _check_shader_status(self, shader: pygl.GL_UNSIGNED_INT) -> Any:
    if pygl.glGetShaderiv(shader, pygl.GL_COMPILE_STATUS) != pygl.GL_TRUE:
      shader_info_log = pygl.glGetShaderInfoLog(shader)
      self.delete()
      GLShaderLogger.info(f"GLShader compile status: {shader_info_log.decode()}")
      return shader_info_log.decode()

  def _compile_shader(self, shader_code: str, shader_type: pygl.GL_UNSIGNED_INT) -> Any:
    shader_id = 0
    try:
      shader_id = pygl.glCreateShader(shader_type)
      pygl.glShaderSource(shader_id, shader_code)
      pygl.glCompileShader(shader_id)
    except Exception:
      GLShaderLogger.exception("Unable to create & compile shader because:")

    s = self._check_shader_status(shader=shader_id)
    if s:
      GLShaderLogger.error(s)

    return shader_id

  def compile(self) -> Any:
    for t in self.shader_code[self.sh_name].keys():
      try:
        sh_id = self._compile_shader(shader_code=self.shader_code[self.sh_name][t],
                                     shader_type=t)
        if sh_id > 0:
          self._shaders.append(sh_id)
      except Exception:
        GLShaderLogger.exception(f"Failed to compile {t} shader")

  def get_id(self) -> List:
    return self._shaders

  def delete(self, program_id: pygl.GL_UNSIGNED_INT=0) -> None:
    try:
      for sh_id in self._shaders:
        if program_id > 0:
          pygl.glDetachShader(program_id, sh_id)
        pygl.glDeleteShader(sh_id)
      self._shaders.clear()
    except Exception:
      GLShaderLogger.exception("Unable to delete shader because:")


if __name__ == '__main__':
  """For development purpose only"""
  shader = GLShader(sh_name='grid')
  GLShaderLogger.info(f"GLShader: {shader}")
  shader.compile()