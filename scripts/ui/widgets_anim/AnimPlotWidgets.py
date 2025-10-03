## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes & functions managing the Animation Graph Widgets.
##
##############################################################################################
##
import os
import sys

from typing import List, Dict

from PySide6.QtGui import QCloseEvent, QResizeEvent
from PySide6.QtCore import QSize, Signal, Qt
from PySide6.QtWidgets import QApplication, QFrame, QSplitter, QVBoxLayout, QHBoxLayout

try:
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget
  from scripts.ui.widgets_sub.anim.AnimPlotSubWidgets import AnimPlotter
except:
  # For the development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import PushButtonWidget
  from scripts.ui.widgets_sub.anim.AnimPlotSubWidgets import AnimPlotter


class DummyLogger(Logger):

  pass


class AnimDataVizWidget(QFrame):

  """
  Class to manage the widgets to display the plots and data of keyframes and path data.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      settings of the widget
    logger: Logger
      logger class

  Signals:
    add_key_frame: Signal()
      signal emitted when add key frame is requested
    delete_key_frame: Signal()
      signal emitted when delete key frame is requested
    update_keyframes_with_total_time: Signal(float, list)
      signal emitted to update key frame with total animation time
  """

  add_key_frame = Signal()
  delete_key_frame = Signal()
  update_keyframes_with_total_time = Signal(float, list)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(AnimDataVizWidget, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # settings
    self._settings = kwargs.get('settings', None)

    # Assign attributes to the frame
    self.setObjectName(u"animGraphWidget")
    if self._parent is None:
      self.resize(QSize(1000, 340))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    # Added robots
    self._added_robots = [] # list of robots added into the UI

    self.init_UI()

  def init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # Create AnimGraph widget layout
    animDataVizWidgetLayout = QVBoxLayout(self)
    animDataVizWidgetLayout.setObjectName(u"animDataVizWidgetLayout")

    # Create Main Splitter
    self.mainHorizSplitter = QSplitter(Qt.Horizontal, parent=self)
    self.mainHorizSplitter.setObjectName(u"mainHorizSplitter")

    # tree view widget
    self.anim_tree_view_widget = AnimTreeViewWidget(parent=self._parent, settings=self._settings,
                                                    logger=self._logger)

    # plot widget
    self.anim_plot_view_widget = AnimPlotViewWidget(parent=self._parent, settings=self._settings,
                                                    logger=self._logger)

    # Add Widgets to splitter
    self.mainHorizSplitter.addWidget(self.anim_tree_view_widget)
    self.mainHorizSplitter.addWidget(self.anim_plot_view_widget)

    # Setup splitter size
    self.mainHorizSplitter.setSizes([0, self.width()])

    # Add widgets to layout & set margins
    animDataVizWidgetLayout.addWidget(self.mainHorizSplitter)
    animDataVizWidgetLayout.setContentsMargins(0, 0, 0, 0)
    animDataVizWidgetLayout.setSpacing(0)

    # Connections
    self._create_plot_view_wdgt_connections()

  def _create_plot_view_wdgt_connections(self) -> None:
    """
    Method to create plot view widget connections.
    """

    # PushButtons
    self.anim_plot_view_widget.addKFButton.clicked.connect(lambda: self.add_key_frame.emit())
    self.anim_plot_view_widget.delKFButton.clicked.connect(lambda: self.delete_key_frame.emit())

  def on_robots_got_added(self, robots: List) -> None:
    """
    Slot/Method called when robot configuration received.

    Arguments:
      robots: List
        list containing robots added
    """

    if not robots:
      return

    self._added_robots = robots
    self.anim_plot_view_widget.addKFButton.setEnabled(len(self._added_robots) > 0)

  def on_updated_robot_keyframes_data_recvd(self, kf: List) -> None:
    """
    Slot/Method called when updated keyframes of robot path is received.

    Arguments:
      kf: List
        list containing updated keyframes data
    """

    if not kf:
      return

    # To-Do: Add data to the TreeView of anim_tree_view_widget
    self.update_keyframes_with_total_time.emit(self.anim_plot_view_widget.plotter.total_time, kf)

  def save_state(self) -> None:
    """
    Method to save the state before exiting.
    """

    pass

  def resizeEvent(self, event: QResizeEvent) -> None:
    """
    Method called when widget is resized.
    """

    self.mainHorizSplitter.setSizes([0, self.width()])
    return super(AnimDataVizWidget, self).resizeEvent(event)

  def closeEvent(self, event: QCloseEvent) -> None:
    """
    Method called when widget is closed.    
    """

    self.save_state()
    return super(AnimDataVizWidget, self).closeEvent(event)


class AnimTreeViewWidget(QFrame):

  """
  Class to manage plotting of the animation data.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      settings of the widget
    logger: Logger
      logger class
  """

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(AnimTreeViewWidget, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # settings
    self._settings = kwargs.get('settings', None)

    # Assign attributes to the frame
    self.setObjectName(u"animTreeViewWidget")
    if self._parent is None:
      self.resize(QSize(300, 340))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self._init_UI()

  def _init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # create layout
    animTreeViewWidgetLayout = QVBoxLayout(self)
    animTreeViewWidgetLayout.setObjectName(u"animPlotWidgetLayout")

    # Add widgets to layout & set margins
    animTreeViewWidgetLayout.addLayout(self._create_bottom_ribbon_layout())
    animTreeViewWidgetLayout.setContentsMargins(0, 0, 0, 0)
    animTreeViewWidgetLayout.setSpacing(0)

  def _create_bottom_ribbon_layout(self) -> QHBoxLayout:
    """
    Method to create bottom ribbon layout to manage various widgets.
    """

    # Create bottom layout
    animPlotWidgetBottomRibbonLayout = QHBoxLayout()
    animPlotWidgetBottomRibbonLayout.setObjectName(u"animPlotWidgetBottomRibbonLayout")

    # Create curve copy/paste bttns layout
    curveCopyPasteBttnsLayout = QHBoxLayout()
    curveCopyPasteBttnsLayout.setObjectName(u"curveCopyPasteBttnsLayout")

    # Copy button
    self.copyCurveBttn = PushButtonWidget(parent=self, logger=self._logger, text=u"Copy Curve",
                                          type="left_button", maxsize=QSize(100, 20))
    self.copyCurveBttn.setObjectName(u"copyCurveBttn")

    # Paste button
    self.pasteCurveBttn = PushButtonWidget(parent=self, logger=self._logger, text=u"Paste Curve",
                                           type="right_button", maxsize=QSize(100, 20))
    self.pasteCurveBttn.setObjectName(u"pasteCurveBttn")

    # Add widgets to layout & set margins
    curveCopyPasteBttnsLayout.addWidget(self.copyCurveBttn)
    curveCopyPasteBttnsLayout.addWidget(self.pasteCurveBttn)
    curveCopyPasteBttnsLayout.setContentsMargins(6, 0, 6, 0)
    curveCopyPasteBttnsLayout.setSpacing(10)

    # Clear Curve button
    self.clearCurveBttn = PushButtonWidget(parent=self, logger=self._logger, text=u"Clear Curve",
                                           type="round_button", maxsize=QSize(100, 20))
    self.clearCurveBttn.setObjectName(u"clearCurveBttn")

    # Add widgets to layout & set margins
    animPlotWidgetBottomRibbonLayout.addLayout(curveCopyPasteBttnsLayout)
    animPlotWidgetBottomRibbonLayout.addWidget(self.clearCurveBttn)
    animPlotWidgetBottomRibbonLayout.setContentsMargins(6, 6, 6, 6)
    animPlotWidgetBottomRibbonLayout.setSpacing(20)

    return animPlotWidgetBottomRibbonLayout


class AnimPlotViewWidget(QFrame):

  """
  Class to manage plotting of the animation data.

  Keyword Arguments:
    parent: QWidget
      parent widget
    settings: QSettings
      settings of the widget
    logger: Logger
      logger class
  """

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(AnimPlotViewWidget, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # settings
    self._settings = kwargs.get('settings', None)

    # Assign attributes to the frame
    self.setObjectName(u"animPlotWidget")
    if self._parent is None:
      self.resize(QSize(700, 340))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self._init_UI()

  def _init_UI(self) -> None:
    """
    Method to initialize the UI.
    """

    # create layout
    animPlotWidgetLayout = QVBoxLayout(self)
    animPlotWidgetLayout.setObjectName(u"animPlotWidgetLayout")

    self.plotter = AnimPlotter(parent=self, settings=self._settings, logger=self._logger)

    # Add widgets to layout & set margins
    animPlotWidgetLayout.addWidget(self.plotter)
    animPlotWidgetLayout.addLayout(self._create_bottom_ribbon_layout())
    animPlotWidgetLayout.setContentsMargins(0, 0, 0, 0)
    animPlotWidgetLayout.setSpacing(0)

  def _create_keyframes_buttons_layout(self) -> QHBoxLayout:
    """
    Method to create a layout managing the keyframes.

    Returns:
      kf_layout: QHBoxLayout
        keyframes layout
    """

    # Create layout
    kfBttnsLayout = QHBoxLayout()
    kfBttnsLayout.setObjectName(u"kfBttnsLayout")

    self.addKFButton = PushButtonWidget(parent=self, logger=self._logger, text=u"Add KF",
                                        type="left_button", minsize=QSize(0, 20))
    self.addKFButton.setObjectName(u"addKFButton")
    self.addKFButton.setEnabled(False)

    self.delKFButton = PushButtonWidget(parent=self, logger=self._logger, text=u"Delete KF",
                                        type="right_button", minsize=QSize(0, 20))
    self.delKFButton.setObjectName(u"delKFButton")
    self.delKFButton.setEnabled(False)

    # Add widgets to layout & set margins
    kfBttnsLayout.addWidget(self.addKFButton)
    kfBttnsLayout.addWidget(self.delKFButton)
    kfBttnsLayout.setContentsMargins(0, 0, 0, 0)
    kfBttnsLayout.setSpacing(0)

    return kfBttnsLayout

  def _create_bottom_ribbon_layout(self) -> QHBoxLayout:
    """
    Method to create bottom ribbon layout to manage various widgets.
    """

    # Create bottom layout
    animPlotViewWdgtBttmRibbonLayout = QHBoxLayout()
    animPlotViewWdgtBttmRibbonLayout.setObjectName(u"animPlotViewWdgtBttmRibbonLayout")

    # Fit Curves button
    self.fitCurvesBttn = PushButtonWidget(parent=self, logger=self._logger, text=u"Fit Curves",
                                          type="round_button", minsize=QSize(0, 20))
    self.fitCurvesBttn.setObjectName(u"fitCurvesBttn")

    # Add widgets to layout & set margins
    animPlotViewWdgtBttmRibbonLayout.addWidget(self.fitCurvesBttn)
    animPlotViewWdgtBttmRibbonLayout.addLayout(self._create_keyframes_buttons_layout())
    animPlotViewWdgtBttmRibbonLayout.setContentsMargins(6, 6, 6, 6)
    animPlotViewWdgtBttmRibbonLayout.setSpacing(20)

    return animPlotViewWdgtBttmRibbonLayout


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of top bar
  anim_data_viz_wdgt = AnimDataVizWidget(logger=None)
  # Show the top bar
  anim_data_viz_wdgt.show()
  # execute the program
  sys.exit(app.exec())