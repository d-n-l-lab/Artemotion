## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including sub Widget classes required for SimRobCtrlWidget.
##
##############################################################################################
##
import os
import sys

from PySide6.QtCore import Signal, QSize, Qt
from PySide6.QtWidgets import QApplication, QFrame, QWidget, QSlider, QHBoxLayout

try:
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget, LineEditWidget, PushButtonWidget
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget, LineEditWidget, PushButtonWidget


class SimRobCtrlSliderWidget(QFrame):

  """
  Class to manage various widgets to control/manipulate thetas/pose values of the robot.

  Keyword Arguments:
    parent: QWidget
      parent widget
    logger : Logger
      Logger class
    bttn_size: QSize
      maximum size of the button

  Signals:
    value_modified: Signal()
      signal emitted when the value of the slider is modified either by slider or buttons
  """

  value_modified = Signal()

  def __init__(self, **kwargs) -> None:
    super(SimRobCtrlSliderWidget, self).__init__(parent=kwargs.get('parent', None))

    self._logger = kwargs['logger']
    self._parent = kwargs.get('parent', None)

    # Setup the widget frame
    self.setFrameShape(QFrame.NoFrame)
    self.setFrameShadow(QFrame.Raised)
    self.setObjectName(u"simRobCtrlSliderWidget")

    # Slider Attributes
    self._min = -360.0 # in Degrees
    self._max = 360.0 # in Degrees
    self._interval = 1

    # Button attributes
    self._bttn_max_size = kwargs.get('bttn_size', QSize(20, 20))

    self._init_UI()

  def _init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create layout
    simRobCtrlSliderWdgtLayout = QHBoxLayout(self)
    simRobCtrlSliderWdgtLayout.setObjectName(u"simRobCtrlSliderWdgtLayout")

    # Create Widgets
    self._create_slider()
    self._create_slider_ctrl_buttons()

    # Add widgets to layout & set margins
    simRobCtrlSliderWdgtLayout.addWidget(self.negValButton)
    simRobCtrlSliderWdgtLayout.addWidget(self.slider)
    simRobCtrlSliderWdgtLayout.addWidget(self.posValButton)
    simRobCtrlSliderWdgtLayout.setContentsMargins(0, 0, 0, 0)
    simRobCtrlSliderWdgtLayout.setSpacing(0)

  def _create_slider_ctrl_buttons(self) -> None:
    """
    Method to create buttons to control the slider.
    """

    # PushButtons
    self.negValButton = PushButtonWidget(parent=self._parent, logger=self._logger,
                                         type="neg_button", maxsize=self._bttn_max_size)
    self.negValButton.clicked.connect(self._handle_neg_value_bttn_clicked)
    self.negValButton.setObjectName(u"negValButton")

    self.posValButton = PushButtonWidget(parent=self._parent, logger=self._logger,
                                         type="pos_button", maxsize=self._bttn_max_size)
    self.posValButton.clicked.connect(self._handle_pos_value_bttn_clicked)
    self.posValButton.setObjectName(u"posValButton")

  def _create_slider(self) -> None:
    """
    Method to create slider.
    """

    self.slider = QSlider(parent=self._parent)
    self.slider.setObjectName(u"slider")
    self.slider.setOrientation(Qt.Horizontal)
    self.slider.valueChanged.connect(self._handle_slider_value_changed)

  @property
  def index(self) -> int:
    """
    Property:
      Returns slider value
    """

    return self.slider.value()

  def set_index(self, index: int) -> None:
    """
    Method to set the index.

    Arguments:
      index: int
        index
    """

    self.slider.setValue(index)

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
    self.slider.setValue(index)

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
  def min(self) -> int | float:
    """
    Property:
      Returns minimum
    """

    return self._min

  @min.setter
  def min(self, value: int | float) -> None:
    """
    Property setter:
      Sets minimum
    """

    self._min = value
    self._range_adjusted()

  @property
  def max(self) -> int | float:
    """
    Property:
      Returns maximum
    """

    return self._max

  @max.setter
  def max(self, value: int | float) -> None:
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
    self.slider.setMaximum(num_of_steps)

  def _handle_slider_value_changed(self) -> None:
    """
    Slot/Method to handle the event when slider value is changed.
    """

    if self.slider.hasFocus():
      self.value_modified.emit()

  def _handle_neg_value_bttn_clicked(self) -> None:
    """
    Slot/Method to handle the event when negative value button is clicked.
    """

    value = self.value() - (self._interval * 100)
    self.set_value(value)
    self.value_modified.emit()

  def _handle_pos_value_bttn_clicked(self) -> None:
    """
    Slot/Method to handle the event when positive value button is clicked.
    """

    value = self.value() + (self._interval * 100)
    self.set_value(value)
    self.value_modified.emit()


class SimRobCtrlWdgtsLayout(QHBoxLayout):

  """
  Class to manage the horizontal layout containing various widgets to control/manipulate
  theta value of the robot.

  Constants:
    LE_W: int
      LineEdit width
    LBL_W: int
      Label width
    LIM_LBL_W: int
      Limit Label width
    WDGT_H: int
      Widets' height
    VALUE_PRECISION: float
      precision of slider value

  Keyword Arguments:
    parent: QWidget
      parent widget
    logger: Logger
      logger class
    lbl_txt: str
      text for label
    show_limits: bool
      flag to show the limit widgets
  """

  # Constants
  LE_W = 45
  LBL_W = 30
  LIM_LBL_W = 70
  WDGT_H = 20
  VALUE_PRECISION = 0.1

  def __init__(self, **kwargs) -> None:
    super(SimRobCtrlWdgtsLayout, self).__init__()

    # logger
    self._logger = kwargs['logger']

    # parent
    self._parent = kwargs.get('parent', None)

    # attributes
    self._lbl_txt = kwargs.get('lbl_txt', '')
    self._show_limits = kwargs.get('show_limits', False)

    # setup the layout
    self.setObjectName(u"thetaCtrlLayout")

    # initialize layout
    self._init_layout()

  def _init_layout(self) -> None:
    """
    Method to initialize the layout.
    """

    # Create Widgets
    label = LabelWidget(parent=self._parent, logger=self._logger, text=self._lbl_txt,
                        maxsize=QSize(self.LBL_W, self.WDGT_H),
                        align=Qt.AlignLeft)
    label.setObjectName(u"label")

    self.lineEdit = LineEditWidget(parent=self._parent, logger=self._logger, type="data", only_float=True,
                                   maxsize=QSize(self.LE_W, self.WDGT_H))
    self.lineEdit.setObjectName(u"lineEdit")

    # Slider Widget
    self.sliderWidget = SimRobCtrlSliderWidget(parent=self._parent, logger=self._logger)
    self.sliderWidget.interval = self.VALUE_PRECISION

    if self._show_limits:
      self.lowLimLabel = LabelWidget(parent=self._parent, logger=self._logger,
                                    maxsize=QSize(self.LIM_LBL_W, self.WDGT_H),
                                    align=Qt.AlignLeft)
      self.lowLimLabel.setObjectName(u"lowLimLabel")
      self.upLimLabel = LabelWidget(parent=self._parent, logger=self._logger,
                                    maxsize=QSize(self.LIM_LBL_W, self.WDGT_H),
                                    align=Qt.AlignRight)
      self.upLimLabel.setObjectName(u"upLimLabel")

    # Add widgets to layout & set margins
    self.addWidget(label)
    self.addWidget(self.lineEdit)
    if self._show_limits: self.addWidget(self.lowLimLabel)
    self.addWidget(self.sliderWidget)
    if self._show_limits: self.addWidget(self.upLimLabel)
    self.setContentsMargins(0, 0, 0, 0)
    self.setSpacing(2)


if __name__ == '__main__':
  # For development purpose only
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  app.setAttribute(Qt.AA_UseHighDpiPixmaps)
  # Create an instance of subclassed QWidget
  widget = QWidget()
  layout = SimRobCtrlWdgtsLayout(parent=widget)
  widget.setLayout(layout)
  # Show the widget
  widget.show()
  # execute the program
  sys.exit(app.exec())