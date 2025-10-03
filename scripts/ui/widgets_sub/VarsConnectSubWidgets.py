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

from typing import Any, List

from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QWidget

try:
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import StandardItem
  from scripts.ui.widgets_sub.SubWidgets import TreeViewWidget
  from scripts.ui.widgets_sub.OPCUASubWidgets import OPCUAVarsTreeView
  from scripts.ui.widgets_sub.OPCUASubWidgets import OPCUAVarsTreeModel
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import StandardItem
  from scripts.ui.widgets_sub.SubWidgets import TreeViewWidget
  from scripts.ui.widgets_sub.OPCUASubWidgets import OPCUAVarsTreeView
  from scripts.ui.widgets_sub.OPCUASubWidgets import OPCUAVarsTreeModel


class VarsConnSubUILogger(Logger):

  FILE_NAME = "ui_vars_conn_sub"
  LOGGER_NAME = "UIVarsConnSub"


class VarsConnOPCUATreeView(OPCUAVarsTreeView):

  def __init__(self, tree_name: str='vars_conn_opcua_tree',
               tree_model: QStandardItemModel=OPCUAVarsTreeModel(),
               header_labels: List=['Structure', 'Data Type', 'Access', 'Desciption'],
               parent: QWidget=None, settings: QSettings=None) -> None:
    super(VarsConnOPCUATreeView, self).__init__(tree_name, tree_model, header_labels, parent,
                                                settings)