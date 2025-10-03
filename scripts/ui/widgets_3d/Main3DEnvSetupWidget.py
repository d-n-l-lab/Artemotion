## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including various classes to manage Main 3D Environment setup widget.
##
##############################################################################################
##
import os
import sys
import posixpath

from typing import Any

from PySide6.QtGui import QCloseEvent, Qt
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (QApplication, QFrame, QFormLayout, QHBoxLayout, QVBoxLayout,
                               QGroupBox, QStackedWidget, QLayout)

try:
  from scripts.settings import PathManager
  from scripts.ui.widgets_sub.SubWidgets import (LabelWidget, CheckBoxWidget, LineEditWidget,
                                                 ComboBoxWidget, PushButtonWidget)
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.ui.widgets_sub.SubWidgets import (LabelWidget, CheckBoxWidget, LineEditWidget,
                                                 ComboBoxWidget, PushButtonWidget)


class Main3DEnvSetupWidget(QFrame):

  # Constants
  DEFAULT_WIDTH = 410
  DEFAULT_HEIGHT = 487

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(Main3DEnvSetupWidget, self).__init__(parent=self._parent)

    self._logger =  kwargs['logger']
    self._settings = kwargs.get('settings', None)

    # Setup the top bar
    self.setObjectName(u"main3DEnvSetupWidget")
    self.setWindowTitle(u"Environment Setup")
    if self._parent is None:
      self.resize(QSize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self.init_UI()

    # Set Artemis Control Widget default stylesheet
    self.set_stylesheet()

  def init_UI(self) -> None:
    # Create main layout
    main3DEnvSetupMainLayout = QVBoxLayout(self)
    main3DEnvSetupMainLayout.setObjectName(u"artemisCtrlMainLayout")

    # Create layouts
    titleLayout = self._create_main_3d_title_layout()
    buttonsLayout = self._create_stacked_widget_ctrls_btns_layout()

    # Create widgets
    self._create_stacked_widget()

    # Add widgets to the layout & set margins
    main3DEnvSetupMainLayout.addLayout(titleLayout)
    main3DEnvSetupMainLayout.addLayout(buttonsLayout)
    # main3DEnvSetupMainLayout.addItem(verticalSpacer)
    main3DEnvSetupMainLayout.addWidget(self.main3DEnvStackedWidget)
    main3DEnvSetupMainLayout.setContentsMargins(20, 10, 20, 10)
    main3DEnvSetupMainLayout.setSpacing(20)

  def set_stylesheet(self, theme: str='default', qss: str='Main3DEnvSetupWidget.qss') -> None:
    try:
      # Set the StyleSheet
      qss_file = PathManager.get_qss_path(logger=self._logger,
                                          qss_file=os.path.join(theme, qss))
      icons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.relpath(qss_file)))),
                                "icons", theme)
      with open(qss_file, 'r') as fh:
        style_sheet = fh.read()
        self.setStyleSheet(style_sheet.replace("<icons_path>",
                                              f"{icons_path}".replace(os.sep, posixpath.sep)))
    except FileNotFoundError:
      pass
    except Exception:
      self._logger("Unable to set stylesheet because:")

  def _create_main_3d_title_layout(self) -> None:
    # Create title layout
    main3DTitleHorizLayout = QHBoxLayout()
    main3DTitleHorizLayout.setObjectName(u"main3DTitleHorizLayout")

    # Create title label
    main3DTitleLabel = LabelWidget(parent=self, logger=self._logger,
                                   text=u"3D Environment", minsize=QSize(275, 20),
                                   align=Qt.AlignCenter)
    main3DTitleLabel.setObjectName(u"main3DTitleLabel")

    # Create sticky checkbox
    self.stickyCheckBox = CheckBoxWidget(parent=self, logger=self._logger, text=u"Sticky",
                                         layout_dir=Qt.RightToLeft)
    self.stickyCheckBox.setLayoutDirection(Qt.RightToLeft)

    # Add widgets to layout & set margins
    main3DTitleHorizLayout.addWidget(main3DTitleLabel)
    main3DTitleHorizLayout.addWidget(self.stickyCheckBox)
    main3DTitleHorizLayout.setContentsMargins(0, 0, 0, 0)
    main3DTitleHorizLayout.setSpacing(6)

    return main3DTitleHorizLayout

  def _create_stacked_widget_ctrls_btns_layout(self) -> QLayout:
    # Create layout
    stackedWdgtBtnsHorizLayout = QHBoxLayout()
    stackedWdgtBtnsHorizLayout.setObjectName(u"stackedWdgtBtnsHorizLayout")

    # Pushbuttons
    dummy1PushButton = PushButtonWidget(parent=self, logger=self._logger, minsize=QSize(0, 25))
    dummy1PushButton.setEnabled(False)
    dummy1PushButton.setObjectName(u"dummy1PushButton")

    dummy2PushButton = PushButtonWidget(parent=self, logger=self._logger, minsize=QSize(0, 25))
    dummy2PushButton.setEnabled(False)
    dummy2PushButton.setObjectName(u"dummy2PushButton")

    # Add widgets to horizontal layout & set margins
    stackedWdgtBtnsHorizLayout.addWidget(dummy1PushButton)
    stackedWdgtBtnsHorizLayout.addWidget(dummy2PushButton)
    stackedWdgtBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    stackedWdgtBtnsHorizLayout.setSpacing(0)

    return stackedWdgtBtnsHorizLayout

  def _create_stacked_widget(self) -> None:
    # Create stacked widgets
    self.main3DEnvStackedWidget = QStackedWidget(self)
    self.main3DEnvStackedWidget.setObjectName(u"main3DEnvStackedWidget")

    # Create pages
    self.main3DEnvConfigPage = Main3DEnvConfigPage(parent=self, settings=self._settings,
                                                   logger=self._logger)

    # Add pages
    self.main3DEnvStackedWidget.addWidget(self.main3DEnvConfigPage)

  def save_state(self) -> None:
    pass

  def closeEvent(self, event: QCloseEvent) -> None:
    self.save_state()
    event.accept()
    return super(Main3DEnvSetupWidget, self).closeEvent(event)


class Main3DEnvConfigPageFunc:

  def __init__(self, **kwargs) -> None:
    super(Main3DEnvConfigPageFunc, self).__init__(parent=kwargs.get('parent', None))

    # logger
    self._logger = kwargs['logger']

    # Environment Attributes
    self.env_preset = 'Auto'
    self.env_opacity = 100 # in percentage
    self.env_width = 1000.0 # in centimeters
    self.env_height = 500.0 # in centimeters
    self.env_depth = 1500.0 # in centimeters
    self.env_grid_width = 50.0 # in centimeters
    self.env_grid_height = 50.0 # in centimeters
    self.env_grid_depth = 50.0 # in centimeters
    self.env_origin_x = 0.0 # in centimeters
    self.env_origin_y = 0.0 # in centimeters
    self.env_origin_z = 0.0 # in centimeters
    self.ref_wall_origin_x = 'Left Wall'
    self.ref_wall_origin_y = 'Floor'
    self.ref_wall_origin_z = 'Front Wall'
    self.ambient_color_red = 100 # in percentage
    self.ambient_color_green = 100 # in percentage
    self.ambient_color_blue = 100 # in percentage
    self.ambient_color_alpha = 100 # in percentage

  @staticmethod
  def _is_int(value: Any) -> bool:
    try:
      int(value)
    except ValueError:
      return False

    return True

  @staticmethod
  def _is_float(value: Any) -> bool:
    try:
      float(value)
    except ValueError:
      return False

    return True

  def setup_environment_preset(self, preset: str) -> None:
    self._logger.info(f"Environment Preset: {preset}")
    if preset != self.env_preset:
      self.env_preset = preset

  def setup_environment_opacity(self, opacity: int) -> None:
    if Main3DEnvConfigPageFunc._is_int(opacity):
      if int(opacity) != self.env_opacity:
        self.env_opacity = int(opacity)

  def setup_environment_dimensions(self, w: float, h: float, d: float) -> None:
    if Main3DEnvConfigPageFunc._is_float(w):
      if float(w) != self.env_width:
        self.env_width = float(w)
    if Main3DEnvConfigPageFunc._is_float(h):
      if float(h) != self.env_height:
        self.env_height = float(h)
    if Main3DEnvConfigPageFunc._is_float(d):
      if float(d) != self.env_depth:
        self.env_depth = float(d)

  def setup_env_grid_dimensions(self, g_w: float, g_h: float, g_d: float) -> None:
    if Main3DEnvConfigPageFunc._is_float(g_w):
      if float(g_w) != self.env_grid_width:
        self.env_grid_width = float(g_w)
    if Main3DEnvConfigPageFunc._is_float(g_w):
      if float(g_h) != self.env_grid_height:
        self.env_grid_height = float(g_h)
    if Main3DEnvConfigPageFunc._is_float(g_w):
      if float(g_d) != self.env_grid_depth:
        self.env_grid_depth = float(g_d)

  def setup_environment_origin(self, x: float, y: float, z: float) -> None:
    if Main3DEnvConfigPageFunc._is_float(x):
      if float(x) != self.env_origin_x:
        self.env_origin_x = float(x)
    if Main3DEnvConfigPageFunc._is_float(y):
      if float(y) != self.env_origin_y:
        self.env_origin_y = float(y)
    if Main3DEnvConfigPageFunc._is_float(z):
      if float(z) != self.env_origin_z:
        self.env_origin_z = float(z)

  def setup_reference_walls(self, ref_wall_x: str, ref_wall_y: str, ref_wall_z: str) -> None:
    if ref_wall_x != self.ref_wall_origin_x:
      self.ref_wall_origin_x = ref_wall_x
    if ref_wall_y != self.ref_wall_origin_y:
      self.ref_wall_origin_y = ref_wall_y
    if ref_wall_z != self.ref_wall_origin_z:
      self.ref_wall_origin_z = ref_wall_z

  def setup_environment_ambience(self, r: int, g: int, b: int, a: int):
    if Main3DEnvConfigPageFunc._is_int(r):
      if int(r) != self.ambient_color_red:
        self.ambient_color_red = int(r)
    if Main3DEnvConfigPageFunc._is_int(g):
      if int(g) != self.ambient_color_green:
        self.ambient_color_green = int(g)
    if Main3DEnvConfigPageFunc._is_int(b):
      if int(b) != self.ambient_color_blue:
        self.ambient_color_blue = int(b)
    if Main3DEnvConfigPageFunc._is_int(a):
      if int(a) != self.ambient_color_alpha:
        self.ambient_color_alpha = int(a)


class Main3DEnvConfigPage(Main3DEnvConfigPageFunc, QFrame):

  ENV_DIM_LIMITS = [20000, 10000, 20000]
  ENV_GRID_LIMITS = [200, 200, 200]

  # Signals
  publish_environment_opacity = Signal(int)
  publish_environment_dimensions = Signal(list)
  publish_env_grid_dimensions = Signal(list)
  publish_environment_origin = Signal(list)
  publish_reference_walls = Signal(list)
  publish_environment_colors = Signal(list)

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(Main3DEnvConfigPage, self).__init__(**kwargs)

    self._logger = kwargs['logger']
    self._settings = kwargs.get('settings', None)

    # Setup the page
    self.setObjectName(u"main3DEnvConfigPage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self.init_UI()

    # Connections
    self._create_local_connects()

  def init_UI(self):
    # Create widget layout
    main3DEnvConfigPageVertLayout = QVBoxLayout(self)
    main3DEnvConfigPageVertLayout.setObjectName(u"main3DEnvConfigPageVertLayout")

    # Create layouts & widgets
    envPresetsLayout = self._create_3d_env_presets_layout()
    envDimensionsLayout = self._create_3d_env_dimensions_layout()
    envOriginLayout = self._create_3d_env_origin_layout()
    envAmbientLayout = self._create_3d_env_amb_layout()

    # Add widgets to layout & set margins
    main3DEnvConfigPageVertLayout.addLayout(envPresetsLayout)
    main3DEnvConfigPageVertLayout.addLayout(envDimensionsLayout)
    main3DEnvConfigPageVertLayout.addLayout(envOriginLayout)
    main3DEnvConfigPageVertLayout.addLayout(envAmbientLayout)
    main3DEnvConfigPageVertLayout.setContentsMargins(15, 0, 15, 0)
    main3DEnvConfigPageVertLayout.setSpacing(15)

  def _create_3d_env_presets_layout(self) -> QLayout:
    # Create presets layout
    envPresetsHorizontalLayout = QHBoxLayout()
    envPresetsHorizontalLayout.setObjectName(u"envPresetsHorizontalLayout")

    # Opacity group box
    opacityGroupBox = QGroupBox(parent=self, title=u"Opacity")
    opacityGroupBox.setObjectName(u"opacityGroupBox")

    # Create Opacity layout
    opacityHorizLayout = QHBoxLayout(opacityGroupBox)
    opacityHorizLayout.setObjectName(u"opacityHorizLayout")

    # Create Opacity LineEdit
    self.opacityLineEdit = LineEditWidget(parent=opacityGroupBox, logger=self._logger,
                                          ph_text=u"Opacity", type="data",
                                          minsize=QSize(0, 20), only_int=True)
    self.opacityLineEdit.setObjectName(u"opacityLineEdit")

    # Add widgets to layout & set margins
    opacityHorizLayout.addWidget(self.opacityLineEdit)
    opacityHorizLayout.setContentsMargins(10, 20, 0, 0)
    opacityHorizLayout.setSpacing(3)

    # Presets group box
    envPresetsGroupBox = QGroupBox(parent=self, title=u"Environment Presets")
    envPresetsGroupBox.setObjectName(u"envPresetsGroupBox")

    # Create Presets layout
    envPresetsHorizLayout = QHBoxLayout(envPresetsGroupBox)
    envPresetsHorizLayout.setObjectName(u"envPresetsHorizLayout")

    # Create Presets ComboBox
    self.envPresetsComboBox = ComboBoxWidget(parent=envPresetsGroupBox, logger=self._logger,
                                             items=[u"Custom", u"Auto"], type="title_combo_box",
                                             minsize=QSize(0, 20))
    self.envPresetsComboBox.setObjectName(u"envPresetsComboBox")
    self.envPresetsComboBox.setCurrentIndex(1)

    # Add widgets to layout & set margins
    envPresetsHorizLayout.addWidget(self.envPresetsComboBox)
    envPresetsHorizLayout.setContentsMargins(10, 20, 0, 0)
    envPresetsHorizLayout.setSpacing(3)

    # Add widgets to presets layout & set margins
    envPresetsHorizontalLayout.addWidget(opacityGroupBox)
    envPresetsHorizontalLayout.addWidget(envPresetsGroupBox)
    envPresetsHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    # self.envPresetsHorizontalLayout.setStretch(1, 1)
    envPresetsHorizontalLayout.setSpacing(50)

    return envPresetsHorizontalLayout

  def _create_dimensions_group_box(self) -> QGroupBox:
    # Create dimensions group box
    envDimensionsGroupBox = QGroupBox(parent=self, title=u"Dimensions")
    envDimensionsGroupBox.setObjectName(u"envDimensionsGroupBox")

    # Create dimensions sub layout
    envDimensionsFormLayout = QFormLayout(envDimensionsGroupBox)
    envDimensionsFormLayout.setObjectName(u"envDimensionsFormLayout")

    # Create dimensions Labels
    envDimWidthLabel = LabelWidget(parent=envDimensionsGroupBox, logger=self._logger,
                                   text=u"width", type="sub_label", minsize=QSize(30, 20),
                                   align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envDimWidthLabel.setObjectName(u"envDimWidthLabel")

    envDimHeightLabel = LabelWidget(parent=envDimensionsGroupBox, logger=self._logger,
                                    text=u"height", type="sub_label", minsize=QSize(30, 20),
                                    align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envDimHeightLabel.setObjectName(u"envDimHeightLabel")

    envDimDepthLabel = LabelWidget(parent=envDimensionsGroupBox, logger=self._logger,
                                   text=u"depth", type="sub_label", minsize=QSize(30, 20),
                                   align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envDimDepthLabel.setObjectName(u"envDimDepthLabel")

    # Create dimensions LineEdits
    self.envDimWidthLineEdit = LineEditWidget(parent=envDimensionsGroupBox, logger=self._logger,
                                              ph_text=u"width", type="data",
                                              minsize=QSize(100, 20), only_float=True,
                                              min_value=-self.ENV_DIM_LIMITS[0],
                                              max_value=self.ENV_DIM_LIMITS[0])
    self.envDimWidthLineEdit.setObjectName(u"envDimWidthLineEdit")

    self.envDimHeightLineEdit = LineEditWidget(parent=envDimensionsGroupBox, logger=self._logger,
                                               ph_text=u"height", type="data",
                                               minsize=QSize(100, 20), only_float=True,
                                               min_value=-self.ENV_DIM_LIMITS[1],
                                               max_value=self.ENV_DIM_LIMITS[1])
    self.envDimHeightLineEdit.setObjectName(u"envDimHeightLineEdit")

    self.envDimDepthLineEdit = LineEditWidget(parent=envDimensionsGroupBox, logger=self._logger,
                                              ph_text=u"depth", type="data",
                                              minsize=QSize(100, 20), only_float=True,
                                              min_value=-self.ENV_DIM_LIMITS[2],
                                              max_value=self.ENV_DIM_LIMITS[2])
    self.envDimDepthLineEdit.setObjectName(u"envDimDepthLineEdit")

    # Add widgets to dimensions sub layout & set margins
    envDimensionsFormLayout.setWidget(0, QFormLayout.LabelRole, envDimWidthLabel)
    envDimensionsFormLayout.setWidget(0, QFormLayout.FieldRole, self.envDimWidthLineEdit)
    envDimensionsFormLayout.setWidget(1, QFormLayout.LabelRole, envDimHeightLabel)
    envDimensionsFormLayout.setWidget(1, QFormLayout.FieldRole, self.envDimHeightLineEdit)
    envDimensionsFormLayout.setWidget(2, QFormLayout.LabelRole, envDimDepthLabel)
    envDimensionsFormLayout.setWidget(2, QFormLayout.FieldRole, self.envDimDepthLineEdit)
    envDimensionsFormLayout.setContentsMargins(10, 20, 0, 0)
    envDimensionsFormLayout.setHorizontalSpacing(3)
    envDimensionsFormLayout.setVerticalSpacing(3)

    return envDimensionsGroupBox

  def _create_grid_group_box(self) -> QGroupBox:
    # Create grid group box
    envGridGroupBox = QGroupBox(parent=self, title=u"Grid")
    envGridGroupBox.setObjectName(u"envGridGroupBox")

    # Create grid sub layout
    envGridFormLayout = QFormLayout(envGridGroupBox)
    envGridFormLayout.setObjectName(u"envGridFormLayout")

    # Create Grid Labels
    envGridWidthLabel = LabelWidget(parent=envGridGroupBox, logger=self._logger, text=u"width",
                                    type="sub_label", minsize=QSize(30, 20),
                                    align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envGridWidthLabel.setObjectName(u"envGridWidthLabel")

    envGridHeightLabel = LabelWidget(parent=envGridGroupBox, logger=self._logger, text=u"height",
                                    type="sub_label", minsize=QSize(30, 20),
                                     align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envGridHeightLabel.setObjectName(u"envGridHeightLabel")

    envGridDepthLabel = LabelWidget(parent=envGridGroupBox, logger=self._logger, text=u"depth",
                                    type="sub_label", minsize=QSize(30, 20),
                                    align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envGridDepthLabel.setObjectName(u"envGridDepthLabel")

    # Create Grid LineEdits
    self.envGridWidthLineEdit = LineEditWidget(parent=envGridGroupBox, logger=self._logger,
                                               ph_text=u"width", type="data",
                                               minsize=QSize(100, 20), only_float=True,
                                               min_value=-self.ENV_GRID_LIMITS[0],
                                               max_value=self.ENV_GRID_LIMITS[0])
    self.envGridWidthLineEdit.setObjectName(u"envGridWidthLineEdit")

    self.envGridHeightLineEdit = LineEditWidget(parent=envGridGroupBox, logger=self._logger,
                                                ph_text=u"height", type="data",
                                                minsize=QSize(100, 20), only_float=True,
                                                min_value=-self.ENV_GRID_LIMITS[1],
                                                max_value=self.ENV_GRID_LIMITS[1])
    self.envGridHeightLineEdit.setObjectName(u"envGridHeightLineEdit")

    self.envGridDepthLineEdit = LineEditWidget(parent=envGridGroupBox, logger=self._logger,
                                               ph_text=u"depth", type="data",
                                               minsize=QSize(100, 20), only_float=True,
                                               min_value=-self.ENV_GRID_LIMITS[2],
                                               max_value=self.ENV_GRID_LIMITS[2])
    self.envGridDepthLineEdit.setObjectName(u"envGridDepthLineEdit")

    # Add widgets to Grid sub layout & set margins
    envGridFormLayout.setWidget(0, QFormLayout.LabelRole, envGridWidthLabel)
    envGridFormLayout.setWidget(0, QFormLayout.FieldRole, self.envGridWidthLineEdit)
    envGridFormLayout.setWidget(1, QFormLayout.LabelRole, envGridHeightLabel)
    envGridFormLayout.setWidget(1, QFormLayout.FieldRole, self.envGridHeightLineEdit)
    envGridFormLayout.setWidget(2, QFormLayout.LabelRole, envGridDepthLabel)
    envGridFormLayout.setWidget(2, QFormLayout.FieldRole, self.envGridDepthLineEdit)
    envGridFormLayout.setContentsMargins(10, 20, 0, 0)
    envGridFormLayout.setHorizontalSpacing(3)
    envGridFormLayout.setVerticalSpacing(3)

    return envGridGroupBox

  def _create_3d_env_dimensions_layout(self) -> QLayout:
    # Create dimensions main layout
    envDimensionsHorizLayout = QHBoxLayout()
    envDimensionsHorizLayout.setObjectName(u"envDimensionsHorizLayout")

    dimGroupBox = self._create_dimensions_group_box()
    gridGroupBox = self._create_grid_group_box()

    # Add widgets to dimensions layout & set margins
    envDimensionsHorizLayout.addWidget(dimGroupBox)
    envDimensionsHorizLayout.addWidget(gridGroupBox)
    envDimensionsHorizLayout.setContentsMargins(0, 0, 0, 0)
    envDimensionsHorizLayout.setSpacing(50)

    return envDimensionsHorizLayout

  def _create_origin_group_box(self) -> QGroupBox:
    # Create origin group box
    envOriginGroupBox = QGroupBox(parent=self, title=u"Origin")
    envOriginGroupBox.setObjectName(u"envOriginGroupBox")

    # Create origin sub layout
    envOriginFormLayout = QFormLayout(envOriginGroupBox)
    envOriginFormLayout.setObjectName(u"envOriginFormLayout")

    # Create Origin Labels
    envOriginXLabel = LabelWidget(parent=envOriginGroupBox, logger=self._logger, text=u"x",
                                  type="sub_label", minsize=QSize(30, 20),
                                  align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envOriginXLabel.setObjectName(u"envOriginXLabel")

    envOriginYLabel = LabelWidget(parent=envOriginGroupBox, logger=self._logger, text=u"y",
                                  type="sub_label", minsize=QSize(30, 20),
                                  align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envOriginYLabel.setObjectName(u"envOriginYLabel")

    envOriginZLabel = LabelWidget(parent=envOriginGroupBox, logger=self._logger, text=u"z",
                                  type="sub_label", minsize=QSize(30, 20),
                                  align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envOriginZLabel.setObjectName(u"envOriginZLabel")

    # Create Origin LineEdits
    self.envOriginXLineEdit = LineEditWidget(parent=envOriginGroupBox, logger=self._logger,
                                             ph_text=u"x", type="data", minsize=QSize(100, 20),
                                             only_float=True,
                                             min_value=-self.ENV_DIM_LIMITS[0],
                                             max_value=self.ENV_DIM_LIMITS[0])
    self.envOriginXLineEdit.setObjectName(u"envOriginXLineEdit")

    self.envOriginYLineEdit = LineEditWidget(parent=envOriginGroupBox, logger=self._logger,
                                             ph_text=u"y", type="data", minsize=QSize(100, 20),
                                             only_float=True,
                                             min_value=-self.ENV_DIM_LIMITS[1],
                                             max_value=self.ENV_DIM_LIMITS[1])
    self.envOriginYLineEdit.setObjectName(u"envOriginYLineEdit")

    self.envOriginZLineEdit = LineEditWidget(parent=envOriginGroupBox, logger=self._logger,
                                             ph_text=u"z", type="data", minsize=QSize(100, 20),
                                             only_float=True,
                                             min_value=-self.ENV_DIM_LIMITS[2],
                                             max_value=self.ENV_DIM_LIMITS[2])
    self.envOriginZLineEdit.setObjectName(u"envOriginZLineEdit")

    # Add widgets to Origin sub layout & set margins
    envOriginFormLayout.setWidget(0, QFormLayout.LabelRole, envOriginXLabel)
    envOriginFormLayout.setWidget(0, QFormLayout.FieldRole, self.envOriginXLineEdit)
    envOriginFormLayout.setWidget(1, QFormLayout.LabelRole, envOriginYLabel)
    envOriginFormLayout.setWidget(1, QFormLayout.FieldRole, self.envOriginYLineEdit)
    envOriginFormLayout.setWidget(2, QFormLayout.LabelRole, envOriginZLabel)
    envOriginFormLayout.setWidget(2, QFormLayout.FieldRole, self.envOriginZLineEdit)
    envOriginFormLayout.setContentsMargins(10, 20, 0, 0)
    envOriginFormLayout.setHorizontalSpacing(3)
    envOriginFormLayout.setVerticalSpacing(3)

    return envOriginGroupBox

  def _create_walls_group_box(self) -> QGroupBox:
    # Create walls group box
    envWallsGroupBox = QGroupBox(parent=self, title=u"Reference Walls")
    envWallsGroupBox.setObjectName(u"envWallsGroupBox")

    # Create walls sub layout
    envWallsFormLayout = QFormLayout(envWallsGroupBox)
    envWallsFormLayout.setObjectName(u"envWallsFormLayout")

    # Create Walls Labels
    dummyLabel1 = LabelWidget(parent=envWallsGroupBox, logger=self._logger, text=u"d",
                              type="dummy_label", minsize=QSize(30, 20),
                              align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    dummyLabel1.setObjectName(u"dummyLabel1")

    dummyLabel2 = LabelWidget(parent=envWallsGroupBox, logger=self._logger, text=u"d",
                              type="dummy_label", minsize=QSize(30, 20),
                              align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    dummyLabel2.setObjectName(u"dummyLabel2")

    dummyLabel3 = LabelWidget(parent=envWallsGroupBox, logger=self._logger, text=u"d",
                              type="dummy_label", minsize=QSize(30, 20),
                              align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    dummyLabel3.setObjectName(u"dummyLabel3")

    # Create Walls ComboBoxes
    self.envWallsXComboBox = ComboBoxWidget(parent=envWallsGroupBox, logger=self._logger,
                                            items=[u"Left Wall", u"Right Wall"],
                                            type="sub_combo_box", minsize=QSize(100, 20))
    self.envWallsXComboBox.setObjectName(u"envWallsXComboBox")

    self.envWallsYComboBox = ComboBoxWidget(parent=envWallsGroupBox, logger=self._logger,
                                            items=[u"Floor", u"Roof"],
                                            type="sub_combo_box", minsize=QSize(100, 20))
    self.envWallsYComboBox.setObjectName(u"envWallsYComboBox")

    self.envWallsZComboBox = ComboBoxWidget(parent=envWallsGroupBox, logger=self._logger,
                                            items=[u"Front Wall", u"Back Wall"],
                                            type="sub_combo_box", minsize=QSize(100, 20))
    self.envWallsZComboBox.setObjectName(u"envWallsZComboBox")

    # Add widgets to Walls sub layout & set margins
    envWallsFormLayout.setWidget(0, QFormLayout.LabelRole, dummyLabel1)
    envWallsFormLayout.setWidget(0, QFormLayout.FieldRole, self.envWallsXComboBox)
    envWallsFormLayout.setWidget(1, QFormLayout.LabelRole, dummyLabel2)
    envWallsFormLayout.setWidget(1, QFormLayout.FieldRole, self.envWallsYComboBox)
    envWallsFormLayout.setWidget(2, QFormLayout.LabelRole, dummyLabel3)
    envWallsFormLayout.setWidget(2, QFormLayout.FieldRole, self.envWallsZComboBox)
    envWallsFormLayout.setContentsMargins(10, 20, 0, 0)
    envWallsFormLayout.setHorizontalSpacing(3)
    envWallsFormLayout.setVerticalSpacing(3)

    return envWallsGroupBox

  def _create_3d_env_origin_layout(self) -> QLayout:
    # Create origin main layout
    envOriginHorizLayout = QHBoxLayout()
    envOriginHorizLayout.setObjectName(u"envOriginHorizLayout")

    originGroupBox = self._create_origin_group_box()
    wallsGroupBox = self._create_walls_group_box()

    # Add widgets to origin layout & set margins
    envOriginHorizLayout.addWidget(originGroupBox)
    envOriginHorizLayout.addWidget(wallsGroupBox)
    envOriginHorizLayout.setContentsMargins(0, 0, 0, 0)
    envOriginHorizLayout.setSpacing(50)

    return envOriginHorizLayout

  def _create_colors_group_box(self) -> QGroupBox:
    # Create colors group box
    envColorsGroupBox = QGroupBox(parent=self, title=u"Ambient Colors")
    envColorsGroupBox.setObjectName(u"envColorsGroupBox")

    # Create colors sub layout
    envColorsFormLayout = QFormLayout(envColorsGroupBox)
    envColorsFormLayout.setObjectName(u"envColorsFormLayout")

    # Create Colors Labels
    envColorsRLabel = LabelWidget(parent=envColorsGroupBox, logger=self._logger, text=u"r",
                                  type="sub_label", minsize=QSize(30, 20),
                                  align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envColorsRLabel.setObjectName(u"envColorsRLabel")

    envColorsGLabel = LabelWidget(parent=envColorsGroupBox, logger=self._logger, text=u"g",
                                  type="sub_label", minsize=QSize(30, 20),
                                  align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envColorsGLabel.setObjectName(u"envColorsGLabel")

    envColorsBLabel = LabelWidget(parent=envColorsGroupBox, logger=self._logger, text=u"b",
                                  type="sub_label", minsize=QSize(30, 20),
                                  align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    envColorsBLabel.setObjectName(u"envColorsBLabel")

    # Create Colors LineEdits
    self.envColorsRLineEdit = LineEditWidget(parent=envColorsGroupBox, logger=self._logger,
                                             ph_text=u"r", type="data", minsize=QSize(100, 20),
                                             only_int=True)
    self.envColorsRLineEdit.setObjectName(u"envColorsRLineEdit")

    self.envColorsGLineEdit = LineEditWidget(parent=envColorsGroupBox, logger=self._logger,
                                             ph_text=u"g", type="data", minsize=QSize(100, 20),
                                             only_int=True)
    self.envColorsGLineEdit.setObjectName(u"envColorsGLineEdit")

    self.envColorsBLineEdit = LineEditWidget(parent=envColorsGroupBox, logger=self._logger,
                                             ph_text=u"b", type="data", minsize=QSize(100, 20),
                                             only_int=True)
    self.envColorsBLineEdit.setObjectName(u"envColorsBLineEdit")

    # Add widgets to Colors sub layout & set margins
    envColorsFormLayout.setWidget(0, QFormLayout.LabelRole, envColorsRLabel)
    envColorsFormLayout.setWidget(0, QFormLayout.FieldRole, self.envColorsRLineEdit)
    envColorsFormLayout.setWidget(1, QFormLayout.LabelRole, envColorsGLabel)
    envColorsFormLayout.setWidget(1, QFormLayout.FieldRole, self.envColorsGLineEdit)
    envColorsFormLayout.setWidget(2, QFormLayout.LabelRole, envColorsBLabel)
    envColorsFormLayout.setWidget(2, QFormLayout.FieldRole, self.envColorsBLineEdit)
    envColorsFormLayout.setContentsMargins(10, 20, 0, 0)
    envColorsFormLayout.setHorizontalSpacing(3)
    envColorsFormLayout.setVerticalSpacing(3)

    return envColorsGroupBox

  def _create_alpha_group_box(self) -> QLayout:
    # Create alpha group box
    envAlphaGroupBox = QGroupBox(parent=self, title=u"Alpha")
    envAlphaGroupBox.setObjectName(u"envAlphaGroupBox")

    # Create colors sub layout
    envAlphaFormLayout= QFormLayout(envAlphaGroupBox)
    envAlphaFormLayout.setObjectName(u"envAlphaFormLayout")

    # Create Alpha Labels
    dummyLabel1 = LabelWidget(parent=envAlphaGroupBox, logger=self._logger, text=u"d",
                              type="dummy_label", minsize=QSize(30, 20),
                              align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    dummyLabel1.setObjectName(u"dummyLabel1")

    dummyLabel2 = LabelWidget(parent=envAlphaGroupBox, logger=self._logger, text=u"d",
                              type="dummy_label", minsize=QSize(30, 20),
                              align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    dummyLabel2.setObjectName(u"dummyLabe2")

    dummyLabel3 = LabelWidget(parent=envAlphaGroupBox, logger=self._logger, text=u"d",
                              type="dummy_label", minsize=QSize(30, 20),
                              align=Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
    dummyLabel3.setObjectName(u"dummyLabe3")

    # Create Alpha LineEdits
    self.envAlphaLineEdit = LineEditWidget(parent=envAlphaGroupBox, logger=self._logger,
                                           ph_text=u"a", type="data", minsize=QSize(100, 20),
                                           only_int=True)
    self.envAlphaLineEdit.setObjectName(u"envAlphaLineEdit")

    envDummy1LineEdit = LineEditWidget(parent=envAlphaGroupBox, logger=self._logger,
                                       type="dummy", minsize=QSize(100, 20))
    envDummy1LineEdit.setObjectName(u"envDummy1LineEdit")
    envDummy1LineEdit.setEnabled(False)

    envDummy2LineEdit = LineEditWidget(parent=envAlphaGroupBox, logger=self._logger,
                                       type="dummy", minsize=QSize(100, 20))
    envDummy2LineEdit.setObjectName(u"envDummy2LineEdit")
    envDummy2LineEdit.setEnabled(False)

    # Add widgets to Alpha sub layout & set margins
    envAlphaFormLayout.setWidget(0, QFormLayout.LabelRole, dummyLabel1)
    envAlphaFormLayout.setWidget(0, QFormLayout.FieldRole, self.envAlphaLineEdit)
    envAlphaFormLayout.setWidget(1, QFormLayout.LabelRole, dummyLabel2)
    envAlphaFormLayout.setWidget(1, QFormLayout.FieldRole, envDummy1LineEdit)
    envAlphaFormLayout.setWidget(2, QFormLayout.LabelRole, dummyLabel3)
    envAlphaFormLayout.setWidget(2, QFormLayout.FieldRole, envDummy2LineEdit)
    envAlphaFormLayout.setContentsMargins(10, 20, 0, 0)
    envAlphaFormLayout.setHorizontalSpacing(3)
    envAlphaFormLayout.setVerticalSpacing(3)

    return envAlphaGroupBox

  def _create_3d_env_amb_layout(self) -> QLayout:
    # Create ambient main layout
    envAmbientHorizLayout = QHBoxLayout()
    envAmbientHorizLayout.setObjectName(u"envAmbientHorizLayout")

    colorsGroupBox = self._create_colors_group_box()
    alphaGroupBox = self._create_alpha_group_box()

    # Add widgets to origin layout & set margins
    envAmbientHorizLayout.addWidget(colorsGroupBox)
    envAmbientHorizLayout.addWidget(alphaGroupBox)
    envAmbientHorizLayout.setContentsMargins(0, 0, 0, 0)
    envAmbientHorizLayout.setSpacing(50)

    return envAmbientHorizLayout

  def _create_env_presets_local_connects(self) -> None:
    # ComboBox
    self.envPresetsComboBox.currentIndexChanged.connect(
      lambda: self.setup_environment_preset(
        self.envPresetsComboBox.currentText()
      )
    )
    # LineEdits
    self.opacityLineEdit.editingFinished.connect(
      lambda: self.setup_environment_opacity(opacity=self.opacityLineEdit.text())
    )

  def _create_dimensions_local_connects(self) -> None:
    # LineEdits
    self.envDimWidthLineEdit.editingFinished.connect(
      lambda: self.setup_environment_dimensions(
        w=self.envDimWidthLineEdit.text(), h=self.env_height, d=self.env_depth
      )
    )
    self.envDimHeightLineEdit.editingFinished.connect(
      lambda: self.setup_environment_dimensions(
        w=self.env_width, h=self.envDimHeightLineEdit.text(), d=self.env_depth
      )
    )
    self.envDimDepthLineEdit.editingFinished.connect(
      lambda: self.setup_environment_dimensions(
        w=self.env_width, h=self.env_height, d=self.envDimDepthLineEdit.text()
      )
    )

  def _create_grid_dimensions_local_connects(self) -> None:
    # LineEdits
    self.envGridWidthLineEdit.editingFinished.connect(
      lambda: self.setup_env_grid_dimensions(
        g_w=self.envGridWidthLineEdit.text(), g_h=self.env_grid_height, g_d=self.env_grid_depth
      )
    )
    self.envGridHeightLineEdit.editingFinished.connect(
      lambda: self.setup_env_grid_dimensions(
        g_w=self.env_grid_width, g_h=self.envGridHeightLineEdit.text(), g_d=self.env_grid_depth
      )
    )
    self.envGridDepthLineEdit.editingFinished.connect(
      lambda: self.setup_env_grid_dimensions(
        g_w=self.env_grid_width, g_h=self.env_grid_height, g_d=self.envGridDepthLineEdit.text()
      )
    )

  def _create_env_origin_local_connects(self):
    # LineEdits
    self.envOriginXLineEdit.editingFinished.connect(
      lambda: self.setup_environment_origin(
        x=self.envOriginXLineEdit.text(), y=self.env_origin_y, z=self.env_origin_z
      )
    )
    self.envOriginYLineEdit.editingFinished.connect(
      lambda: self.setup_environment_origin(
        x=self.env_origin_x, y=self.envOriginYLineEdit.text(), z=self.env_origin_z
      )
    )
    self.envOriginZLineEdit.editingFinished.connect(
      lambda: self.setup_environment_origin(
        x=self.env_origin_x, y=self.env_origin_y, z=self.envOriginZLineEdit.text()
      )
    )

  def _create_env_ref_walls_local_connects(self) -> None:
    # ComboBoxes
    self.envWallsXComboBox.currentIndexChanged.connect(
      lambda: self.setup_reference_walls(
        ref_wall_x=self.envWallsXComboBox.currentText(),
        ref_wall_y=self.ref_wall_origin_y,
        ref_wall_z=self.ref_wall_origin_z
      )
    )
    self.envWallsYComboBox.currentIndexChanged.connect(
      lambda: self.setup_reference_walls(
        ref_wall_x=self.ref_wall_origin_x,
        ref_wall_y=self.envWallsYComboBox.currentText(),
        ref_wall_z=self.ref_wall_origin_z
      )
    )
    self.envWallsZComboBox.currentIndexChanged.connect(
      lambda: self.setup_reference_walls(
        ref_wall_x=self.ref_wall_origin_x,
        ref_wall_y=self.ref_wall_origin_y,
        ref_wall_z=self.envWallsZComboBox.currentText()
      )
    )

  def _create_ambient_colors_local_connects(self) -> None:
    # LineEdits
    self.envColorsRLineEdit.editingFinished.connect(
      lambda: self.setup_environment_ambience(
        r=self.envColorsRLineEdit.text(), g=self.ambient_color_green,
        b=self.ambient_color_blue, a=self.ambient_color_alpha
      )
    )
    self.envColorsGLineEdit.editingFinished.connect(
      lambda: self.setup_environment_ambience(
        r=self.ambient_color_red, g=self.envColorsGLineEdit.text(),
        b=self.ambient_color_blue, a=self.ambient_color_alpha
      )
    )
    self.envColorsBLineEdit.editingFinished.connect(
      lambda: self.setup_environment_ambience(
        r=self.ambient_color_red, g=self.ambient_color_green,
        b=self.envColorsBLineEdit.text(), a=self.ambient_color_alpha
      )
    )
    self.envAlphaLineEdit.editingFinished.connect(
      lambda: self.setup_environment_ambience(
        r=self.ambient_color_red, g=self.ambient_color_green,
        b=self.ambient_color_blue, a=self.envAlphaLineEdit.text()
      )
    )

  def _create_local_connects(self) -> None:
    self._create_env_presets_local_connects()
    self._create_dimensions_local_connects()
    self._create_grid_dimensions_local_connects()
    self._create_env_origin_local_connects()
    self._create_env_ref_walls_local_connects()
    self._create_ambient_colors_local_connects()

  def setup_environment_opacity(self, opacity: int) -> None:
    super(Main3DEnvConfigPage, self).setup_environment_opacity(opacity)
    self.publish_environment_opacity.emit(self.env_opacity)

  def setup_environment_dimensions(self, w: float, h: float, d: float) -> None:
    super(Main3DEnvConfigPage, self).setup_environment_dimensions(w, h, d)
    self.publish_environment_dimensions.emit([self.env_width, self.env_height, self.env_depth])

  def setup_env_grid_dimensions(self, g_w: float, g_h: float, g_d: float) -> None:
    super(Main3DEnvConfigPage, self).setup_env_grid_dimensions(g_w, g_h, g_d)
    self.publish_env_grid_dimensions.emit([self.env_grid_width, self.env_grid_height,
                                           self.env_grid_depth])

  def setup_environment_origin(self, x: float, y: float, z: float) -> None:
    super(Main3DEnvConfigPage, self).setup_environment_origin(x, y, z)
    self.publish_environment_origin.emit([self.env_origin_x, self.env_origin_y, self.env_origin_z])

  def setup_reference_walls(self, ref_wall_x: str, ref_wall_y: str, ref_wall_z: str) -> None:
    super(Main3DEnvConfigPage, self).setup_reference_walls(ref_wall_x, ref_wall_y, ref_wall_z)
    self.publish_reference_walls.emit([self.ref_wall_origin_x, self.ref_wall_origin_y,
                                       self.ref_wall_origin_z])

  def setup_environment_ambience(self, r: int, g: int, b: int, a: int):
    super(Main3DEnvConfigPage, self).setup_environment_ambience(r, g, b, a)
    self.publish_environment_colors.emit([self.ambient_color_red, self.ambient_color_green,
                                          self.ambient_color_blue, self.ambient_color_alpha])


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed QFrame
  main_3d_env_setup_widget = Main3DEnvSetupWidget()
  main_3d_env_setup_widget._logger.remove_log_files()
  # Show the widget
  main_3d_env_setup_widget.show()
  # Execute the program
  sys.exit(app.exec())