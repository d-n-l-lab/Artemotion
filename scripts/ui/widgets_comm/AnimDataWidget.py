## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the Animation Data widget with the SQL
##              database.
##
##############################################################################################
##
import os
import sys
import json

from collections import deque
from typing import Any, List, Tuple, Union

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import (QModelIndex, QObject, QPersistentModelIndex, QSettings, QSize,
                            QThread, QTimer, Signal, Qt)
from PySide6.QtWidgets import (QApplication, QFrame, QStackedWidget, QWidget, QFileDialog,
                               QAbstractItemView, QTableView, QHBoxLayout, QVBoxLayout, QLayout,
                               QSpacerItem, QSizePolicy)
from PySide6.QtSql import QSqlQuery, QSqlRelationalTableModel, QSqlTableModel

try:
  from scripts.settings.Logger import Logger
  from scripts.comm.DatabaseNodeStream import DatabaseNodeStream
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget, LineEditWidget, PushButtonWidget
except:
  # For the development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.comm.DatabaseNodeStream import DatabaseNodeStream
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget, LineEditWidget, PushButtonWidget


class AnimDataUILogger(Logger):

  FILE_NAME = "ui_anim_data"
  LOGGER_NAME = "UIAnimDataLogger"


class AnimDataWdgtFunctionality:

  """
  Class to manage Animation Data Widget functionality.

  Keyword Arguments:
    parent : QWidget
      parent widget
    logger : Logger
      Logger class
  """

  def __init__(self, **kwargs) -> None:
    super(AnimDataWdgtFunctionality, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    # Database tables
    self.database_tables = {}
    # Animation Data file
    self.animation_data_file = None

  def read_settings(self) -> None:
    """
    Method responsible to read the Widget settings. It should be derived in sub class.
    """

    pass

  def setup_db_tables(self, db_tables: dict={}) -> None:
    if len(db_tables) == 0:
      AnimDataUILogger.warning("No table names received")
      return

    self.database_tables = db_tables


class AnimDataWidget(AnimDataWdgtFunctionality, QFrame):

  """
  Class to manage the main Animation Data Widget derived from AnimDataWdgtFunctionality &
  QFrame classes.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      widget settings
    logger: Logger)
      logger class
  """

  publish_animation_point = Signal(list)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    kwargs['logger'] = AnimDataUILogger
    super(AnimDataWidget, self).__init__(**kwargs)

    # Assign attributes to the frame
    self.setObjectName(u"animDataWidget")
    self.setWindowTitle(u"Animation Data")
    if self._parent is None:
      self.resize(QSize(500, 392))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Get the application settings
    self._settings = kwargs.get('settings', None)
    if self._settings is not None:
      self.read_settings()

    self.init_UI()

    # It helps to delete old/empty log files
    AnimDataUILogger.remove_log_files()

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create main layout
    animDataWdgtMainLayout = QVBoxLayout(self)
    animDataWdgtMainLayout.setObjectName(u"animDataWdgtMainLayout")

    # Create Layouts
    self._create_top_vertical_layout()
    verticalSpacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
    self._create_anim_data_stacked_wdgt()

    # Add widgets to the layout & set margins
    animDataWdgtMainLayout.addLayout(self.animDataTopVertLayout)
    animDataWdgtMainLayout.addItem(verticalSpacer)
    animDataWdgtMainLayout.addWidget(self.animDataStackedWidget)
    animDataWdgtMainLayout.setContentsMargins(20, 10, 20, 10)
    animDataWdgtMainLayout.setSpacing(10)

    # Connections
    self._create_local_connect()
    self._create_stacked_wdgt_pages_connect()

    self._on_page_select_button_clicked() # To set Stacked Widget index
    self._on_stacked_widget_page_changed()

  def _create_stacked_wdgt_ctrl_btns_layout(self) -> None:
    """
    Method to create a layout to manage the selection buttons of the stacked widget.
    """

    # Create buttons horizontal layout
    stackedWdgtsBtnsHorizLayout = QHBoxLayout()
    stackedWdgtsBtnsHorizLayout.setObjectName(u"stackedWdgtsBtnsHorizLayout")

    # Animation Data from DB Button
    self.animDataFromDBBttn = PushButtonWidget(parent=self, logger=self._logger,
                                               text=u"From Database", type="left_button",
                                               minsize=QSize(0, 20))
    self.animDataFromDBBttn.setObjectName(u"animDataFromDBBttn")

    # Animation Data from file Button
    self.animDataFromFileBttn = PushButtonWidget(parent=self, logger=self._logger,
                                                 text=u"From File", type="right_button",
                                                 minsize=QSize(0, 20))
    self.animDataFromFileBttn.setObjectName(u"animDataFromFileBttn")

    # Add widgets to layout & set margins
    stackedWdgtsBtnsHorizLayout.addWidget(self.animDataFromDBBttn)
    stackedWdgtsBtnsHorizLayout.addWidget(self.animDataFromFileBttn)
    stackedWdgtsBtnsHorizLayout.setContentsMargins(9, 0, 9, 0)
    stackedWdgtsBtnsHorizLayout.setSpacing(0)

    return stackedWdgtsBtnsHorizLayout

  def _create_top_vertical_layout(self) -> None:
    """
    Method to create top vertical layout to manage Title label & selection buttons layout.
    """

    # Create top layout
    self.animDataTopVertLayout = QVBoxLayout()
    self.animDataTopVertLayout.setObjectName(u"animDataTopVertLayout")

    # Create title label
    animDataTitleLabel = LabelWidget(parent=self, logger=self._logger, text=u"Animation Data",
                                     type="title_label", minsize=QSize(0, 20),
                                     align=Qt.AlignCenter)
    animDataTitleLabel.setObjectName(u"animDataTitleLabel")

    btnsHorizLayout = self._create_stacked_wdgt_ctrl_btns_layout()

    # Add widgets to layout & set margins
    self.animDataTopVertLayout.addWidget(animDataTitleLabel)
    self.animDataTopVertLayout.addLayout(btnsHorizLayout)
    self.animDataTopVertLayout.setContentsMargins(0, 0, 0, 0)
    self.animDataTopVertLayout.setSpacing(15)

  def _create_anim_data_stacked_wdgt(self) -> None:
    """
    Main method to create stacked widget with required pages.
    """

    # Create stacked widget
    self.animDataStackedWidget = QStackedWidget(self)
    self.animDataStackedWidget.setObjectName(u"animDataStackedWidget")

    # Create pages
    self.animDataFromDBPage = AnimDataFromDBWidget(parent=self, logger=AnimDataUILogger)
    self.animDataFromFilePage = AnimDataFromFileWidget(parent=self, logger=AnimDataUILogger)

    # Add pages to stacked widget
    self.animDataStackedWidget.addWidget(self.animDataFromDBPage)
    self.animDataStackedWidget.addWidget(self.animDataFromFilePage)

  def _create_local_connect(self) -> None:
    """
    Method to create connections of signals of the local widgets to the respective slots.
    """

    # Pushbuttons
    self.animDataFromDBBttn.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=0)
    )
    self.animDataFromFileBttn.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=1)
    )

    # Stacked Widget
    self.animDataStackedWidget.currentChanged.connect(
      self._on_stacked_widget_page_changed
    )

  def _create_stacked_wdgt_pages_connect(self) -> None:
    """
    Method to create connections of signals of the stacked widget pages to the respective slots.
    """

    # Animation Data from File Page
    self.animDataFromFilePage.publish_animation_point.connect(
      lambda anim_point: self.publish_animation_point.emit(anim_point)
    )

  def _on_page_select_button_clicked(self, idx: int=0) -> None:
    self.animDataStackedWidget.setCurrentIndex(idx)

  def _on_stacked_widget_page_changed(self, idx: int=0) -> None:
    if not isinstance(idx, int):
      AnimDataUILogger.warning("Invalid index type received")
      return

    if idx == 0:
      self.animDataFromDBBttn.setEnabled(False)
      self.animDataFromFileBttn.setEnabled(True)
    elif idx == 1:
      self.animDataFromDBBttn.setEnabled(True)
      self.animDataFromFileBttn.setEnabled(False)

  def save_state(self) -> None:
    """
    Method to save the widget state and perform cleanup before closing.
    """

    self.animDataFromDBPage.save_state()
    self.animDataFromFilePage.save_state()

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called when the widget is closed.
    """

    self.save_state()
    return super(AnimDataWidget, self).closeEvent(event)


class AnimDataFromDBWorker(QObject):

  anim_data_wdgt_msg_sent = Signal(str)
  anim_data_publish_table_data = Signal(str, object)
  anim_data_publish_table_names = Signal(dict)

  def __init__(self) -> None:
    super(AnimDataFromDBWorker, self).__init__()

    self.path_id = 0
    self.kinematic_id = 0
    # Get computer name - works on both Windows and macOS/Linux
    comp_name = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME') or 'localhost'
    self.db_client = DatabaseNodeStream(
                       server_name = f"{comp_name}\\{self._fetch_server_instance()}",
                       database_name = "Artemotion",
                       username = "",
                       password = "",
                       data_from = "sql"
                     )
    self.path_table = "Path"
    self.kinematic_table = "Kinematic"
    self.path_position_table = "PathPosition"

  def _fetch_server_instance(self) -> Union[str, None]:
    result = os.popen('reg query "HKLM\Software\Microsoft\Microsoft SQL Server\Instance Names\SQL')
    try:
      return [line.strip() for line in result.readlines() if line != '\n'][1].split()[0]
    except Exception:
      return None

  def _evaluate_relational_tables(self, table_name: str='') -> Tuple[list, list]:
    ids = []
    names = []
    if table_name not in self.get_table_names():
      AnimDataUILogger.warning("Table does not exist in database")
      return

    q_str = f"SELECT * from {table_name}"
    query = self.db_client.db_process_query(q_string=q_str)
    while query.next():
      ids.append(query.value(query.record().indexOf('id')))
      names.append(query.value(query.record().indexOf('Name')))

    return ids, names

  def _add_entry_to_path_table(self, path_name: str='') -> int:
    if path_name == '':
      AnimDataUILogger.info("Inavalid Robot name received")
      return

    ids, names = self._evaluate_relational_tables(table_name=self.path_table)
    if path_name not in names:
      if len(ids) == 0:
        ids.append(len(ids))
      q_str = f"INSERT INTO {self.path_table} (id, Name) VALUES({max(ids) + 1}, '{path_name}')"
      self.db_client.db_process_query(q_string=q_str)
      return (max(ids) + 1)
    else:
      q_str = f"SELECT id FROM {self.path_table} where Name='{path_name}'"
      query = self.db_client.db_process_query(q_string=q_str)
      if query.next():
        path_id = query.value(query.record().indexOf('id'))
        q_str = f"DELETE FROM {self.path_position_table} WHERE Path = {path_id}"
        self.db_client.db_process_query(q_string=q_str)
        return path_id

  def _add_entry_to_kinematics_table(self, robot_name: str='') -> int:
    if robot_name == '':
      AnimDataUILogger.info("Inavalid Robot name received")
      return

    ids, names = self._evaluate_relational_tables(table_name=self.kinematic_table)
    if robot_name not in names:
      if len(ids) == 0:
        ids.append(len(ids))
      q_str = f"INSERT INTO {self.kinematic_table} (id, Name) VALUES({max(ids) + 1}, '{robot_name}')"
      self.db_client.db_process_query(q_string=q_str)
      return (max(ids) + 1)
    else:
      q_str = f"SELECT id FROM {self.kinematic_table} where Name='{robot_name}'"
      query = self.db_client.db_process_query(q_string=q_str)
      if query.next():
        return query.value(query.record().indexOf('id'))

  def _add_entry_to_PathPositions_table(self, **kwargs) -> QSqlQuery:
    if len(kwargs) < 16:
      AnimDataUILogger.info("Invalid data received")
      return

    q_str = f"""
             INSERT INTO {self.path_position_table}
             (Kinematic, Path, Pos, Time,
             Robot_A1, Robot_A2, Robot_A3, Robot_A4, Robot_A5, Robot_A6,
             Track_A1, Track_A2, Track_A3, Cam_Focus, Cam_Iris, Cam_Zoom)
             VALUES({kwargs['kinematic_id']}, {kwargs['path_id']}, {kwargs['pos']},
             {kwargs['Time']}, {kwargs['Robot_A1']}, {kwargs['Robot_A2']}, {kwargs['Robot_A3']},
             {kwargs['Robot_A4']}, {kwargs['Robot_A5']}, {kwargs['Robot_A6']}, {kwargs['Track_A1']},
             {kwargs['Track_A2']}, {kwargs['Track_A3']}, {kwargs['Cam_Focus']}, {kwargs['Cam_Iris']},
             {kwargs['Cam_Zoom']})
             """
    query = self.db_client.db_process_query(q_string=q_str)
    return query

  def determine_tables_names(self) -> None:
    tables = []
    if self.db_client is not None:
      tables = self.db_client.db_tables()

    if len(tables) > 0:
      # Path Table
      if self.path_table in tables:
        pass
      elif self.path_table.lower() in tables:
        self.path_table = self.path_table.lower()
      elif self.path_table.upper() in tables:
        self.path_table = self.path_table.upper()
      elif self.path_table.title() in tables:
        self.path_table = self.path_table.title()

      # Kinematic table
      if self.kinematic_table in tables:
        pass
      elif self.kinematic_table.lower() in tables:
        self.kinematic_table = self.kinematic_table.lower()
      elif self.kinematic_table.upper() in tables:
        self.kinematic_table = self.kinematic_table.upper()
      elif self.kinematic_table.title() in tables:
        self.kinematic_table = self.kinematic_table.title()

      # PathPosition table
      if self.path_position_table in tables:
        pass
      elif self.path_position_table.lower() in tables:
        self.path_position_table = self.path_position_table.lower()
      elif self.path_position_table.upper() in tables:
        self.path_position_table = self.path_position_table.upper()
      elif self.path_position_table.title() in tables:
        self.path_position_table = self.path_position_table.title()
    else:
      AnimDataUILogger.warning("Database does not have any table")

    # Send table names to widget class
    self.anim_data_publish_table_names.emit(
      {
        "path_tb": self.path_table,
        "kinematic_tb": self.kinematic_table,
        "path_position_tb": self.path_position_table
      }
    )

  def get_table_names(self) -> List[str]:
    return self.db_client.db_tables()

  def get_table_data(self, table_name: str='') -> None:
    if table_name not in self.get_table_names():
      AnimDataUILogger.warning("Table does not exist in database")
      return

    q_str = f"SELECT * from {table_name}"
    query = self.db_client.db_process_query(q_string=q_str)

    self.anim_data_publish_table_data.emit(table_name, query)

  def update_tables_with_anim_data(self, data_str: str) -> None:
    try:
      data_dict = json.loads(data_str)

      AnimDataUILogger.info(f"Processing data: {data_dict}")
      # Enter data into relational tables
      if float(data_dict['TIME']) == 0:
        self.path_id = self._add_entry_to_path_table(path_name='Path_' + data_dict['ROBOT'])
        self.kinematic_id = self._add_entry_to_kinematics_table(robot_name=data_dict['ROBOT'])

      # Enter data into PathPosition table
      self._add_entry_to_PathPositions_table(
        pos = (int((float(data_dict["TIME"])*1000) / 12) + 1),
        path_id = self.path_id,
        kinematic_id = self.kinematic_id,
        Time = float(data_dict['TIME']),
        Robot_A1 = float(data_dict['AXES_VALUES'].split(', ')[0].split(' ')[1]),
        Robot_A2 = float(data_dict['AXES_VALUES'].split(', ')[1].split(' ')[1]),
        Robot_A3 = float(data_dict['AXES_VALUES'].split(', ')[2].split(' ')[1]),
        Robot_A4 = float(data_dict['AXES_VALUES'].split(', ')[3].split(' ')[1]),
        Robot_A5 = float(data_dict['AXES_VALUES'].split(', ')[4].split(' ')[1]),
        Robot_A6 = float(data_dict['AXES_VALUES'].split(', ')[5].split(' ')[1]),
        Track_A1 = float(0.0),
        Track_A2 = float(0.0),
        Track_A3 = float(0.0),
        Cam_Focus = float(data_dict['CAM_VALUES'].split(', ')[0].split(' ')[1]),
        Cam_Iris = float(data_dict['CAM_VALUES'].split(', ')[1].split(' ')[1]),
        Cam_Zoom = float(data_dict['CAM_VALUES'].split(', ')[2].split(' ')[1])
      )
    except Exception:
      AnimDataUILogger.exception("Unable to parse data string because:")
      return

  def delete_data_from_rel_tables(self, id: int=-1, table_name: str='') -> None:
    if id < 0:
      AnimDataUILogger.info("Invalid ID received")
      return

    if table_name == '':
      AnimDataUILogger.info("Invalid Table Name received")
      return

    if table_name == self.path_table:
      q_str = f"DELETE FROM {self.path_position_table} where Path={id}"
      query = self.db_client.db_process_query(q_string=q_str)
      self.anim_data_publish_table_data.emit(self.path_position_table, query)

    if table_name == self.kinematic_table:
      q_str = f"DELETE FROM {self.path_position_table} where Kinematic={id}"
      query = self.db_client.db_process_query(q_string=q_str)
      self.anim_data_publish_table_data.emit(self.kinematic_table, query)

    q_str = f"DELETE FROM {table_name} WHERE id={id}"
    query = self.db_client.db_process_query(q_string=q_str)
    self.anim_data_publish_table_data.emit(table_name, query)

  def delete_data_from_table(self, path: int=-1, pos: int=-1, table_name: str='') -> None:
    if path < 0:
      AnimDataUILogger.info("Invalid Path received")
      return

    if pos < 0:
      AnimDataUILogger.info("Invalid Pos received")

    if table_name == '':
      AnimDataUILogger.info("Invalid Table Name received")
      return

    q_str = f"DELETE FROM {table_name} WHERE Path={path} AND Pos={pos}"
    query = self.db_client.db_process_query(q_string=q_str)

    self.anim_data_publish_table_data.emit(table_name, query)


class AnimDataFromDBWidget(QFrame):

  """
  Class to manage the Animation Data From Database Widget derived from QFrame class.

  Keyword Arguments:
    parent: QWidget
      parent widget
    logger: Logger)
      logger class
  """

  anim_data_request_table_data = Signal(str)
  anim_data_request_table_names = Signal()
  anim_data_delete_table_data = Signal(int, int, str)
  anim_data_delete_rel_table_data = Signal(int, str)
  publish_status_message = Signal(str)
  publish_animation_data = Signal(dict)

  def __init__(self, **kwargs) -> None:
    super(AnimDataFromDBWidget, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']
    self._database_tables = {}

    self.init_UI()

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create main layout
    animDataFrmDBWdgtMainLayout = QVBoxLayout(self)
    animDataFrmDBWdgtMainLayout.setObjectName(u"animDataFrmDBWdgtMainLayout")

    # Create stacked widget
    self._create_anim_data_from_db_stacked_wdgt()

    # Add widgets to the layout & set margins
    animDataFrmDBWdgtMainLayout.addLayout(self._create_stacked_wdgt_ctrl_btns_layout())
    animDataFrmDBWdgtMainLayout.addWidget(self.animDataFrmDBStackedWidget)
    animDataFrmDBWdgtMainLayout.setContentsMargins(20, 10, 20, 10)
    animDataFrmDBWdgtMainLayout.setSpacing(10)

    # Connections
    self._create_local_connect()

    # Workers & threads
    self._create_wdgt_worker_thread()

    # Emit initialization signals
    # self.anim_data_request_table_names.emit() # TO-DO: Uncoment this once Database is established

    self._on_page_select_button_clicked() # To set Stacked Widget index
    self._on_stacked_widget_page_changed()

  def _create_stacked_wdgt_ctrl_btns_layout(self) -> QLayout:
    """
    Method to create layout to manage the buttons to change the pages of Stacked widget.

    Returns:
      stackedWdgtsBtnsHorizLayout: QLayout
        Buttons horizontal layout
    """

    # Create buttons horizontal layout
    stackedWdgtsBtnsHorizLayout = QHBoxLayout()
    stackedWdgtsBtnsHorizLayout.setObjectName(u"stackedWdgtsBtnsHorizLayout")

    # Paths Table Page Select button
    self.pathsPageSelectButton = PushButtonWidget(parent=self, logger=self._logger,
                                                  text=u"Paths Table", type="left_button",
                                                  minsize=QSize(0, 20))
    self.pathsPageSelectButton.setObjectName(u"pathsPageSelectButton")

    # Kinematics Table Page Select button
    self.kinematicsPageSelectButton = PushButtonWidget(parent=self, logger=self._logger,
                                                       text=u"Kinematics Table",
                                                       type="page_sel_btn", minsize=QSize(0, 20))
    self.kinematicsPageSelectButton.setObjectName(u"kinematicsPageSelectButton")

    # Paths Position Table Page Select button
    self.pathsPositionPageSelectButton = PushButtonWidget(parent=self, logger=self._logger,
                                                          text=u"PathsPosition Table",
                                                          type="right_button",
                                                          minsize=QSize(0, 20))
    self.pathsPositionPageSelectButton.setObjectName(u"pathsPositionPageSelectButton")

    # Add widgets to layout & set margins
    stackedWdgtsBtnsHorizLayout.addWidget(self.pathsPageSelectButton)
    stackedWdgtsBtnsHorizLayout.addWidget(self.kinematicsPageSelectButton)
    stackedWdgtsBtnsHorizLayout.addWidget(self.pathsPositionPageSelectButton)
    stackedWdgtsBtnsHorizLayout.setContentsMargins(9, 0, 9, 0)
    stackedWdgtsBtnsHorizLayout.setSpacing(0)

    return stackedWdgtsBtnsHorizLayout

  def _create_anim_data_from_db_stacked_wdgt(self) -> None:
    # Create stacked widget
    self.animDataFrmDBStackedWidget = QStackedWidget(self)
    self.animDataFrmDBStackedWidget.setObjectName(u"animDataFrmDBStackedWidget")

    # Create pages
    self.pathsTablePage = PathsTablePage(logger=self._logger)
    self.kinematicsTablePage = KinematicsTablePage(logger=self._logger)
    self.pathPositionsTablePage = PathPositionsTablePage(logger=self._logger)

    # Add pages to stacked widget
    self.animDataFrmDBStackedWidget.addWidget(self.pathsTablePage)
    self.animDataFrmDBStackedWidget.addWidget(self.kinematicsTablePage)
    self.animDataFrmDBStackedWidget.addWidget(self.pathPositionsTablePage)

  def _create_local_connect(self) -> None:
    # Pushbuttons
    self.pathsPageSelectButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=0)
    )
    self.kinematicsPageSelectButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=1)
    )
    self.pathsPositionPageSelectButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=2)
    )

    self.pathsTablePage.refreshButton.clicked.connect(
      lambda: self._on_refresh_button_clicked(self._database_tables['path_tb'])
    )
    self.pathsTablePage.deleteButton.clicked.connect(
      lambda: self._on_delete_button_clicked(self._database_tables['path_tb'])
    )
    self.kinematicsTablePage.refreshButton.clicked.connect(
      lambda: self._on_refresh_button_clicked(self._database_tables['kinematic_tb'])
    )
    self.kinematicsTablePage.deleteButton.clicked.connect(
      lambda: self._on_delete_button_clicked(self._database_tables['kinematic_tb'])
    )
    self.pathPositionsTablePage.refreshButton.clicked.connect(
      lambda: self._on_refresh_button_clicked(self._database_tables['path_position_tb'])
    )
    self.pathPositionsTablePage.deleteButton.clicked.connect(
      lambda: self._on_delete_button_clicked(self._database_tables['path_position_tb'])
    )

    # Stacked Widget
    self.animDataFrmDBStackedWidget.currentChanged.connect(
      self._on_stacked_widget_page_changed
    )

  def _create_wdgt_worker_thread(self) -> None:
    # Create the Worker & thread
    self.anim_data_wdgt_worker_thread = QThread(self)
    self.anim_data_wdgt_worker = AnimDataFromDBWorker()
    self.anim_data_wdgt_worker.moveToThread(self.anim_data_wdgt_worker_thread)

    # Create connections
    self.anim_data_request_table_data.connect(self.anim_data_wdgt_worker.get_table_data)
    self.anim_data_request_table_names.connect(self.anim_data_wdgt_worker.determine_tables_names)
    self.publish_animation_data.connect(self.anim_data_wdgt_worker.update_tables_with_anim_data)
    self.anim_data_delete_table_data.connect(self.anim_data_wdgt_worker.delete_data_from_table)
    self.anim_data_delete_rel_table_data.connect(self.anim_data_wdgt_worker.delete_data_from_rel_tables)

    self.anim_data_wdgt_worker.anim_data_publish_table_data.connect(self.on_table_data_received)
    self.anim_data_wdgt_worker.anim_data_publish_table_names.connect(self._set_database_tables)

    # Start the worker thread
    self.anim_data_wdgt_worker_thread.start()

  def _set_database_tables(self, db_tables: dict={}) -> None:
    if len(db_tables) == 0:
      AnimDataUILogger.warning("No table names received")
      return

    self._database_tables = db_tables

  def _on_page_select_button_clicked(self, idx: int=0) -> None:
    self.animDataFrmDBStackedWidget.setCurrentIndex(idx)

  def _on_refresh_button_clicked(self, table_name: str='') -> None:
    if table_name == '':
      AnimDataUILogger.warning("Invalid table name")
      return

    self.anim_data_request_table_data.emit(table_name)

  def _on_delete_button_clicked(self, table_name: str='') -> None:
    id = 0
    path = 0
    pos = 0
    if table_name == '':
      AnimDataUILogger.warning("Invalid table name")
      return

    if table_name == self._database_tables['path_tb']:
      id = self.pathsTablePage.tableView.data(self.pathsTablePage.tableView.currentIndex(),
                                              self.pathsTablePage.tableView.model.ID_DATA_ROLE)
      AnimDataUILogger.info(f"Requesting to delete ID: {id} from Path table")
      self.anim_data_delete_rel_table_data.emit(id, table_name)
    elif table_name == self._database_tables['kinematic_tb']:
      id = self.kinematicsTablePage.tableView.data(
              self.kinematicsTablePage.tableView.currentIndex(),
              self.kinematicsTablePage.tableView.model.ID_DATA_ROLE)
      AnimDataUILogger.info(f"Requesting to delete ID: {id} from Kinematic table")
      self.anim_data_delete_rel_table_data.emit(id, table_name)
    elif table_name == self._database_tables['path_position_tb']:
      path, pos = self.pathPositionsTablePage.tableView.data(
                    self.pathPositionsTablePage.tableView.currentIndex(),
                    self.pathPositionsTablePage.tableView.model.PATH_POS_DATA_ROLE)
      AnimDataUILogger.info(f"Requesting to delete Path: {path} at Pos: {pos} from PathPosition table")
      self.anim_data_delete_table_data.emit(path, pos, table_name)

  def _on_stacked_widget_page_changed(self, idx: int=0) -> None:
    if not isinstance(idx, int):
      AnimDataUILogger.warning("Invalid index type received")
      return

    if idx == 0:
      self.pathsPageSelectButton.setEnabled(False)
      self.kinematicsPageSelectButton.setEnabled(True)
      self.pathsPositionPageSelectButton.setEnabled(True)
    elif idx == 1:
      self.pathsPageSelectButton.setEnabled(True)
      self.kinematicsPageSelectButton.setEnabled(False)
      self.pathsPositionPageSelectButton.setEnabled(True)
    elif idx == 2:
      self.pathsPageSelectButton.setEnabled(True)
      self.kinematicsPageSelectButton.setEnabled(True)
      self.pathsPositionPageSelectButton.setEnabled(False)

  def on_table_data_received(self, table_name: str='', query: QSqlQuery=None) -> None:
    if table_name == '':
      AnimDataUILogger.warning("Invalid table name received")
      return

    if query is None:
      AnimDataUILogger.warning("Invalid table data received")
      return

    # Set query to TableView
    if table_name == self._database_tables['path_tb']:
      self.pathsTablePage.tableView.clear()
      self.pathsTablePage.tableView.model.setQuery(query)
      self.pathsTablePage.tableView.resizeColumnsToContents()
    elif table_name == self._database_tables['kinematic_tb']:
      self.kinematicsTablePage.tableView.clear()
      self.kinematicsTablePage.tableView.model.setQuery(query)
      self.kinematicsTablePage.tableView.resizeColumnsToContents()
    elif table_name == self._database_tables['path_position_tb']:
      self.pathPositionsTablePage.tableView.clear()
      self.pathPositionsTablePage.tableView.model.setQuery(query)
      self.pathPositionsTablePage.tableView.resizeColumnsToContents()

  def on_tcp_client_sock_msg_recvd(self, msg_dict: dict={}) -> None:
    if not isinstance(msg_dict, dict):
      AnimDataUILogger.warning("Invalid message dict received")
      return

    if msg_dict['MSG_TYPE'] == 'ANIM_DATA':
      AnimDataUILogger.info(f"Path data received: {msg_dict}")
      self.publish_animation_data.emit(msg_dict['DATA'])

  def save_state(self) -> None:
    """
    Method to save the widget state and perform cleanup before closing.
    """

    try:
      if self.anim_data_wdgt_worker_thread.isRunning():
        self.anim_data_wdgt_worker_thread.quit()
        self.anim_data_wdgt_worker_thread.wait()
    except Exception:
      AnimDataUILogger.exception("Unable to close Animation Data Widget worker thread because:")

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called when the widget is closed.
    """

    self.save_state()
    return super(AnimDataFromDBWidget, self).closeEvent(event)


class PathsTablePage(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(PathsTablePage, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"pathsTablePage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self._settings = kwargs.get('settings', None)

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    pathsTablePageVertLayout = QVBoxLayout(self)
    pathsTablePageVertLayout.setObjectName(u"pathsTablePageVertLayout")

    # Create group boxes
    btnsLayout = self._create_buttons_layout()
    self._create_table_view()

    # Add widgets to layout & set margins
    pathsTablePageVertLayout.addLayout(btnsLayout)
    pathsTablePageVertLayout.addWidget(self.tableView)
    pathsTablePageVertLayout.setContentsMargins(15, 0, 15, 0)
    pathsTablePageVertLayout.setSpacing(0)

  def _create_buttons_layout(self) -> QLayout:
    # Create buttons layout
    buttonsHorizontalLayout = QHBoxLayout()
    buttonsHorizontalLayout.setObjectName(u"buttonsHorizontalLayout")

    # Create spacer and buttons
    buttonsHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    self.refreshButton = PushButtonWidget(parent=self, logger=self._logger, minsize=QSize(20, 20),
                                          maxsize=QSize(20, 20))
    self.refreshButton.setObjectName(u"refreshButton")
    self.refreshButton.setToolTip(u"Refresh")

    self.deleteButton = PushButtonWidget(parent=self, logger=self._logger, minsize=QSize(20, 20),
                                         maxsize=QSize(20, 20))
    self.deleteButton.setObjectName(u"deleteButton")
    self.deleteButton.setToolTip(u"Delete")

    # Add widgets to horizontal layout & set margins
    buttonsHorizontalLayout.addItem(buttonsHorizontalSpacer)
    buttonsHorizontalLayout.addWidget(self.refreshButton)
    buttonsHorizontalLayout.addWidget(self.deleteButton)
    buttonsHorizontalLayout.setContentsMargins(0, 0, 0, 0)

    return buttonsHorizontalLayout

  def _create_table_view(self) -> None:
    # Create Paths Table View
    self.tableView = AnimDataRelTableView(table_name="Paths Table",
                                          settings=self._settings,
                                          parent=self)
    self.tableView.setObjectName(u"pathsTableView")


class KinematicsTablePage(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(KinematicsTablePage, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"kinematicsTablePage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self._settings = kwargs.get('settings', None)

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    kinematicsTablePageVertLayout = QVBoxLayout(self)
    kinematicsTablePageVertLayout.setObjectName(u"pathsTablePageVertLayout")

    # Create group boxes
    btnsLayout = self._create_buttons_layout()
    self._create_table_view()

    # Add widgets to layout & set margins
    kinematicsTablePageVertLayout.addLayout(btnsLayout)
    kinematicsTablePageVertLayout.addWidget(self.tableView)
    kinematicsTablePageVertLayout.setContentsMargins(15, 0, 15, 0)
    kinematicsTablePageVertLayout.setSpacing(0)

  def _create_buttons_layout(self) -> QLayout:
    # Create buttons layout
    buttonsHorizontalLayout = QHBoxLayout()
    buttonsHorizontalLayout.setObjectName(u"buttonsHorizontalLayout")

    # Create spacer and buttons
    buttonsHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    self.refreshButton = PushButtonWidget(parent=self, logger=self._logger, minsize=QSize(20, 20),
                                          maxsize=QSize(20, 20))
    self.refreshButton.setObjectName(u"refreshButton")
    self.refreshButton.setToolTip(u"Refresh")

    self.deleteButton = PushButtonWidget(parent=self, logger=self._logger, minsize=QSize(20, 20),
                                         maxsize=QSize(20, 20))
    self.deleteButton.setObjectName(u"deleteButton")
    self.deleteButton.setToolTip(u"Delete")

    # Add widgets to horizontal layout & set margins
    buttonsHorizontalLayout.addItem(buttonsHorizontalSpacer)
    buttonsHorizontalLayout.addWidget(self.refreshButton)
    buttonsHorizontalLayout.addWidget(self.deleteButton)
    buttonsHorizontalLayout.setContentsMargins(0, 0, 0, 0)

    return buttonsHorizontalLayout

  def _create_table_view(self) -> None:
    # Create Kinematics Table View
    self.tableView = AnimDataRelTableView(table_name="Kinematics Table",
                                          settings=self._settings,
                                          parent=self)
    self.tableView.setObjectName(u"kinematicsTableView")


class PathPositionsTablePage(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(PathPositionsTablePage, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"pathPositionsTablePage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self._settings = kwargs.get('settings', None)

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    pathPositionsTablePageVertLayout = QVBoxLayout(self)
    pathPositionsTablePageVertLayout.setObjectName(u"pathsTablePageVertLayout")

    # Create group boxes
    btnsLayout = self._create_buttons_layout()
    self._create_table_view()

    # Add widgets to layout & set margins
    pathPositionsTablePageVertLayout.addLayout(btnsLayout)
    pathPositionsTablePageVertLayout.addWidget(self.tableView)
    pathPositionsTablePageVertLayout.setContentsMargins(15, 0, 15, 0)
    pathPositionsTablePageVertLayout.setSpacing(0)

  def _create_buttons_layout(self) -> QLayout:
    # Create buttons layout
    buttonsHorizontalLayout = QHBoxLayout()
    buttonsHorizontalLayout.setObjectName(u"buttonsHorizontalLayout")

    # Create spacer and buttons
    buttonsHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    self.refreshButton = PushButtonWidget(parent=self, logger=self._logger, minsize=QSize(20, 20),
                                          maxsize=QSize(20, 20))
    self.refreshButton.setObjectName(u"refreshButton")
    self.refreshButton.setToolTip(u"Refresh")

    self.deleteButton = PushButtonWidget(parent=self, logger=self._logger, minsize=QSize(20, 20),
                                         maxsize=QSize(20, 20))
    self.deleteButton.setObjectName(u"deleteButton")
    self.deleteButton.setToolTip(u"Delete")

    # Add widgets to horizontal layout & set margins
    buttonsHorizontalLayout.addItem(buttonsHorizontalSpacer)
    buttonsHorizontalLayout.addWidget(self.refreshButton)
    buttonsHorizontalLayout.addWidget(self.deleteButton)
    buttonsHorizontalLayout.setContentsMargins(0, 0, 0, 0)

    return buttonsHorizontalLayout

  def _create_table_view(self) -> None:
    # Create Path Positions Table View
    self.tableView = AnimDataRelTableView(table_name="Path Positions Table",
                                          settings=self._settings,
                                          parent=self)
    self.tableView.setObjectName(u"pathPositionsTableView")


class AnimDataFromFileWorker(QObject):

  """
  Worker class to manage the Animation Data from file.

  Constants:
    FILE_FORMATS: list
      Accepted data file formats

  Signals:
    publish_file_header: Signal(list)
      Signal to publish headers of animation data
    enable_animation_stop: Signal(bool)
      Signal to enable stopping of the animation
    enable_animation_play: Signal(bool)
      Signal to enable playback of the animation
    enable_animation_pause: Signal(bool)
      Signal to enable pausing of the animation
    display_animation_data: Signal(list)
      Signal emitted to display animation data in TreeView
    publish_animation_point: Signal(list)
      Signal to publish the animation point
  """

  # Constants
  FILE_FORMATS = [".csv", ".emily", ".pgx"]
  CSV_FILE_HEADERS = ["Timestamp", "Axis 1", "Axis 2", "Axis 3", "Axis 4", "Axis 5", "Axis 6",
                      "Ext_Axis 1", "Ext_Axis 2", "Ext_Axis 3", "Cam_Axis 1", "Cam_Axis 2",
                      "Cam_Axis 3"]

  # Signals
  publish_file_header = Signal(list)
  enable_animation_stop = Signal(bool)
  enable_animation_play = Signal(bool)
  enable_animation_pause = Signal(bool)
  display_animation_data = Signal(list)
  publish_animation_point = Signal(list)

  def __init__(self, logger: Logger) -> None:
    super(AnimDataFromFileWorker, self).__init__()

    # logger
    self._logger = logger

    # Animation Data
    self.anim_data_file = None
    self.anim_data_q = []
    self.anim_active_data_q = deque()

    # Play controls
    self._stop_animation = False
    self._pause_animation = False
    self._playback_initiated = False
    self._wait_time_to_publish = 0.0
    self.publish_timer = QTimer(parent=self)
    self.publish_timer.setTimerType(Qt.PreciseTimer)
    self.publish_timer.timeout.connect(self.play_animation)

  def _read_anim_data_file(self) -> List:
    """
    Method to read animation data file.

    Returns:
      lines: list
        Lines from the animation data file.
    """

    lines = []
    try:
      with open(self.anim_data_file, 'r') as data_file:
        lines = data_file.readlines()
    except Exception:
      self._logger.exception(f"Unable to read {self.anim_data_file} because:")
    finally:
      return lines

  def _setup_data_publish_rate(self) -> bool:
    """
    Method to setup the animation data publishing rate.
    """

    try:
      self._wait_time_to_publish = (float(self.anim_data_q[1][0]) -
                                    float(self.anim_data_q[0][0]))
    except Exception:
      self._logger.exception("Unable to compute wait time to publish because:")
      return False
    else:
      self.publish_timer.setInterval(self._wait_time_to_publish*1000)
      return True

  def _check_for_camera_axes_values(self) -> None:
    """
    Method to check if the camera axes are present, if not add zeroes to the data.
    """

    try:
      if len(self.anim_data_q) > 0:
        if len(self.anim_data_q[0]) < len(self.CSV_FILE_HEADERS):
          [data.append(float(i * 0))
           for i in range((len(self.CSV_FILE_HEADERS)) - (len(self.anim_data_q[0])))
           for data in self.anim_data_q]
      self._logger.info(f"Animation data with camera axes: {self.anim_data_q}")
    except Exception:
      self._logger.exception("Unable to add camera axes values because:")

  def _check_for_external_axes_values(self) -> None:
    """
    Method to check if the external axes/track of the robot are present in the data, if not add
    zeroes to the data.
    """

    try:
      if len(self.anim_data_q) > 0:
        if len(self.anim_data_q[0]) < (len(self.CSV_FILE_HEADERS) - 3):
          [data.append(float(i * 0))
           for i in range(((len(self.CSV_FILE_HEADERS) - 3) - len(self.anim_data_q[0])))
           for data in self.anim_data_q]
        # To-Do: Add conditions to check various combinations of data in animation array &
        # produce the complete list of axes values
        #   Timestamp + 6 Axis
        #   Timestamp + 6 Axis + 1 Ext
        #   Timestamp + 6 Axis + 2 Ext
        #   Timestamp + 6 Axis + 1 Ext + 3 Cam Axes
        #   Timestamp + 6 Axis + 2 Ext + 3 Cam Axes
      self._logger.info(f"Animation data with external axes: {self.anim_data_q}")
    except Exception:
      self._logger.exception("Unable to add external axes values because:")

  def _publish_csv_animation_data(self) -> None:
    """
    Method to publish the animation data retrieved from a csv file.
    """

    if len(self.anim_data_q[0]) == len(self.CSV_FILE_HEADERS):
      self.publish_file_header.emit(self.CSV_FILE_HEADERS)
    elif len(self.anim_data_q[0]) == len(self.CSV_FILE_HEADERS) - 1:
      self.publish_file_header.emit(self.CSV_FILE_HEADERS[1:])
    self.display_animation_data.emit(self.anim_data_q)

  def _get_anim_data_from_csv_file(self) -> None:
    """
    Method to read animation data from the csv file (generic robots) and save it in the buffer.
    """

    lines = self._read_anim_data_file()
    try:
      [self.anim_data_q.append([float(l) for l in line.strip().split(", ")]) for line in lines[1:]]
    except Exception:
      self._logger.exception("Unable to decipher animation data because:")
    else:
      if self._setup_data_publish_rate():
        self._check_for_external_axes_values()
        self._check_for_camera_axes_values()
        self._publish_csv_animation_data()
        self.enable_animation_play.emit(True)

  def _get_anim_data_from_emily_file(self) -> None:
    """
    Method to read animation data from the emily file (KUKA robots) and save it in the buffer.
    """

    lines = self._read_anim_data_file()
    self._logger.info(f"Lines: {lines}")

  def _get_anim_data_from_pgx_file(self) -> None:
    """
    Method to read animation data from the pgx (Staubli Robots) file and save it in the buffer.
    """

    lines = self._read_anim_data_file()
    self._logger.info(f"Lines: {lines}")

  def setup_data_file(self, data_file_path: str='') -> None:
    """
    Method to setup the data file path and read the data into a buffer.

    Arguments:
      data_file_path: str
        Absolute path of the data file
    """

    if not isinstance(data_file_path, str):
      self._logger.warning("Invalid data file path received")
      return

    file_format = os.path.splitext(data_file_path)[1]
    if file_format not in self.FILE_FORMATS:
      self._logger.warning(
        "File type not supported, please select a valid file!!!"
      )
      return

    self.anim_data_file = data_file_path
    if file_format == '.csv':
      self._get_anim_data_from_csv_file()
    elif file_format == '.pgx':
      self._get_anim_data_from_pgx_file()
    elif file_format == '.emily':
      self._get_anim_data_from_emily_file()

  def play_pause_animation(self, play: bool=False) -> None:
    """
    Method to play/pause the animation.
    """

    if play:
      if len(self.anim_active_data_q) == 0:
        [self.anim_active_data_q.append(data) for data in self.anim_data_q]
      self.publish_timer.start()
      self.enable_animation_stop.emit(True)
      self.enable_animation_play.emit(False)
      self.enable_animation_pause.emit(True)
    else:
      self.publish_timer.stop()
      self.enable_animation_stop.emit(True)
      self.enable_animation_play.emit(True)
      self.enable_animation_pause.emit(False)

  def stop_animation(self) -> None:
    """
    Method to stop the animation.
    """

    self.anim_active_data_q.clear()
    if self.publish_timer.isActive():
      self.publish_timer.stop()
    self.enable_animation_stop.emit(False)
    self.enable_animation_play.emit(True)
    self.enable_animation_pause.emit(False)

  def play_animation(self) -> None:
    """
    Method to read the animation data queue & publish the data until pause, stopped and/or
    finished.
    """

    if len(self.anim_active_data_q) == 0:
      if self.publish_timer.isActive():
        self.publish_timer.stop()
      self._logger.warning("No animation data to play")
      return

    anim_point = self.anim_active_data_q.popleft()
    self.publish_animation_point.emit(anim_point)


class AnimDataFromFileWidget(QFrame):

  """
  Class to manage the Animation Data From File Widget derived from QFrame class.

  Keyword Arguments:
    parent: QWidget
      parent widget
    logger: Logger)
      logger class

  Constants:
    DATA_FILE_FILTERS: str
      Filter for the browsable files

  Signals:
    publish_anim_data_file_path: Signal(str)
      Signal to publish animation data file path
    play_anim_data: Signal(bool)
      Signal to play the animation data
    pause_anim_data: Signal(bool)
      Signal to pause the playing of animation data
    stop_anim_data: Signal
      Signal to stop the playing of animation data
    publish_animation_point: Signal(list)
      Signal to publish the animation data point
  """

  # Constants
  DATA_FILE_FILTERS = "data File (*.csv);;data File (*.emily);;data File (*.pgx);; All Files (*.*)"

  # Signals
  publish_anim_data_file_path = Signal(str)
  play_anim_data = Signal(bool)
  pause_anim_data = Signal(bool)
  stop_anim_data = Signal()
  publish_animation_point = Signal(list)

  def __init__(self, **kwargs) -> None:
    super(AnimDataFromFileWidget, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    # Setup the widget
    self.setObjectName(u"animDataFromFileWidget")
    if kwargs.get('parent') is None:
      self.resize(QSize(375, 382))

    self.init_UI()

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create main layout
    animDataFrmFileWdgtMainLayout = QVBoxLayout(self)
    animDataFrmFileWdgtMainLayout.setObjectName(u"animDataFrmFileWdgtMainLayout")

    # Create stacked widget
    self._create_anim_data_from_file_stacked_wdgt()

    # Add widgets to the layout & set margins
    animDataFrmFileWdgtMainLayout.addLayout(self._create_browse_anim_data_file_layout())
    animDataFrmFileWdgtMainLayout.addWidget(self.animDataFrmFileStackedWidget)
    animDataFrmFileWdgtMainLayout.setContentsMargins(20, 10, 20, 10)
    animDataFrmFileWdgtMainLayout.setSpacing(30)

    # Connections
    self._create_local_connect()

    # Create stacked widget pages connections
    self._create_anim_data_play_page_connect()

    # Workers & threads
    self._create_wdgt_worker_thread()

    self._on_page_select_button_clicked() # To set Stacked Widget index
    self._on_stacked_widget_page_changed()

  def _create_browse_anim_data_file_layout(self) -> QLayout:
    """
    Method to create layout to manage the widgets to browse the animation data file.

    Returns:
      stackedWdgtsBtnsHorizLayout: QLayout
        Buttons horizontal layout
    """

    # Create Horizontal Layout
    animDataFileHorizLayout = QHBoxLayout()
    animDataFileHorizLayout.setObjectName(u"animDataFileHorizLayout")

    # Animation Data File LineEdit
    self.animDataFileLineEdit = LineEditWidget(parent=self, logger=self._logger,
                                               ph_text=u"animation data file",
                                               minsize=QSize(0, 20))
    self.animDataFileLineEdit.setObjectName(u"animDataFileLineEdit")

    # Animation Data File Browse Button
    self.animDataFileBrowseBttn = PushButtonWidget(parent=self, logger=self._logger,
                                                   text=u"...", minsize=QSize(30, 20))
    self.animDataFileBrowseBttn.setObjectName(u"animDataFileBrowseBttn")

    # Add widgets to horizontal layout & set margins
    animDataFileHorizLayout.addWidget(self.animDataFileLineEdit)
    animDataFileHorizLayout.addWidget(self.animDataFileBrowseBttn)
    animDataFileHorizLayout.setContentsMargins(0, 0, 0, 0)
    animDataFileHorizLayout.setSpacing(0)

    return animDataFileHorizLayout

  def _create_anim_data_from_file_stacked_wdgt(self) -> None:
    """
    Method to create the Stacked widget and add pages.
    """

    # Create stacked widget
    self.animDataFrmFileStackedWidget = QStackedWidget(self)
    self.animDataFrmFileStackedWidget.setObjectName(u"animDataFrmFileStackedWidget")

    # Create Pages
    self.animDataFrmFilePlayPage = AnimDataFrmFilePlayPage(logger=self._logger)

    # Add Pages
    self.animDataFrmFileStackedWidget.addWidget(self.animDataFrmFilePlayPage)

  def _create_local_connect(self) -> None:
    """
    Method to create connections of signals of the local widgets to the respective slots.
    """

    # Pushbuttons
    self.animDataFileBrowseBttn.clicked.connect(self._on_anim_data_file_browse_btn_clicked)

  def _create_anim_data_play_page_connect(self) -> None:
    """
    Method to create connections of signals of the widgets on Animation Data Play page.
    """

    # Pushbuttons
    self.animDataFrmFilePlayPage.animPlayButton.clicked.connect(
      lambda: self.play_anim_data.emit(True)
    )
    self.animDataFrmFilePlayPage.animPauseButton.clicked.connect(
      lambda: self.pause_anim_data.emit(False)
    )
    self.animDataFrmFilePlayPage.animStopButton.clicked.connect(
      lambda: self.stop_anim_data.emit()
    )

  def _create_wdgt_worker_thread(self) -> None:
    """
    Method to create the animation data from file worker & the respective thread. This method
    also creates connection between the widget and the worker.
    """

    # Create worker & the thread
    self.anim_data_from_file_worker_thread = QThread(self)
    self.anim_data_from_file_worker = AnimDataFromFileWorker(logger=self._logger)
    self.anim_data_from_file_worker.moveToThread(self.anim_data_from_file_worker_thread)

    # Create connections
    self.publish_anim_data_file_path.connect(self.anim_data_from_file_worker.setup_data_file)
    self.play_anim_data.connect(self.anim_data_from_file_worker.play_pause_animation)
    self.pause_anim_data.connect(self.anim_data_from_file_worker.play_pause_animation)
    self.stop_anim_data.connect(self.anim_data_from_file_worker.stop_animation)

    self.anim_data_from_file_worker.enable_animation_stop.connect(
      lambda enable: self.animDataFrmFilePlayPage.animStopButton.setEnabled(enable)
    )
    self.anim_data_from_file_worker.enable_animation_play.connect(
      lambda enable: self.animDataFrmFilePlayPage.animPlayButton.setEnabled(enable)
    )
    self.anim_data_from_file_worker.enable_animation_pause.connect(
      lambda enable: self.animDataFrmFilePlayPage.animPauseButton.setEnabled(enable)
    )
    self.anim_data_from_file_worker.publish_animation_point.connect(
      lambda anim_data: self.publish_animation_point.emit(anim_data)
    )
    self.anim_data_from_file_worker.display_animation_data.connect(
      self._on_animation_data_received
    )
    self.anim_data_from_file_worker.publish_file_header.connect(
      self._on_anim_data_headers_received
    )

    # Start the worker thread
    self.anim_data_from_file_worker_thread.start()

  def _on_anim_data_file_browse_btn_clicked(self) -> None:
    """
    Method to process the event when the animation data file browse pushbutton clicked.
    """

    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    in_file_path, _ = QFileDialog.getOpenFileName(self, "Open data file", "",
                                                  self.DATA_FILE_FILTERS,
                                                  options=options)
    if in_file_path:
      self.animDataFileLineEdit.setText(f"{in_file_path}")
      self.publish_anim_data_file_path.emit(in_file_path)

  def _on_page_select_button_clicked(self, idx: int=0) -> None:
    """
    Method to process the event when selection button clicked.

    Argument:
      idx: int
        index of the page to be made active
    """

    self.animDataFrmFileStackedWidget.setCurrentIndex(idx)

  def _on_stacked_widget_page_changed(self, idx: int=0) -> None:
    """
    Method to process the event when the page of stacked widget changes.

    Argument:
      idx: int
        index of the page to be made active
    """

    if not isinstance(idx, int):
      self._logger.warning("Invalid index type received")
      return

  def _on_animation_data_received(self, anim_data: list) -> None:
    """
    Method to process the event when the animation data is received.

    Argument:
      anim_data: list
        list of animation points with timestamp
    """

    if len(anim_data) == 0:
      self._logger.warning("No animation data to display")
      return

    self._logger.info(f"Animation data received: {anim_data}")

  def _on_anim_data_headers_received(self, headers: list) -> None:
    """
    Method to process the event when the headers of the animation data received.

    Argument:
      headers: list
        list of headers of the animation data
    """

    if len(headers) == 0:
      self._logger.warning("Invalid headers received")
      return

    self._logger.info(f"Headers received: {headers}")
    # To-Do: Assign headers to the TableView

  def save_state(self) -> None:
    """
    Method to save the widget state and perform cleanup before closing.
    """

    try:
      if self.anim_data_from_file_worker_thread.isRunning():
        self.anim_data_from_file_worker_thread.quit()
        self.anim_data_from_file_worker_thread.wait()
    except Exception:
      self._logger.exception(
        "Unable to close the animation date from file worker thread because:"
      )

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called on Close Event.
    """

    self.save_state()
    return super(AnimDataFromFileWidget, self).closeEvent(event)


class AnimDataFrmFilePlayPage(QFrame):

  """
  Stacked Widget Page Class to manage the playback of the animation data from file.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings:
      widget settings
    logger: Logger)
      logger class
  """

  def __init__(self, **kwargs) -> None:
    super(AnimDataFrmFilePlayPage, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"animDataFrmFilePlayPage")
    if kwargs.get('parent') is None:
      self.resize(QSize(375, 382))

    # Settings
    self._settings = kwargs.get('settings', None)

    self.init_UI()

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create Main Layout
    animDataFrmFilePageVertLayout = QVBoxLayout(self)
    animDataFrmFilePageVertLayout.setObjectName(u"animDataFrmFilePageVertLayout")

    # Create TableView
    self._create_anim_data_table_view()

    # Add widgets to layout & set margins
    animDataFrmFilePageVertLayout.addWidget(self.tableView)
    animDataFrmFilePageVertLayout.addLayout(self._create_playback_ctrl_bttns_layout())
    animDataFrmFilePageVertLayout.setContentsMargins(15, 0, 15, 0)
    animDataFrmFilePageVertLayout.setSpacing(10)

  def _create_playback_ctrl_bttns_layout(self) -> QLayout:
    """
    Method to create a layout managing animation playback buttons.

    Returns:
      QLayout:
        Widget layout
    """

    # Create Layout
    animPlaybackCtrlBttnsLayout = QHBoxLayout()
    animPlaybackCtrlBttnsLayout.setObjectName(u"animPlaybackCtrlBttnsLayout")

    # Create Buttons
    self.animPlayButton = PushButtonWidget(parent=self, logger=self._logger, text=u"Play",
                                           type="left_button", minsize=QSize(0, 20))
    self.animPlayButton.setObjectName(u"animPlayButton")
    self.animPlayButton.setEnabled(False)

    self.animPauseButton = PushButtonWidget(parent=self, logger=self._logger, text=u"Pause",
                                            minsize=QSize(0, 20))
    self.animPauseButton.setObjectName(u"animPauseButton")
    self.animPauseButton.setEnabled(False)

    self.animStopButton = PushButtonWidget(parent=self, logger=self._logger, text=u"Stop",
                                           type="right_button", minsize=QSize(0, 20))
    self.animStopButton.setObjectName(u"animStopButton")
    self.animStopButton.setEnabled(False)

    # Add widgets to layout & set margins
    animPlaybackCtrlBttnsLayout.addWidget(self.animPlayButton)
    animPlaybackCtrlBttnsLayout.addWidget(self.animPauseButton)
    animPlaybackCtrlBttnsLayout.addWidget(self.animStopButton)
    animPlaybackCtrlBttnsLayout.setContentsMargins(0, 0, 0, 0)
    animPlaybackCtrlBttnsLayout.setSpacing(0)

    return animPlaybackCtrlBttnsLayout

  def _create_anim_data_table_view(self) -> None:
    """
    Method to create Table View showing animation data from the file.
    """

    # Create TableView
    self.tableView = AnimDataTableView(table_name="Animation Data",
                                       settings=self._settings,
                                       parent=self)
    self.tableView.setObjectName(u"animDataFrmFileTableView")


class AnimDataRelTableView(QTableView):

  def __init__(self, table_name: str, settings: QSettings=None, parent: QWidget=None) -> None:
    super(AnimDataRelTableView, self).__init__(parent=parent)

    # Load the settings
    try:
      self._settings = settings
      state = self._settings.value("anim_data_rel_table_state", None)
      if state is not None:
        self.horizontalHeader().restoreState(state)
    except Exception:
      AnimDataUILogger.info("Working with default settings.")
      pass

    # Setup the Table View
    self.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.setSelectionMode(QAbstractItemView.SingleSelection)

    # Set the model
    self.model = AnimDataRelTableModel(table_name=table_name)
    self.model.clear()
    self.setModel(self.model)

  def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> Any:
    return self.model.data(index, role)

  def clear(self) -> None:
    self.model.clear()


class AnimDataTableView(QTableView):

  def __init__(self, table_name: str, settings: QSettings=None, parent: QWidget=None) -> None:
    super(AnimDataTableView, self).__init__(parent=parent)

    # Load the settings
    try:
      self._settings = settings
      state = self._settings.value("anim_data_table_state", None)
      if state is not None:
        self.horizontalHeader().restoreState(state)
    except Exception:
      AnimDataUILogger.info("Working with default settings.")
      pass

    # Setup the Table View
    self.setSelectionBehavior(QAbstractItemView.SelectRows)

    # Set the model
    self.model = AnimDataTableModel(table_name=table_name)
    self.model.clear()
    self.setModel(self.model)

  def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> Any:
    return self.model.data(index, role)

  def clear(self) -> None:
    self.model.clear()


class AnimDataRelTableModel(QSqlRelationalTableModel):

  ID_DATA_ROLE = Qt.UserRole + 1

  def __init__(self, table_name: str) -> None:
    super(AnimDataRelTableModel, self).__init__()

    self.setTable(table_name)

  def clear(self) -> None:
    self.removeRows(0, self.rowCount())

  def setQuery(self, query: QSqlQuery=None) -> None:
    if not isinstance(query, QSqlQuery):
      AnimDataUILogger.warning(f"Invalid query received")
      return
    return super(AnimDataRelTableModel, self).setQuery(query)

  def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int=Qt.DisplayRole) -> Any:
    if not index.isValid():
      return None

    if role == self.ID_DATA_ROLE:
      row = index.row()
      column = index.column()
      return super().data(self.index(row, 0), Qt.DisplayRole)
    else:
      return super().data(index, role)


class AnimDataTableModel(QSqlTableModel):

  PATH_POS_DATA_ROLE = Qt.UserRole + 1

  def __init__(self, table_name: str) -> None:
    super(AnimDataTableModel, self).__init__()

    self.setTable(table_name)

  def clear(self) -> None:
    self.removeRows(0, self.rowCount())

  def setQuery(self, query: QSqlQuery=None) -> None:
    if not isinstance(query, QSqlQuery):
      AnimDataUILogger.warning(f"Invalid query received")
      return
    return super(AnimDataTableModel, self).setQuery(query)

  def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int=Qt.DisplayRole) -> Any:
    if not index.isValid():
      return None

    if role == self.PATH_POS_DATA_ROLE:
      row = index.row()
      column = index.column()
      AnimDataUILogger.info(f"Row & Column: {row}: {column}")
      return (super().data(self.index(row, 1), Qt.DisplayRole),
              super().data(self.index(row, 2), Qt.DisplayRole))
    else:
      return super().data(index, role)


if __name__ == '__main__':
  """ For development purpose only """
  #Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed QWidget
  anim_data_widget = AnimDataWidget()
  # Show the widget
  anim_data_widget.show()
  # execute the program
  sys.exit(app.exec())