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


class GLCamera:

  view_config = {"yaw": 90.0, "roll": 0.0, "pitch": 0.0, "cam_pos": glm.vec3(5, 5, 5),
                 "cam_spd": 0.75, "mouse_sens": 0.1, "world_up": glm.vec3(0, 1, 0)}
  proj_config = {"fov": 45.0, "width": 800, "height": 600, "near_plane": 0.1, "far_plane": 1000.0}

  def __init__(self, logger: Logger=DummyLogger) -> None:

    # logger
    self._logger = logger
    # setups
    self.setup_view_space(**self.view_config)
    self.setup_projection(**self.proj_config)

    # Up
    self.up = self.world_up
    # Target
    self.cam_target = glm.vec3(0)

    # Matrices
    self.view = glm.mat4(1)
    self.perspective = glm.mat4(1)
    self.orthographic = glm.mat4(1)

  def setup_view_space(self, **kwargs: Any) -> None:
    if 'yaw' in kwargs: self.yaw = kwargs['yaw']
    if 'roll' in kwargs: self.roll = kwargs['roll']
    if 'pitch' in kwargs: self.pitch = kwargs['pitch']
    if 'cam_pos' in kwargs: self.cam_pos = kwargs['cam_pos']
    if 'cam_spd' in kwargs: self.cam_spd = kwargs['cam_spd']
    if 'world_up' in kwargs: self.world_up = kwargs['world_up']
    if 'mouse_sens' in kwargs: self.mouse_sens = kwargs['mouse_sens']

  def update_view_space(self) -> None:
    self.view = glm.lookAt(self.cam_pos, self.cam_target, self.up)

  def update_cam_pos(self, cam_pos: glm.vec3) -> None:
    self.cam_pos = cam_pos

  def update_target_pos(self, cam_target: glm.vec3) -> None:
    self.cam_target = cam_target

  def get_view_matrix(self) -> glm.mat4:
    return self.view

  def get_orthographic_projection(self) -> glm.mat4:
    return self.orthographic

  def get_perspective_projection(self) -> glm.mat4:
    return self.perspective

  def setup_projection(self, **kwargs) -> None:
    if 'fov' in kwargs: self.fov = kwargs['fov']
    if 'width' in kwargs: self.width = kwargs['width']
    if 'height' in kwargs: self.height = kwargs['height']
    if 'far_plane' in kwargs: self.far_plane = kwargs['far_plane']
    if 'near_plane' in kwargs: self.near_plane = kwargs['near_plane']

  def set_orthographic_projection(self, **kwargs: Any) -> None:
    self.setup_projection(**kwargs)
    self.orthographic = glm.ortho(0.0, self.width, 0.0, self.height, self.near_plane,
                                  self.far_plane)

  def set_perspective_projection(self, **kwargs: Any) -> None:
    self.setup_projection(**kwargs)
    self.perspective = glm.perspective(glm.radians(self.fov), self.width/self.height,
                                       self.near_plane, self.far_plane)


class GLTargetCamera(GLCamera):

  def __init__(self, logger: Logger = DummyLogger) -> None:
    super(GLTargetCamera, self).__init__(logger)

  def rotate_around_target_view(self, target: glm.vec3, dx: float, dy: float) -> None:
    view = glm.lookAt(self.cam_pos, self.cam_target, self.up)

    pivot = glm.vec3(view * glm.vec4(target.x, target.y, target.z, 1))
    axis = glm.vec3(-dy, -dx, 0)
    angle = glm.length(glm.vec2(dx, dy))

    rot = glm.rotate(glm.mat4(1), angle, axis)
    rot_pivot = glm.translate(glm.mat4(1), pivot) * rot * glm.translate(glm.mat4(1), -pivot)
    new_view = rot_pivot * view

    c = glm.inverse(new_view)
    target_dist = glm.length(self.cam_target - self.cam_pos)
    self.cam_pos = glm.vec3(c[3])
    self.cam_target = self.cam_pos - glm.vec3(c[2]) * target_dist
    self.up = glm.vec3(c[1])

    # View Matrix
    self.update_view_space()

  def rotate_around_target_world(self, target: glm.vec3, dx: float, dy: float) -> None:
    view = glm.lookAt(self.cam_pos, self.cam_target, self.up)

    pivot = target
    axis = glm.vec3(-dy, -dx, 0)
    angle = glm.length(glm.vec2(dx, dy))

    rot = glm.rotate(glm.mat4(1), angle, axis)
    rot_pivot = glm.translate(glm.mat4(1), pivot) * rot * glm.translate(glm.mat4(1), -pivot)
    new_view = rot_pivot * view

    c = glm.inverse(new_view)
    target_dist = glm.length(self.cam_target - self.cam_pos)
    self.cam_pos = glm.vec3(c[3])
    self.cam_target = self.cam_pos - glm.vec3(c[2]) * target_dist
    self.up = glm.vec3(c[1])

    # View Matrix
    self.update_view_space()

  def rotate_around_origin(self, dx: float, dy: float) -> None:
    self.rotate_around_target_view(target=glm.vec3(0), dx=dx, dy=dy)

  def rotate_around_target(self, target: glm.vec3, dx: float, dy: float) -> None:
    self.rotate_around_target_view(target=target, dx=dx, dy=dy)

  def pan(self, new_pos: glm.vec2, old_pos: glm.vec2, depth: float) -> None:
    wnd_from = glm.vec3(old_pos[0], old_pos[1], float(depth))
    wnd_to = glm.vec3(new_pos[0], new_pos[1], float(depth))

    vp_rect = glm.vec4(0, 0, self.width, self.height)
    world_from = glm.unProject(wnd_from, self.view, self.perspective, vp_rect)
    world_to = glm.unProject(wnd_to, self.view, self.perspective, vp_rect)

    world_vec = world_to - world_from

    self.cam_pos = self.cam_pos - world_vec
    self.cam_target = self.cam_target - world_vec
    self.update_view_space()

  def zoom(self, amount: float) -> None:
    delta = -amount * 0.1
    self.cam_pos = self.cam_target + (self.cam_pos - self.cam_target) * (delta + 1)
    self.update_view_space()

  def zoom_towards_cursor(self, **kwargs) -> None:
    x = kwargs['x'] # cursor x position
    y = kwargs['y'] # cursor y position
    v = kwargs['v'] # viewport

    pt_wnd = glm.vec3(x, v.w - y, 1.0)
    pt_world = glm.unProject(pt_wnd, self.view, self.perspective, v)
    ray_cursor = glm.normalize(pt_world - self.cam_pos)

    self.cam_pos += (-kwargs['delta'] * ray_cursor)
    self.cam_target += (-kwargs['delta'] * ray_cursor)

    self.update_view_space()


if __name__ == '__main__':
  """For development purpose only"""
  gl_target_cam = GLTargetCamera()
  gl_target_cam._logger.remove_log_files()
  gl_target_cam.set_orthographic_projection()
  gl_target_cam.set_perspective_projection()
  gl_target_cam.update_cam_pos(glm.vec3(15))
  gl_target_cam.update_target_pos(glm.vec3(-1))
  gl_target_cam.update_view_space()