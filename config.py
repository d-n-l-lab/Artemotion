## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various classes to manage configuration/settings of various
##              modules & submodules.
##
##############################################################################################
##
import os
import sys
import yaml

from dataclasses import dataclass, field
from typing import Any, AnyStr, Dict


def read_config_file(file_path: os.PathLike[AnyStr]) -> Any | None:
  """
  Function to read the config file i.e. yaml file and returns a string.

  Argument:
    file_path: os.PathLike[AnyStr]
      path of the config file

  Returns:
    config_file: Any | None
      data from config file
  """

  with open(file_path, 'r') as config_file:
    return config_file.read()


def parse_config_file(config_str: str) -> Dict | None:
  """
  Function to parse the config string i.e. a yaml string and returns a Dict.

  Argument:
    config_str: str
      configuration string

  Returns:
    config_dict: Dict | None
      Dict containing config keys & values
  """

  return yaml.safe_load(config_str)


@dataclass
class Config:

  """
  DataClass to manage configuration/settings.

  Parameters:
    config_dir: os.PathLike[AnyStr]
      directory path of requested config file
    config_file: str
      configuration file
  """

  config_dir: os.PathLike[AnyStr]
  config_file: str

  def __post_init__(self) -> None:
    if os.path.splitext(self.config_file)[-1] != ".yaml":
      self.config_file += ".yaml"
    self.file_path = os.path.join(self.config_dir, self.config_file)
    self.load()

  def __str__(self) -> str:
    return f"Configuration from file: {self.config_file}"

  def load(self) -> None:
    """
    Method to load the properties of self instance.
    """

    dict_config = parse_config_file(config_str=read_config_file(file_path=self.file_path))
    try:
      self.__dict__.update(dict_config)
    except Exception as exc:
      print(f"Unable to load configuration because: {exc}")
      sys.exit()


@dataclass
class AppConfig(Config):

  """
  DataClass to manage application wide configuration/settings derived from Config class.

  Parameters:
    config_dir: os.PathLike[AnyStr]
      directory path of requested config file
    config_file: str
      configuration file
  """

  config_dir: os.PathLike[AnyStr] = field(default=os.path.join("configs"))
  config_file: str = field(default="app_config.yaml")


@dataclass
class Config3D(Config):

  """
  DataClass to manage configuration/settings 3D engine/rendering derived from Config class.

  Parameters:
    config_dir: os.PathLike[AnyStr]
      directory path of requested config file
    config_file: str
      configuration file
  """

  config_dir: os.PathLike[AnyStr] = field(default=os.path.join("configs", "3d"))
  config_file: str = field(default="config.yaml")


@dataclass
class ConfigRobot(Config):

  """
  DataClass to manage configuration/settings 3D engine/rendering derived from Config class.

  Parameters:
    config_dir: os.PathLike[AnyStr]
      directory path of requested config file
    config_file: str
      configuration file
  """

  config_dir: os.PathLike[AnyStr] = field(default=os.path.join("configs", "robots"))
  config_file: str = field(default="KR16-R2010-2.yaml")


if __name__ == '__main__':
  config_app = AppConfig()
  print(f"AppConfig: {config_app.App}")
  config_3d = Config3D()
  print(f"Config3D: {config_3d.Meshes}")
  config_robot = ConfigRobot(config_file="Staubli-RX160.yaml")
  print(config_robot)
  dh_params = config_robot.Axes['a1']['dh-params']
  print(f"Config Robot: {dh_params}")