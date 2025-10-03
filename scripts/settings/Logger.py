# -*- coding: utf-8 -*- #
import os
import sys
import logging
import datetime

from typing import Any, Dict, Literal

try:
  from scripts.settings import PathManager
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings import PathManager


class Logger:

  DAYS = 7 # Files older than DAYS get deleted

  LOGS_DIR = "logs"
  FILE_NAME = "root"
  LOGGER_NAME = "Root"
  LEVEL_DEFAULT = logging.DEBUG
  LOG_FORMAT = "[%(asctime)s.%(msecs)03d] {%(filename)30s:%(lineno)4s} (%(name)25s:%(levelname)8s) - %(message)s"

  _logger_obj = None
  _log_path = None

  @classmethod
  def logger_obj(cls) -> Any:
    if cls.logger_exists():
      cls._logger_obj = logging.getLogger(cls.LOGGER_NAME)
    else:
      cls._logger_obj = logging.getLogger(cls.LOGGER_NAME)
      cls._logger_obj.setLevel(cls.LEVEL_DEFAULT)

      formatter = logging.Formatter(fmt=cls.LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

      # Stream Handler
      stream_handler = logging.StreamHandler(sys.stdout)
      stream_handler.setFormatter(formatter)
      cls._logger_obj.addHandler(stream_handler)

      # File Handler
      # cls._log_path = os.path.join(os.path.abspath(cls.LOGS_DIR), cls.LOGGER_NAME)
      cls._log_path = os.path.join(PathManager.get_project_dir_path(logger=cls),
                                   cls.LOGS_DIR, cls.LOGGER_NAME)
      file_handler = logging.FileHandler(os.path.join(cls._log_path, cls.get_log_file()))
      file_handler.setFormatter(formatter)
      file_handler.setLevel(logging.WARNING)
      cls._logger_obj.addHandler(file_handler)

    return cls._logger_obj

  @classmethod
  def get_log_file(cls) -> str:
    # Create directory if doesn't exist
    if not os.path.exists(cls._log_path):
      os.makedirs(cls._log_path)

    time_stamp = datetime.datetime.now().replace(microsecond=0)
    filename_with_time = cls.FILE_NAME + "_" + time_stamp.strftime('%Y-%m-%d_%H-%M-%S') + ".log"

    return filename_with_time

  @classmethod
  def logger_exists(cls) -> Literal:
    return cls.LOGGER_NAME in logging.Logger.manager.loggerDict.keys()

  @classmethod
  def remove_log_files(cls) -> None:
    # Compute time
    try:
      days_ago = datetime.datetime.timestamp(datetime.datetime.today() - datetime.timedelta(days=cls.DAYS))
    except Exception:
      cls.exception("Unable to compute days ago time")

    # Get the log files older than the days ago and delete them
    try:
      logs_dir = os.path.join(PathManager.get_project_dir_path(logger=cls),
                              cls.LOGS_DIR, cls.LOGGER_NAME)
      if os.path.exists(logs_dir):
        [os.remove(os.path.join(logs_dir, f)) for f in os.listdir(logs_dir)
         if not os.path.isdir(os.path.join(logs_dir, f)) and
         os.path.getmtime(os.path.join(logs_dir, f)) < days_ago or
         os.path.getsize(os.path.join(logs_dir, f)) == 0 and
         os.path.getctime(os.path.join(logs_dir, f)) <
         datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(seconds=1))]
    except Exception:
      cls.exception("Unable to delete log files because")

  @classmethod
  def set_level(cls, level: Any) -> None:
    lg = cls.logger_obj()
    lg.setLevel(level)

  @classmethod
  def debug(cls, msg: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
    kwargs.setdefault('stacklevel', 2)
    lg = cls.logger_obj()
    lg.debug(msg, *args, **kwargs)

  @classmethod
  def info(cls, msg: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
    kwargs.setdefault('stacklevel', 2)
    lg = cls.logger_obj()
    lg.info(msg, *args, **kwargs)

  @classmethod
  def warning(cls, msg: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
    kwargs.setdefault('stacklevel', 2)
    lg = cls.logger_obj()
    lg.warning(msg, *args, **kwargs)

  @classmethod
  def error(cls, msg: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
    kwargs.setdefault('stacklevel', 2)
    lg = cls.logger_obj()
    lg.error(msg, *args, **kwargs)

  @classmethod
  def critical(cls, msg: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
    kwargs.setdefault('stacklevel', 2)
    lg = cls.logger_obj()
    lg.critical(msg, *args, **kwargs)

  @classmethod
  def log(cls, level, msg: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
    kwargs.setdefault('stacklevel', 2)
    lg = cls.logger_obj()
    lg.log(level, msg, *args, **kwargs)

  @classmethod
  def exception(cls, msg: str, *args: Any, **kwargs: Dict[str, Any]) -> None:
    kwargs.setdefault('stacklevel', 3)
    lg = cls.logger_obj()
    lg.exception(msg, *args, **kwargs)


if __name__ == '__main__':
  # Only for development purpose
  logger = Logger()
  logger.set_level(5)
  logger.debug("Debug Message")
  logger.info("Info Message")
  logger.warning("Warning Message")
  logger.error("Error Message")
  logger.critical("Critical Message")
  logger.log(5, "Log Message")

  try:
    a = []
    b = a[0]
  except:
    logger.exception("Exception Message:")
  logger.remove_log_files()