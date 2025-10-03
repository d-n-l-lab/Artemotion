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

try:
  from scripts.settings.Logger import Logger
  from scripts.engine3d.core.GLShader import GLShader
  from scripts.engine3d.core.GLProgram import GLProgram
  from scripts.engine3d.core.GLVertexArray import GLVertexArray
  from scripts.engine3d.core.GLVertexBuffer import GLVertexBuffer
  from scripts.engine3d.core.GLElementBuffer import GLElementBuffer
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.engine3d.core.GLShader import GLShader
  from scripts.engine3d.core.GLProgram import GLProgram
  from scripts.engine3d.core.GLVertexArray import GLVertexArray
  from scripts.engine3d.core.GLVertexBuffer import GLVertexBuffer
  from scripts.engine3d.core.GLElementBuffer import GLElementBuffer


class DummyLogger(Logger):

  pass


class Renderable:

  """
  Parent class to manage a renderable object.

  Keyword Arguments:
    sh_file: str
      name of the shader file
    logger: Logger
      logger class
  """

  def __init__(self, sh_file: str, **kwargs) -> None:
    super(Renderable, self).__init__(**kwargs)

    # logger
    try:
      self._logger = kwargs['logger']
    except Exception:
      self.__del__()
      return

    # array objects
    self.vao = self.vbo = self.ebo = self.ibo = None

    # parameters
    self.program = None
    self.shaders = []
    try:
      self._shader_file = sh_file
    except Exception:
      self._logger.exception("Unable to instantiate Renderable because:")
      self.__del__()
      return

    # vertices & indices
    self.indices = glm.array(glm.int32)
    self.vertices = glm.array(glm.float32)

    # Transformations
    self.model = glm.mat4(1)

    # Initialized flag (set this flag in sub-class after initialization)
    self._initialized = False

  def __del__(self) -> None:
    """
    Method to delete the objects.
    """

    self.delete()

  def init_gl(self) -> None:
    """
    Method to initialize the OpenGL to render. Re-implement this method in subclass if required.
    """

    # Create & compile shader
    shaders = GLShader(sh_name=self._shader_file)
    shaders.compile()
    self.shaders = shaders.get_id()

    # Create & Link program
    self.program = GLProgram(logger=self._logger)
    for shader in self.shaders:
      self.program.attach_shader(shader=shader)
    self.program.link()
    shaders.delete()

    # Create & bind vertex array object
    self.vao = GLVertexArray(logger=self._logger)

    # Create & bind buffer objects
    # Vertex buffer
    self.vbo = GLVertexBuffer(data=self.vertices, logger=self._logger)

    # Element/Index buffer
    if len(self.indices) > 0:
      self.ebo = GLElementBuffer(data=self.indices.ptr, size=self.indices.nbytes,
                                 logger=self._logger)

  @property
  def initialized(self) -> bool:
    """
    Property: Initialized
    """

    return self._initialized

  def render(self, primitive: pygl.GLenum=pygl.GL_TRIANGLES) -> None:
    """
    Method to render 3D. Re-implement this method in subclass.

    Argument:
      primitive: pygl.GLenum
        OpenGL drawing primitive
    """

    # pygl.glBindVertexArray(self.vao)

    self.vao.bind()
    self.program.use()
    if self.ebo:
      pygl.glDrawElements(primitive, len(self.indices), pygl.GL_UNSIGNED_INT, None)
    else:
      pygl.glDrawArrays(primitive, 0, len(self.vertices)//3)
    self.program.release()

  def update_data(self) -> None:
    """
    Method to update data in the vertex buffer object.
    """

    self.vao.bind()
    self.vbo.bind()
    self.vbo.data = self.vertices
    self.vbo.set_data()
    self.vbo.unbind()
    self.vao.unbind()

  def set_model(self) -> None:
    """
    Method to set the model matrix.
    """

    # model matrix
    self.program.use()
    self.program.set_mat4(name='umodel', mat=self.model)
    self.program.release()

  def set_view(self, view: glm.mat4) -> None:
    """
    Method to set the view matrix.

    Argument:
      model: glm.mat4
        view matrix
    """

    # view matrix
    self.program.use()
    self.program.set_mat4(name='uview', mat=view)
    self.program.release()

  def set_projection(self, projection: glm.mat4) -> None:
    """
    Method to set the projection matrix.

    Argument:
      model: glm.mat4
        projection matrix
    """

    # projection matrix
    self.program.use()
    self.program.set_mat4(name='uproj', mat=projection)
    self.program.release()

  def delete(self) -> None:
    """
    Method to delete vertex buffer objects.
    """

    try:
      pygl.glDeleteVertexArrays(1, self.vao)
      del self.vbo
      self.vao, self.vbo, self.ebo, self.ibo = None
    except:
      pass


if __name__ == '__main__':
  """For development purpose only"""
  renderable = Renderable(sh_file='room')