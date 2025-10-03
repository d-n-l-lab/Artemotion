## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including sub Widget classes required for AnimPlotWidgets.py.
##
##############################################################################################
##
import os
import sys
import pyqtgraph as pg

from typing import List

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout


class AnimPlotter(QFrame):

  """
  Subclassed QFrame to create a class to manage the plotting of animation data.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      settings of the widget
    logger: Logger
      logger class
  """

  FRAME_RATE = 25 # in fps

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(AnimPlotter, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # settings
    self._settings = kwargs.get('settings', None)

    # Assign attributes to the frame
    self.setObjectName(u"animPlotter")
    if self._parent is None:
      self.resize(QSize(700, 340))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self._init_UI()

  def _init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # create layout
    animPlotterLayout = QVBoxLayout(self)
    animPlotterLayout.setObjectName(u"animPlotWidgetLayout")

    self.plot_item = AnimPlotItem()
    self.plot_widget = AnimPlotWidget(logger=self._logger, parent=self, plotItem=self.plot_item)

    # Add widgets to layout & set margins
    animPlotterLayout.addWidget(self.plot_widget)
    animPlotterLayout.setContentsMargins(0, 0, 0, 0)
    animPlotterLayout.setSpacing(0)

  @property
  def total_time(self) -> float:
    """
    Property: total time

    Returns
      total_time: float
        returns the total time set in the plot
    """

    total_time = round(self.plot_item.curr_frame_line.value() / self.FRAME_RATE, 3)
    return total_time * 1000


class AnimPlotItem(pg.PlotItem):

  """
  Subclassed pyqtgraph PlotItem class to create this class to manage the various plot items. Refer
  pyqtgraph documentation for details.
  """

  def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None,
               axisItems=None, enableMenu=True, **kargs):
    super(AnimPlotItem, self).__init__(parent, name, labels, title, viewBox, axisItems,
                                       enableMenu, **kargs)

    # Infinite lines
    self._x_axis_line = None
    self._y_axis_line = None
    self.curr_frame_line = None

    self._x_axis = self.getAxis('bottom')
    self._y_axis = self.getAxis('left')
    self._setup_x_axis()

    self.showGrid(x=True, y=True, alpha=0.25)

    # Add lines
    self._add_x_line()
    self._add_y_line()
    self._add_current_frame_line()

  def _add_current_frame_line(self) -> None:
    """
    Method to add a vertical infinite line showing current frame.
    """

    self.curr_frame_line = pg.InfiniteLine(pos=0, movable=True,
                                           pen=pg.mkPen({'color': '#FFEC8B', 'width': 1.5}),
                                           hoverPen=pg.mkPen({'color': '#CDC1C5', 'width': 1.5}),
                                           label='{value:.0f}',
                                           labelOpts={'position':0.1, 'color': '#8e9092',
                                                      'fill': '#3c3c3c', 'movable': True,
                                                      'anchors': (-0.25,-0.25)})
    self.addItem(self.curr_frame_line)

  def _add_x_line(self) -> None:
    """
    Method to add a horizontal infinite line showing x axis 0 position.
    """

    _x_axis_line = pg.InfiniteLine(pos=0, angle=0, movable=False,
                                   pen=pg.mkPen({'color': '#F08080', 'width': 1.5}))
    self.addItem(_x_axis_line)

  def _add_y_line(self) -> None:
    """
    Method to add a horizontal infinite line showing x axis 0 position.
    """

    _y_axis_line = pg.InfiniteLine(pos=0, movable=False,
                                   pen=pg.mkPen({'color': '#00CD66', 'width': 1.5}))
    self.addItem(_y_axis_line)

  def _setup_x_axis(self) -> None:
    """
    Method to 
    """

    pen = pg.mkPen(color='#8e9092', width=1.5)
    self._x_axis.setTextPen(pen)
    self._x_axis.setTickPen(pen)


class AnimPlotWidget(pg.PlotWidget):
  """
  Subclassed PyQtGraph PlotWidget to create a class to manage the plotting of animation data.

  Keyword Arguments:
    parent: QWidget
      parent widget
    logger: Logger
      logger class
  """

  def __init__(self, logger=None, parent=None, background='default', plotItem: pg.PlotItem=None,
               **kargs):
    self._parent = kargs.get('parent', None)
    super().__init__(parent, background, plotItem, **kargs)

    # logger
    self._logger = logger

    # setup widget
    pg.setConfigOptions(antialias=True)
    self.setBackground('#464646')

    # setup the plot
    self._plot = plotItem

    # Setup axes
    self.setup_x_axis(range=[0, 700])
    self.setup_y_axis(range=[0, 100])

  def setup_x_axis(self, range: List[int], padding: float=0.05) -> None:
    """
    Method to setup the X axis i.e bottom axis.

    Aruments:
      range: List[int]
        range of the values to initialize the axis
    """

    if not range:
      return

    self.setXRange(range[0], range[1], padding)

  def setup_y_axis(self, range: List[int], padding: float=0.05) -> None:
    """
    Method to setup the Y axis i.e left axis.

    Aruments:
      range: List[int]
        range of the values to initialize the axis
    """

    if not range:
      return

    self.setYRange(range[0], range[1], padding)

  def close(self):
    """
    Method called when the widget is closed.    
    """

    return super(AnimPlotWidget, self).close()


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of top bar
  plotter = AnimPlotter(logger=None)
  # Show the top bar
  plotter.show()
  # execute the program
  sys.exit(app.exec())