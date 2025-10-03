# -*- coding: utf-8 -*- #
import os
import sys

from PySide6.QtSql import QSqlDatabase, QSqlQuery

try:
  from scripts.settings.Logger import Logger
except:
  # For development purpose only
  sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  from scripts.settings.Logger import Logger


class DatabaseClientLogger(Logger):

  FILE_NAME = "database_client"
  LOGGER_NAME = "DatabaseClientLogger"


class DatabaseNodeStream():
  """Simple Client class to interact with SQL Database"""

  def __init__(self, **kwargs):
    self.server_name = kwargs['server_name']
    self.database_name = kwargs['database_name']
    self.username = ""
    self.password = ""

    self.database = None

    # It helps to delete old/empty log files
    DatabaseClientLogger.remove_log_files()

  def db_connect(self):
    connString = f'DRIVER={{SQL Server}};SERVER={self.server_name};DATABASE={self.database_name}'
    try:
      self.database = QSqlDatabase.addDatabase("QODBC", f"{self.database_name}_db_conn")
      self.database.setDatabaseName(connString)
      self.database.open(self.username, self.password)
      if not self.database.isOpen():
        DatabaseClientLogger.info(f"Connection error: {self.database.lastError().databaseText()}")
    except Exception:
      DatabaseClientLogger.exception("Unable to connect to database because:")

  def db_tables(self):
    if self.database is None:
      self.db_connect()
    return self.database.tables()

  def db_create(self):
    pass

  def db_process_query(self, q_string=""):
    query = None
    if self.database is None:
      self.db_connect()

    DatabaseClientLogger.info(f"Processing query: {q_string}")
    try:
      query = QSqlQuery(self.database)
      query.prepare(q_string)
      query.exec_()
    except Exception:
      DatabaseClientLogger.exception("Unable to process query because:")

    return query

  def db_update(self):
    pass

  def db_delete(self):
    pass


if __name__ == '__main__':
  """For development purpose only"""
  db_client = DatabaseNodeStream(server_name = "DESKTOP-B4NSNJ1\\SQLEXPRESS2019",
                                 database_name = "Artemotion",
                                 username = "",
                                 password = "")
  tables = db_client.db_tables()
  DatabaseClientLogger.info(f"Database tables: {tables}")
  # q = db_client.db_process_query(q_string="SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name LIKE 'Path'")
  q = db_client.db_process_query(q_string="SELECT * FROM Path")
  ids = []
  names = []
  while q.next():
    ids.append(q.value(q.record().indexOf('id')))
    names.append(q.value(q.record().indexOf('Name')))
  DatabaseClientLogger.info(f"{max(ids) + 1}")
  DatabaseClientLogger.info(f"{names}")