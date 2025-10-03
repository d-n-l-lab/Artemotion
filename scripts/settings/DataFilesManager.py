# -*- coding: utf-8 -*- #
import os
import sys
import datetime

from PySide6.QtCore import QObject

try:
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings import PathManager
  from scripts.settings.Logger import Logger


class DataFilesManagerLogger(Logger):

  FILE_NAME = "data_files_manager"
  LOGGER_NAME = "DataFilesManagerLogger"


class DataFilesManager(QObject):

  # Constants
  DATA_DIR = "data"
  DAYS = 7 # Files older than DAYS get deleted

  def __init__(self, data_source):
    super(DataFilesManager, self).__init__()

    self.data_source = data_source
    self.data_file_path = None

    # Check if respective data directory exists, create if it doesn't
    self._create_data_dirs()

    # Check for old and/or empty files and delete them
    self._remove_files()

    # It helps to delete old log files
    DataFilesManagerLogger.remove_log_files()

  def _create_data_dirs(self): 
    # directory to save files
    try:
      if not os.path.exists(os.path.join(PathManager.get_project_dir_path(logger=DataFilesManagerLogger),
                                         self.DATA_DIR, self.data_source + '_data')):
        os.makedirs(os.path.join(PathManager.get_project_dir_path(logger=DataFilesManagerLogger),
                                 self.DATA_DIR, self.data_source + '_data'))
    except Exception:
      DataFilesManagerLogger.exception("Exception message:")

  def _remove_files(self):
    if not os.path.join(PathManager.get_project_dir_path(logger=DataFilesManagerLogger),
                        self.DATA_DIR, self.data_source + 'data'):
      DataFilesManagerLogger.info(
        f"{self.data_source + '_data'} direcory does not exist, cannot remove old/empty files"
      )

    # Compute time
    try:
      days_ago = datetime.datetime.timestamp(datetime.datetime.today() -
                                             datetime.timedelta(days=self.DAYS))
    except Exception:
      DataFilesManagerLogger.exception("Unable to compute days ago time:")

    # Get the data files older than the days ago and delete them
    try:
      data_dir = os.path.join(PathManager.get_project_dir_path(logger=DataFilesManagerLogger),
                              self.DATA_DIR, self.data_source + '_data')
      [os.remove(os.path.join(data_dir, f)) for f in os.listdir(data_dir)
       if not os.path.isdir(os.path.join(data_dir, f)) and self.data_source in f and
       os.path.getmtime(os.path.join(data_dir, f)) < days_ago or
       os.path.getsize(os.path.join(data_dir, f)) == 0 and
       os.path.getctime(os.path.join(data_dir, f)) <
       datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(seconds=1))]
    except Exception:
      DataFilesManagerLogger.exception("Unable to delete data files because:")

  def _get_time_str(self):
    curr_time = datetime.datetime.now().replace(microsecond=0)
    return curr_time.strftime("%Y-%m-%d_%H-%M-%S")

  def _create_data_file_path(self):
    if self.data_file_path is not None:
      DataFilesManagerLogger.info(f"File path {self.data_file_path} already exists")
      return
    data_source_dir = os.path.join(PathManager.get_project_dir_path(logger=DataFilesManagerLogger),
                                   self.DATA_DIR, self.data_source + '_data')
    if not os.path.exists(data_source_dir):
      DataFilesManagerLogger.info("Data directory does not exits, cannot write to file")

    # Create data file path
    self.data_file_path = os.path.join(data_source_dir, self.data_source + "_data_" +
                                       f"{self._get_time_str()}" + ".txt")
    DataFilesManagerLogger.info(f"File path created: {self.data_file_path}")

  def write_data_to_file(self, data={}):
    if len(data) == 0:
      DataFilesManagerLogger.info("Empty data, nothing to write to file")
      return
    if self.data_file_path is None:
      self._create_data_file_path()

    try:
      with open(self.data_file_path, 'a') as data_file:
        DataFilesManagerLogger.info(f"Writing {data} to {data_file}.")
        data_file.write("{{{0}}}".format(data['DATA']) + "\n")
    except Exception:
      DataFilesManagerLogger.exception("Unable to write to file:")


if __name__ == '__main__':
  # For development purpose only
  data_manager = DataFilesManager(data_source='opc')
  robot_data = {"DATA": "A1 113.145845695, A2 0.423001084226, A3 3.10049144981, A4 -88.4950650373, A5 113.099554284, A6 93.8310537669",
               "MSG_TYPE": "ROBOT_DATA"}
  camera_data = {"DATA": "F 0.262, I 0.495, Z 0.112",
                 "NAME": "mFIZ_0",
                 "MSG_TYPE": "CAMERA_DATA"}
  data_manager.write_data_to_file(data=camera_data)