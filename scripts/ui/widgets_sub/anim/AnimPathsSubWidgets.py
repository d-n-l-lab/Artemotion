## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including sub Widget classes required for AnimPathsWidget.
##
##############################################################################################
##
import os
import sys
import json

from typing import Any, Dict, Union

from PySide6.QtGui import QPainter, QStandardItemModel
from PySide6.QtCore import (Signal, QSize, QAbstractItemModel, QModelIndex, QPersistentModelIndex,
                            Qt)
from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QHeaderView,
                               QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem)

try:
  from scripts.ui.widgets_sub.SubWidgets import (LabelWidget, LineEditWidget, TableViewWidget,
                                                 StandardItem)
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.ui.widgets_sub.SubWidgets import (LabelWidget, LineEditWidget, TableViewWidget,
                                                 StandardItem)


class KeyFramesWidget(QWidget):

  """
  Subclassed QWidget to create widget to edit the KeyFrames data.

  Keyword Arguments:
    parent: QWidget
      parent widget
    logger: Logger
      logger class
    show_roll: bool
      flag to create & show Roll angle widgets
  """

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(KeyFramesWidget, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    self._show_roll = kwargs.get('show_roll', False)

    self._init_widget()

  def _init_widget(self) -> None:
    """
    Method to create & initialize the widget.
    """

    # Create layout
    kfWidgetLayout = QGridLayout(self)
    kfWidgetLayout.setObjectName(u"kfWidgetLayout")

    # Create labels
    xPosLabel = LabelWidget(parent=self, logger=self._logger, text=u"X: ", type="sub_label",
                            align=Qt.AlignCenter)
    xPosLabel.setObjectName(u"xPosLabel")

    yPosLabel = LabelWidget(parent=self, logger=self._logger, text=u"Y: ", type="sub_label",
                            align=Qt.AlignCenter)
    yPosLabel.setObjectName(u"yPosLabel")

    zPosLabel = LabelWidget(parent=self, logger=self._logger, text=u"Z: ", type="sub_label",
                            align=Qt.AlignCenter)
    zPosLabel.setObjectName(u"zPosLabel")

    # Create LineEdits
    self.xPosLineEdit = LineEditWidget(parent=self, logger=self._parent, type="data",
                                       only_float=True)
    self.xPosLineEdit.setObjectName(u"xPosLineEdit")

    self.yPosLineEdit = LineEditWidget(parent=self, logger=self._parent, type="data",
                                       only_float=True)
    self.yPosLineEdit.setObjectName(u"yPosLineEdit")

    self.zPosLineEdit = LineEditWidget(parent=self, logger=self._parent, type="data",
                                       only_float=True)
    self.zPosLineEdit.setObjectName(u"zPosLineEdit")

    # Roll Widgets
    if self._show_roll:
      rollLabel = LabelWidget(parent=self, logger=self._logger, text=u"Roll", type="sub_label",
                              align=Qt.AlignCenter)
      rollLabel.setObjectName(u"rollLabel")

      self.rollLineEdit = LineEditWidget(parent=self, logger=self._logger, type="data",
                                         only_float=True)
      self.rollLineEdit.setObjectName(u"rollLineEdit")

    # Add widgets to layout & set margins
    kfWidgetLayout.addWidget(xPosLabel, 0, 0, 1, 1)
    kfWidgetLayout.addWidget(self.xPosLineEdit, 0, 1, 1, 1)
    kfWidgetLayout.addWidget(yPosLabel, 1, 0, 1, 1)
    kfWidgetLayout.addWidget(self.yPosLineEdit, 1, 1, 1, 1)
    kfWidgetLayout.addWidget(zPosLabel, 2, 0, 1, 1)
    kfWidgetLayout.addWidget(self.zPosLineEdit, 2, 1, 1, 1)
    if self._show_roll:
      kfWidgetLayout.addWidget(rollLabel, 1, 2, 1, 1)
      kfWidgetLayout.addWidget(self.rollLineEdit, 2, 2, 1, 1)
    kfWidgetLayout.setContentsMargins(10, 5, 10, 5)
    kfWidgetLayout.setSpacing(6)

  @property
  def data(self) -> Dict:
    """
    Data property

    Returns:
      data: Dict
    """

    data = {'x_pose': float(self.xPosLineEdit.text()), 'y_pose': float(self.yPosLineEdit.text()),
            'z_pose': float(self.zPosLineEdit.text())}
    if self._show_roll:
      data['roll'] = float(self.rollLineEdit.text())

    return data

  @data.setter
  def data(self, value: Dict) -> None:
    """
    Data setter

    Arguments:
      value: Dict
    """

    self.xPosLineEdit.setText(f"{value['x_pose']*1000:.2f}")
    self.yPosLineEdit.setText(f"{value['y_pose']*1000:.2f}")
    self.zPosLineEdit.setText(f"{value['z_pose']*1000:.2f}")
    if 'c_pose' in value and self._show_roll:
      self.rollLineEdit.setText(f"{value['c_pose']:.2f}")


class KeyFramesDelegate(QStyledItemDelegate):

  """
  Subclassed QStyleItemDelegate to create a class to manage the KeyFrames data.

  Keyword Arguments:
    parent: QWidget
      parent widget

  Signals:
    editor_data: Signal(dict)
      signal emitted to publish the data of the editor widget
  """

  editor_data = Signal(dict)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(KeyFramesDelegate, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    self._show_roll = kwargs.get('show_roll', False)
    self.setObjectName(u"keyFramesDelegate")

  def paint(self, painter: QPainter, option: QStyleOptionViewItem,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    if isinstance(self._parent, QAbstractItemView) and self._parent.model is index.model():
      self.parent().openPersistentEditor(index)
    return super(KeyFramesDelegate, self).paint(painter, option, index)

  def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    """
    Reimplemented method to create an editor widget.
    """

    if not index.isValid():
      return

    self.kf_widget = KeyFramesWidget(parent=parent, logger=self._logger, show_roll=self._show_roll)

    return self.kf_widget

  def setEditorData(self, editor: QWidget,
                    index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Re-implemented the method to set the data of editor widget. This method is called when a
    row is added to the Model/View widget.
    """

    if not index.isValid():
      return

    if isinstance(editor, KeyFramesWidget):
      data = json.loads(index.data(role=StandardItem.DATA_ROLE))
      editor.data = data
      data['index'] = index.row()
      self.editor_data.emit(data)

  def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Re-implemented the method to set the data of the model. This method is called when a
    editor widget's data being updated.
    """

    if not index.isValid():
      return

    if isinstance(editor, KeyFramesWidget):
      data = editor.data
      model.setData(index, json.dumps(data), StandardItem.DATA_ROLE)
      data['index'] = index.row()
      self.editor_data.emit(data)

  def sizeHint(self, option: QStyleOptionViewItem,
               index: Union[QModelIndex, QPersistentModelIndex]) -> QSize:
    """
    Re-implemented the method to return the editor widget size. This method is called when
    editor widget is resized.
    """

    size = super(KeyFramesDelegate, self).sizeHint(option, index)
    size.setHeight(80)
    return size


class KeyFramesTableViewModel(QStandardItemModel):

  """
  Subclassed QStandardItemModel to create KeyFramesTableViewModel.
  """

  def __init__(self) -> None:
    super(KeyFramesTableViewModel, self).__init__()

    self.root_node = self.invisibleRootItem()

  def clear(self) -> None:
    """
    Method to clear data from the Model.
    """

    # Remove all rows but not the header
    self.removeRows(0, self.rowCount())

  def add_item(self, item: Union[Dict, None]=None) -> None:
    """
    Method to add items into the table model.

    item: Union[Dict, None]
      table model item
    """

    if item is None:
      return

    column = StandardItem(tooltip=item['path_of'])
    column.setData(json.dumps({k: item[k] for k in item if k != 'path_of'}),
                   StandardItem.DATA_ROLE)
    self.root_node.appendRow(column)


class KeyFramesTableView(TableViewWidget):

  """
  Subclassed TableViewWidget to create KeyFramesTableView to manage the KeyFrames data.

  Keyword Arguments:
    parent: QWidget
      parent widget of the TableView
    logger: Logger
      logger class
    settings: QSettings
      settings of the TableView
    table_name: str
      name of the TableView
    table_model: QStandardItemModel
      model of the TableView

  Signals:
    invalid_item_selected: Signal()
      Signal emits when an invalid item selected or no item selected
    table_view_empty: Signal()
      Signal emits when the Table View gets empty
    key_frames_data: Signal(list)
      Signal emits to publish the key frames data
  """

  key_frames_data = Signal(list)

  def __init__(self, **kwargs) -> None:
    self._logger = kwargs['logger']
    kwargs['table_name'] = 'key_frames_table'
    kwargs['table_model'] = KeyFramesTableViewModel()
    super(KeyFramesTableView, self).__init__(**kwargs)

    # Delegate
    self.key_frame_delegate = KeyFramesDelegate(parent=self, logger=self._logger,
                                                show_roll=kwargs.get('show_roll', False))
    # self.key_frame_delegate.editor_data.connect(lambda data: self.key_frames_data.emit(data))

    # Setup the Table View
    self.setItemDelegate(self.key_frame_delegate)
    self.setContextMenuPolicy(Qt.CustomContextMenu)
    self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
    self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    self.model.itemChanged.connect(self._on_item_changed)

  def _update_data(self) -> None:
    """
    Method to cache data after items are added and removed.
    """

    try:
      _data = []
      for row in range(self.model.rowCount()):
        _data.append([])
        for col in range(self.model.columnCount()):
          idx = self.model.index(row, col)
          _data[row].append(json.loads(self.model.data(idx, role=StandardItem.DATA_ROLE)))
    except Exception:
      self._logger.exception("Unable to update data because:")
    else:
      # self._logger.info(f"Updated data: {_data}")
      self.key_frames_data.emit(_data)

  def add_item(self, data: Union[Any, Dict]=None) -> None:
    """
    Method to add items into the table.

    Arguments:
      item: Dict
        item data
    """

    super(KeyFramesTableView, self).add_item(data)
    self._update_data()
    self.resizeRowsToContents()
    self.scrollToBottom()

  def remove_row(self, indexes: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Method to remove a row from the table

    Arguments:
      indexes: Union[QModelIndex, QPersistentModelIndex]
        indexes of the rows selected
    """

    super(KeyFramesTableView, self).remove_row(indexes)
    self._update_data()

  def _on_item_changed(self, item: StandardItem) -> None:
    """
    Slot/Method called when an item is updated or changed.

    Arguments:
      item: StandardItem
        StandardItem class
    """

    self._update_data()


if __name__ == '__main__':
  # For development purpose only
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  app.setAttribute(Qt.AA_UseHighDpiPixmaps)
  # Create an instance of subclassed QWidget
  kf_widget = KeyFramesWidget(parent=None, show_roll=True)
  # Show the widget
  kf_widget.show()
  # execute the program
  sys.exit(app.exec())