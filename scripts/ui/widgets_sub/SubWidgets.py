## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various widget classes sub-classed from various widgets'
##              classes from PySide library.
##
##############################################################################################
##
import sys

from typing import Any, List, Union

from PySide6.QtGui import (QStandardItem, QColor, QFont, QMouseEvent, QCloseEvent, QIntValidator,
                           QDoubleValidator)
from PySide6.QtCore import QSize, QModelIndex, QPersistentModelIndex, Signal, QEvent, Qt
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QPushButton, QLabel, QLineEdit,
                               QComboBox, QCheckBox, QTreeView, QTableView, QAbstractItemView,
                               QHeaderView, QVBoxLayout, QHBoxLayout, QSlider, QSpacerItem,
                               QSizePolicy)


class LabelWidget(QLabel):

  """
  Subclassed QLabel class to customize the labels used in the UI.

  Keyword Arguments:
    parent: QWidget
      parent widget of the label
    logger: Logger
      logger class
    text: str
      label text
    type: str
      type property of the label
    minsize: QSize
      minimum size of the label
    maxsize: QSize
      maximum size of the label
    align: Qt.Alignment
      Alignment of the text of the label
  """

  def __init__(self, **kwargs) -> None:
    super(LabelWidget, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    if 'text' in kwargs:
      self.setText(kwargs.get('text', ''))
    if 'type' in kwargs:
      if kwargs['type'] == 'dummy_label':
        self.setEnabled(False)
      self.setProperty("type", kwargs.get('type', ''))
    if 'minsize' in kwargs:
      self.setMinimumSize(kwargs['minsize'])
    if 'maxsize' in kwargs:
      self.setMaximumSize(kwargs['maxsize'])
    if 'align' in kwargs:
      self.setAlignment(kwargs['align'])

  def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
    """
    Method called to process mouse release event.

    event: QMouseEvent
      mouse release event
    """

    return super(LabelWidget, self).mouseReleaseEvent(ev)


class LineEditWidget(QLineEdit):

  """
  Subclassed QLineEdit class to customize the LineEdit used in the UI.

  Keyword Arguments:
    parent: QWidget
      parent widget of the lineedit
    logger: Logger
      logger class
    ph_text: str
      placeholder text of the linedit
    type: str
      type property of the linedit
    minsize: QSize
      minimum size of the linedit
    maxsize: QSize
      maximum size of the linedit
    only_int: bool
      enable validator type int
    only_float: bool
      enable validator type float
    min_value: Union[int, float]
      minimum limit value
    max_value: Union[int, float]
      maximum limit value

  Signals:
    text_modified: Signal(str)
      signal emitted when text is modified when widget has focus
  """

  text_modified = Signal(str)

  def __init__(self, **kwargs) -> None:
    super(LineEditWidget, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    self.new_text = ''
    self.editingFinished.connect(self._handle_editing_finished)

    self._setup_defaults(**kwargs)

  def _setup_defaults(self, **kwargs) -> None:
    """
    Method to setup the default parameters of the Label Widget.

    Keyword Arguments:
      ph_text: str
        placeholder text of the linedit
      type: str
        type property of the linedit
      minsize: QSize
        minimum size of the linedit
      maxsize: QSize
        maximum size of the linedit
      only_int: bool
        enable validator type int
      only_float: bool
        enable validator type float
      min_value: Union[int, float]
        minimum limit value
      max_value: Union[int, float]
        maximum limit value
    """

    if 'ph_text' in kwargs:
      self.setPlaceholderText(kwargs.get('ph_text', ''))
    if 'type' in kwargs:
      if kwargs['type'] == 'dummy_line_edit':
        self.setEnabled(False)
      self.setProperty("type", kwargs.get('type', ''))
    if 'minsize' in kwargs:
      self.setMinimumSize(kwargs['minsize'])
    if 'maxsize' in kwargs:
      self.setMaximumSize(kwargs['maxsize'])
    self._only_int = kwargs.get('only_int', False)
    if self._only_int:
      self._min = kwargs.get('min_value', 0)
      self._max = kwargs.get('min_value', 100)
    self._only_float = kwargs.get('only_float', False)
    if self._only_float:
      self._min = kwargs.get('min_value', -100)
      self._max = kwargs.get('min_value', 100)
    self._setup_validators()
    self.setAlignment(Qt.AlignCenter)
    self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))

  def _setup_validators(self) -> None:
    """
    Method to setup the validators.
    """

    # Int Validator
    if self._only_int:
      self._validator = QIntValidator(bottom=self._min, top=self._max)
      self.setValidator(self._validator)

    # Float Validator
    if self._only_float:
      self._validator = QDoubleValidator(bottom=self._min, top=self._max, decimals=2)
      self.setValidator(self._validator)

    # Connections
    if self._only_int or self._only_float:
      self.textChanged.connect(self._new_text)

  def _new_text(self, text: Any) -> None:
    """
    Slot to set the new text.

    Arguments:
      text: str
        valid text
    """

    if not self.hasFocus() and self.hasAcceptableInput():
      self.new_text = text

  def _check_validator(self) -> None:
    """
    Method to check the validator & accordingly set the text.
    """

    if self.new_text is not None:
      if self._only_int:
        self.setText(
          str(min(max(int(self.text()), self.validator().bottom()), self.validator().top()))
        )
      if self._only_float:
        self.setText(
          str(min(max(float(self.text()), self.validator().bottom()), self.validator().top()))
        )

  def _handle_editing_finished(self) -> None:
    """
    Slot/Method to handle the event when editing finished signal is emitted.
    """

    before, after = self.new_text, self.text()
    if before != after:
      self._before = after
      self.text_modified.emit(after)

  @property
  def min(self) -> Union[int, float]:
    """ Property: minimum value allowed """

    return self._min

  @min.setter
  def min(self, value: Union[int, float]) -> None:
    """ Property: minimum value setter """

    self._min = value
    self._setup_validators()

  @property
  def max(self) -> Union[int, float]:
    """ Property: maximum value allowed """

    return self._max

  @max.setter
  def max(self, value: Union[int, float]) -> None:
    """ Property: maximum value setter """

    self._max = value
    self._setup_validators()

  def event(self, event: QEvent) -> bool:
    """
    Method called to process an event.

    event: QEvent
      event
    """

    if event.type() == QEvent.KeyPress:
      key = event.key()
      if not self.hasAcceptableInput() and (key == Qt.Key_Tab or key == Qt.Key_Return or
                                            key == Qt.Key_Enter):
        self._check_validator()
    return super(LineEditWidget, self).event(event)

  def mousePressEvent(self, ev: QMouseEvent) -> None:
    """
    Method called to process mouse Press event.

    event: QMouseEvent
      mouse press event
    """

    return super(LineEditWidget, self).mousePressEvent(ev)


class PushButtonWidget(QPushButton):

  """
  Subclassed QPushButton class to customize the PushButton used in the UI.

  Keyword Arguments:
    parent: QWidget
      parent widget of the pushbutton
    logger: Logger
      logger class
    text: str
      text of the pushbutton
    type: str
      type property of the pushbutton
    minsize: QSize
      minimum size of the pushbutton
    maxsize: QSize
      maximum size of the pushbutton
  """

  def __init__(self, **kwargs) -> None:
    super(PushButtonWidget, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    if 'text' in kwargs:
      self.setText(kwargs['text'])
    if 'type' in kwargs:
      self.setProperty("type", kwargs.get('type', ''))
    if 'minsize' in kwargs:
      self.setMinimumSize(kwargs['minsize'])
    if 'maxsize' in kwargs:
      self.setMaximumSize(kwargs['maxsize'])

  def mousePressEvent(self, e: QMouseEvent) -> None:
    """
    Method called to process mouse Press event.

    event: QMouseEvent
      mouse press event
    """

    return super(PushButtonWidget, self).mousePressEvent(e)


class ComboBoxWidget(QComboBox):

  """
  Subclassed QComboBox class to customize the ComboBox used in the UI.

  Keyword Arguments:
    parent: QWidget
      parent widget of the combobox
    logger: Logger
      logger class
    items: list
      items of the combobox
    type: str
      type property of the combobox
    minsize: QSize
      minimum size of the combobox
    maxsize: QSize
      maximum size of the combobox
  """

  def __init__(self, **kwargs) -> None:
    super(ComboBoxWidget, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    if 'items' in kwargs:
      self.addItems(kwargs.get('items', []))
    if 'type' in kwargs:
      self.setProperty("type", kwargs.get('type', ''))
    if 'minsize' in kwargs:
      self.setMinimumSize(kwargs['minsize'])
    if 'maxsize' in kwargs:
      self.setMaximumSize(kwargs['maxsize'])

    self._setup_alignment()

  def _setup_alignment(self):
    """
    Method to setup the alignment of the items.
    """

    # Setup the alignment
    self.setEditable(True)
    self.lineEdit().setReadOnly(True)
    self.lineEdit().setAlignment(Qt.AlignCenter)
    self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
    for item in range(self.count()):
      self.setItemData(item, Qt.AlignCenter, Qt.TextAlignmentRole)

  def showPopup(self) -> None:
    """
    Re-implemented the method to control the pop-up shown.
    """

    popup = self.view().window()
    rect = popup.geometry()
    rect.moveTopLeft(self.mapToGlobal(self.rect().bottomLeft()))
    return super(ComboBoxWidget, self).showPopup()


class CheckBoxWidget(QCheckBox):

  """
  Subclassed QCheckBox class to customize the CheckBox used in the UI.

  Keyword Arguments:
    parent: QWidget
      parent widget of the checkbox
    logger: Logger
      logger class
    text:str
      text of the checkbox
    type:str
      type property of the checkbox
    layout_dir: Qt.LayoutDirection
      layout direction of the checkbox
    minsize: QSize
      minimum size of the checkbox
    maxsize: QSize
      maximum size of the checkbox
  """

  def __init__(self, **kwargs) -> None:
    super(CheckBoxWidget, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    if 'text' in kwargs:
      self.setText(kwargs['text'])
    if 'type' in kwargs:
      self.setProperty("type", kwargs.get('type', ''))
    if 'layout_dir' in kwargs:
      self.setLayoutDirection(kwargs['layout_dir'])
    if 'minsize' in kwargs:
      self.setMinimumSize(kwargs['minsize'])
    if 'maxsize' in kwargs:
      self.setMaximumSize(kwargs['maxsize'])

  def mousePressEvent(self, event: QMouseEvent) -> None:
    """
    Method called to process mouse Press event.

    event: QMouseEvent
      mouse press event
    """

    return super(CheckBoxWidget, self).mousePressEvent(event)


class DialogWidget(QDialog):

  """
  Subclassed QDialog class to customize the Dialog widget used in the UI.

  Keyword Arguments:
    parent: QWidget
      parent widget of the dialog
    settings: QSettings
      settings of the dialog
    logger: Logger
      logger class
    title: str
      title of the dialog

  Signals:
    dialog_closed: Signal()
      signal emitted when dialog is closed
  """

  # Signals
  dialog_closed = Signal()

  def __init__(self, **kwargs) -> None:
    super(DialogWidget, self).__init__(parent=kwargs.get('parent'))

    # logger
    self._logger = kwargs['logger']

    # Setup the dialog
    self.title = kwargs.get('title', '')
    self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

    # Settings
    self._settings = kwargs.get('settings')
    if self._settings is not None:
      self._read_settings()

    self._init_dialog()

    # Move dialog
    def _move_dialog(event: QMouseEvent):
      # Move dialog on left click
      if event.buttons() == Qt.LeftButton:
        self.move(self.pos() + event.globalPosition().toPoint() - self.current_pos)
        self.current_pos = event.globalPosition().toPoint()
        event.accept()

    # Set top frame
    self.dlgTitleFrame.mouseMoveEvent = _move_dialog

  def _read_settings(self):
    """
    Method to read the widget's setting.
    """

    pass

  def _save_settings(self):
    """
    Method to save the widget's setting.
    """

    pass

  def _init_dialog(self):
    """
    Method to initialize the dialog.
    """

    # Create Vertical Layout
    dialogVerticalLayout = QVBoxLayout(self)
    dialogVerticalLayout.setObjectName(u"dialogVerticalLayout")

    # Create frames
    self._create_title_frame()
    self._create_contents_frame()

    # Add widgets to layout & set margins
    dialogVerticalLayout.addWidget(self.dlgTitleFrame)
    dialogVerticalLayout.addWidget(self.dlgContentsFrame)
    dialogVerticalLayout.setContentsMargins(0, 0, 0, 0)
    dialogVerticalLayout.setSpacing(0)

    # Connections
    self._create_local_connects()

  def _create_title_frame(self):
    """
    Method to create the title frame.
    """

    # Title Frame
    self.dlgTitleFrame = QFrame(self)
    self.dlgTitleFrame.setObjectName(u"dlgTitleFrame")
    self.dlgTitleFrame.setMaximumSize(QSize(16777215, 30))
    self.dlgTitleFrame.setFrameStyle(QFrame.NoFrame | QFrame.Plain)

    # Title frame layout
    dlgTitleFrameHorizLayout = QHBoxLayout(self.dlgTitleFrame)
    dlgTitleFrameHorizLayout.setObjectName(u"dlgTitleFrameHorizLayout")

    # Spacer
    dlgTitleHorizSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    # Title label
    dlgTitleLabel = LabelWidget(parent=self.dlgTitleFrame, text=self.title, type="title_label")
    dlgTitleLabel.setObjectName(u"dlgTitleLabel")

    # Minimize button
    self.dlgMinimizeButton = PushButtonWidget(parent=self.dlgTitleFrame, maxsize=QSize(50, 30))
    self.dlgMinimizeButton.setToolTip(u"Minimize")
    self.dlgMinimizeButton.setObjectName(u"dlgMinimizeButton")

    # Close button
    self.dlgCloseButton = PushButtonWidget(parent=self.dlgTitleFrame, maxsize=QSize(50, 30))
    self.dlgCloseButton.setToolTip(u"Close")
    self.dlgCloseButton.setObjectName(u"dlgCloseButton")

    # Add widgets to layout & set margins
    dlgTitleFrameHorizLayout.addWidget(dlgTitleLabel)
    dlgTitleFrameHorizLayout.addItem(dlgTitleHorizSpacer)
    dlgTitleFrameHorizLayout.addWidget(self.dlgMinimizeButton)
    dlgTitleFrameHorizLayout.addWidget(self.dlgCloseButton)
    dlgTitleFrameHorizLayout.setContentsMargins(0, 0, 0, 0)
    dlgTitleFrameHorizLayout.setSpacing(0)

  def _create_contents_frame(self):
    """
    Method to create the contents frame.
    """

    self.dlgContentsFrame = QFrame(self)
    self.dlgContentsFrame.setObjectName(u"dlgContentsFrame")

  def _create_local_connects(self):
    """
    Method to create the connections of local widgets & signals.
    """

    # PushButtons
    self.dlgMinimizeButton.clicked.connect(lambda: self.showMinimized())
    self.dlgCloseButton.clicked.connect(lambda: self.close())

  def mousePressEvent(self, event: QMouseEvent) -> None:
    """
    Method called to process mouse Press event.

    event: QMouseEvent
      mouse press event
    """

    self.current_pos = event.globalPosition().toPoint()
    return super(DialogWidget, self).mousePressEvent(event)

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called at a close event.

    close: QCloseEvent
      close event
    """

    self.dialog_closed.emit()
    return super(DialogWidget, self).closeEvent(event)

  def showMinimized(self) -> None:
    """
    Method called to show widget minimized.
    """

    return super(DialogWidget, self).showMinimized()

  def close(self) -> bool:
    """
    Method called to close.
    """

    return super(DialogWidget, self).close()


class SliderWidget(QSlider):

  """
  Subclassed QDialog class to customize the Dialog widget used in the UI.

  Keyword Arguments:
    parent: QWidget
      parent widget of the dialog
    logger: Logger
      logger class
    min: float
      minimum slider value, default=-1.0
    max: float
      maximum slider value, default=1.0
    interval: int
      slider interval, default=1
    orientation: Qt.Orientation
      orientation of the slider

  Signals:
    value_modified: Signal()
      signal emitted when the value of the slider is modified either by slider
  """

  value_modified = Signal()

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(SliderWidget, self).__init__(parent=self._parent)

    self._logger = kwargs['logger']

    # Slider Attributes
    self._min = kwargs.get('min', -1.0)
    self._max = kwargs.get('max', 1.0)
    self._interval = kwargs.get('interval', 1)

    # setup
    self.setOrientation(kwargs.get('orientation', Qt.Horizontal))

    # connection
    self.valueChanged.connect(self._handle_slider_value_changed)

  @property
  def index(self) -> int:
    """
    Property:
      Returns slider value
    """

    return super(SliderWidget, self).value()

  def set_index(self, index: int) -> None:
    """
    Method to set the index.

    Arguments:
      index: int
        index
    """

    return super(SliderWidget, self).setValue(index)

  def value(self) -> int:
    """
    Method returns the value of the slider.
    """

    return self.index * self._interval + self._min

  def set_value(self, value: int) -> None:
    """
    Method to set a value of the slider.

    Arguments:
      value: int
        value to be set
    """

    index = round((value - self._min) / self._interval)
    return super(SliderWidget, self).setValue(index)

  @property
  def interval(self) -> int:
    """
    Property:
      Returns interval
    """

    return self._interval

  @interval.setter
  def interval(self, value: int) -> None:
    """
    Property setter:
      Sets interval
    """

    if not value:
      raise ValueError("interval of zero specified")
    self._interval = value
    self._range_adjusted()

  @property
  def min(self) -> Union[int, float]:
    """
    Property:
      Returns minimum
    """

    return self._min

  @min.setter
  def min(self, value: Union[int, float]) -> None:
    """
    Property setter:
      Sets minimum
    """

    self._min = value
    self._range_adjusted()

  @property
  def max(self) -> Union[int, float]:
    """
    Property:
      Returns maximum
    """

    return self._max

  @max.setter
  def max(self, value: Union[int, float]) -> None:
    """
    Property setter:
      Sets maximum
    """

    self._max = value
    self._range_adjusted()

  def _range_adjusted(self) -> None:
    """
    Method to adjust the range of the slider.
    """

    num_of_steps = int((self._max - self._min) / self._interval)
    super(SliderWidget, self).setMaximum(num_of_steps)

  def _handle_slider_value_changed(self) -> None:
    """
    Slot/Method to handle the event when slider value is changed.
    """

    if self.hasFocus():
      self.value_modified.emit()


class StandardItem(QStandardItem):

  """
  Subclassed QStandardItem class to customize the StandardItems used in the TreeView/TableView.

  Keyword Arguments:
    logger: Logger
      logger class
    font_size: int
      size of the font of the texts
    set_bold: bool
      flag to set the fonts to bold
    text: str
      text
    tooltip: str
      tooltip
    editable: bool
      flag to set the contents editable
    color: QColor
      color of the fonts

  Constants:
    DATA_ROLE: int
      Data role to save item data
  """

  DATA_ROLE = Qt.UserRole + 1

  def __init__(self, **kwargs) -> None:
    super(StandardItem, self).__init__()

    fnt = QFont('MS Shell Dlg 2', kwargs.get('font_size', 8))
    fnt.setBold(kwargs.get('set_bold', False))
    self.setFont(fnt)

    self.setText(kwargs.get('text', ''))
    self.setToolTip(kwargs.get('tooltip', ''))
    self.setEditable(kwargs.get('editable', False))
    self.setForeground(kwargs.get('color', QColor(0, 0, 0)))

  def setData(self, value: Any, role: int) -> None:
    """
    Method to save the data of an Item for a given role.

    Argument:
      value: Any
        data value
      role: int
        data role
    """

    return super(StandardItem, self).setData(value, role=role)


class TreeViewWidget(QTreeView):

  """
  Subclassed QTreeView class to customize the TreeView used in the UI.

  Keyword Arguments:
    parent: QWidget
      parent widget of the TreeView
    logger: Logger
      logger class
    settings: QSettings
      settings of the TreeView
    tree_name: str
      name of the TreeView
    tree_model: QStandardItemModel
      model of the TreeView

  Signals:
    invalid_item_selected: Signal()
      Signals emits when an invalid item selected or no item selected
  """

  invalid_item_selected = Signal()

  def __init__(self, **kwargs) -> None:
    super(TreeViewWidget, self).__init__(parent=kwargs.get('parent'))

    # logger
    self._logger = kwargs['logger']

    # Load the settings
    self._tree_name = kwargs.get('tree_name', '')
    try:
      self._settings = kwargs.get('settings')
      state = self._settings.value(self._tree_name + "_state", None)
      if state is not None:
        self.header().restoreState()
    except Exception:
      # SubUILogger.info("Working with default settings")
      pass

    # Set the model
    self.model = kwargs.get('tree_model')
    if self.model is not None:
      self.model.clear()
      if len(kwargs.get('header_labels', [])) > 0:
        self.model.setHorizontalHeaderLabels(kwargs.get('header_labels'))
      else:
        self.setHeaderHidden(True)
      self.setModel(self.model)

    # Setup the TreeView
    self.setAlternatingRowColors(True)
    self.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.setSelectionMode(QAbstractItemView.SingleSelection)

  def clear(self) -> None:
    """
    Method to clear the data from the Tree View
    """

    self.model.clear()

  def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> Any:
    """
    Method to get the data from the TreeView.

    Arguments:
      index: Union[QModelIndex, QPersistentModelIndex]
        index of an item in the TreeView
      role: int
        data role

    Returns
      data: Any
        data of an item
    """

    return self.model.data(index, role)

  def mousePressEvent(self, event: QMouseEvent) -> None:
    """
    Method called to process mouse Press event.

    event: QMouseEvent
      mouse press event
    """

    item = self.indexAt(event.position().toPoint())
    if not item.isValid():
      self.clearSelection()
      self.invalid_item_selected.emit()
    return super(TreeViewWidget, self).mousePressEvent(event)

  def save_state(self) -> None:
    """
    Method to save the settings of the TreeView before exiting.
    """

    if self._settings is not None:
      self._settings.setValue(self._tree_name + "_state", self.header().saveState())

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called at a close event.

    close: QCloseEvent
      close event
    """

    self.save_state()
    return super(TreeViewWidget, self).closeEvent(event)


class TableViewWidget(QTableView):

  """
  Subclassed QTableView class to customize the TableView used in the UI.

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
  """

  invalid_item_selected = Signal()
  table_view_empty = Signal()
  removed_row = Signal(int)

  def __init__(self, **kwargs) -> None:
    super(TableViewWidget, self).__init__(parent=kwargs.get('parent'))

    self._items = []
    self._logger = kwargs['logger']

    # Load the settings
    self._table_name = kwargs.get('table_name', '')
    try:
      self._settings = kwargs.get('settings')
      state = self._settings.value(self._table_name + "_state", None)
      if state is not None:
        self.horizontalHeader().restoreState(state)
    except:
      # SubUILogger.info("Working with default settings.")
      pass

    # Set the model
    self.model = kwargs.get('table_model')
    if self.model is not None:
      self.model.clear()
      if len(kwargs.get('header_labels', [])) > 0:
        self.model.setHorizontalHeaderLabels(kwargs.get('header_labels'))
      else:
        self.horizontalHeader().hide()
      self.setModel(self.model)

    # Setup the Table View
    self.horizontalHeader().setStretchLastSection(True)
    self.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.setSelectionMode(QAbstractItemView.SingleSelection)
    self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

  def remove_row(self, indexes: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Method to remove a row from the table. Reimplement this method in subclass if required.

    Arguments:
      indexes: Union[QModelIndex, QPersistentModelIndex]
        indexes of the rows selected
    """

    for index in indexes:
      if not index.isValid():
        return
      self.model.removeRow(index.row())
      del self._items[index.row()]
      self.removed_row.emit(index.row())
    if self.model.rowCount() == 0:
      self.table_view_empty.emit()

  def add_item(self, data: Any) -> None:
    """
    Method to add an item in the TableView. Reimplement this method in subclass if required.

    data: Any
      data item
    """

    if data in self._items:
      return

    try:
      self.model.add_item(data)
      self.resizeColumnsToContents()
      self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    except Exception:
      self._logger.exception(f"Unable to add an item {data} because:")
    else:
      self._items.append(data)

  @property
  def items(self) -> List:
    """
    Items property.

    Returns:
      items: List
        list containing all the items of the Table view
    """

    return self._items

  def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> Any:
    """
    Method to get the data from the TableView.

    Arguments:
      index: Union[QModelIndex, QPersistentModelIndex]
        index of an item in the TreeView
      role: int
        data role

    Returns
      data: Any
        data of an item
    """

    return self.model.data(index, role)

  def clear(self) -> None:
    """
    Method to clear the data from the Table View
    """

    self.model.clear()

  def save_state(self) -> None:
    """
    Method to save the settings of the TreeView before exiting.
    """

    self._settings.setValue(self._table_name + "_state", self.horizontalHeader().saveState())

  def mousePressEvent(self, event: QMouseEvent) -> None:
    """
    Method called to process mouse Press event.

    event: QMouseEvent
      mouse press event
    """

    item = self.indexAt(event.pos())
    if not item.isValid():
      self.clearSelection()
      self.invalid_item_selected.emit()
    return super(TableViewWidget, self).mousePressEvent(event)

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called at a close event.

    close: QCloseEvent
      close event
    """

    self.save_state()
    return super(TableViewWidget, self).closeEvent(event)


if __name__ == '__main__':
  # For development purpose only
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  app.setAttribute(Qt.AA_UseHighDpiPixmaps)
  # Create an instance of subclassed QWidget
  dialog_widget = DialogWidget()
  # Show the widget
  dialog_widget.show()
  # execute the program
  sys.exit(app.exec())