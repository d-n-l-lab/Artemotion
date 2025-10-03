# -*- coding: utf-8 -*- #
import os
import sys

from typing import Any, AnyStr, Union

try:
  from config import Config3D
except:
  # For the development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from config import Config3D


_config_3d = Config3D()

def get_project_root_path(logger: Any) -> Union[os.PathLike[AnyStr], None]:
  try:
    return os.path.dirname(os.path.abspath('app.py'))
  except Exception:
    logger.exception("Unable to get base path because:")
    return None

def get_project_dir_path(logger: Any) -> Union[os.PathLike[AnyStr], None]:
  try:
    if hasattr(sys, '_MEIPASS'):
      # App launched via Pyinstaller
      return os.path.join(os.path.expanduser('~'), 'artemotion')
    else:
      # For development purpose
      return os.path.dirname(os.path.abspath('app.py'))
  except Exception:
    logger.execption("Unable to get project directory because:")
    return None

def get_image_path(logger: Any, image_file: os.PathLike[AnyStr]) -> Union[os.PathLike[AnyStr], None]:
  """ Get absolute path to images, work for dev and Pyinstaller. """
  try:
    project_dir = get_project_root_path(logger=logger)
    if hasattr(sys, '_MEIPASS'):
      # App launched via Pyinstaller
      return os.path.join(project_dir, os.path.join('resources', 'images', image_file))
    else:
      # For development purpose
      return os.path.join(project_dir,
                          os.path.join('scripts', 'ui', 'resources', 'images', image_file))
  except Exception:
    logger.exception(f"Unable to get the {image_file} path because:")
    return None

def get_qss_path(logger: Any, qss_file: os.PathLike[AnyStr]) -> Union[os.PathLike[AnyStr], None]:
  """ Get absolute path to PySide Stylesheet, works for dev and Pyinstaller. """
  try:
    project_dir = get_project_root_path(logger=logger)
    if hasattr(sys, '_MEIPASS'):
      return os.path.join(project_dir, os.path.join('resources', 'stylesheets', qss_file))
    else:
      return os.path.join(project_dir,
                          os.path.join('scripts', 'ui', 'resources', 'stylesheets', qss_file))
  except Exception:
    logger.exception(f"Unable to get {qss_file} path because:")
    return None

def get_config_path(logger: Any, config_file: os.PathLike[AnyStr]=None) -> Union[os.PathLike[AnyStr], None]:
  """ Get absolute path to config files or configs dir, works for dev and Pyinstaller. """
  try:
    project_root = get_project_root_path(logger=logger)
    if config_file is None:
      return os.path.join(project_root, os.path.join('configs'))
    else:
      return os.path.join(project_root, os.path.join('configs', config_file))
  except Exception:
    logger.exception("Unable to get configs path because:")
    return None

def get_shader_path(logger: Any, shader_file: os.PathLike[AnyStr]) -> Union[os.PathLike[AnyStr], None]:
  """ Get absolute path to shader files or shaders dir, works for dev and Pyinstaller. """
  try:
    project_dir = get_project_root_path(logger=logger)
    if hasattr(sys, '_MEIPASS'):
      return os.path.join(project_dir, os.path.join('resources', 'shaders', shader_file))
    else:
      return os.path.join(project_dir,
                          os.path.join('scripts', 'ui', 'resources', 'shaders', shader_file))
  except:
    logger.exception(f"Unable to get {shader_file} path because:")
    return None

def get_3d_file_path(logger: Any, file_name: os.PathLike[AnyStr]) -> Union[os.PathLike[AnyStr], None]:
  """ Get absolute path to 3d files or obj dir, works for dev and Pyinstaller. """
  if os.path.splitext(os.path.basename(file_name))[-1].lower() not in _config_3d.Meshes['files_ext']:
    logger.warning(f"Invalid {file_name} file received")
    return None

  try:
    project_dir = get_project_root_path(logger=logger)
    if hasattr(sys, '_MEIPASS'):
      return os.path.join(project_dir, os.path.join('resources', 'meshes', file_name))
    else:
      return os.path.join(
        project_dir, os.path.join('scripts', 'ui', 'resources', 'meshes', file_name)
      )
  except:
    logger.exception(f"Unable to get {file_name} path because:")
    return None


if __name__ == '__main__':
  """For development purpose only"""
  print(get_project_root_path(logger=None))
  print(get_project_dir_path(logger=None))
  print(get_config_path(logger=None, config_file='fromKuka.xml'))
  print(get_qss_path(logger=None, qss_file='AnimDataWidget.qss'))
  print(get_shader_path(logger=None, shader_file='grid.frag'))
  print(get_3d_file_path(logger=None, file_name='robot.stl'))
  print(get_3d_file_path(logger=None, file_name='robot.obj'))