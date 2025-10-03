## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the Artemis Control Widgets.
##
##############################################################################################
##
import os
import sys
import posixpath

from PySide6.QtGui import QCloseEvent, Qt
from PySide6.QtCore import QSettings, QSize
from PySide6.QtWidgets import (QApplication, QWidget, QFrame, QGroupBox, QHBoxLayout, QVBoxLayout,
                               QStackedWidget, QSpacerItem, QSizePolicy)

try:
  from scripts.settings import PathManager
  from scripts.ui.widgets_sub.SubWidgets import (LabelWidget, ComboBoxWidget, CheckBoxWidget,
                                                 LineEditWidget, PushButtonWidget)
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings import PathManager
  from scripts.ui.widgets_sub.SubWidgets import (LabelWidget, CheckBoxWidget, ComboBoxWidget,
                                                 LineEditWidget, PushButtonWidget)


class ArtemisCtrlWidget(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(ArtemisCtrlWidget, self).__init__(parent=self._parent)

    self._logger = kwargs['logger']
    self._settings = kwargs.get('settings', None)

    # Setup the top bar
    self.setObjectName(u"artemisCtrlWidget")
    self.setWindowTitle(u"Artemis Controls")
    if self._parent is None:
      self.resize(QSize(410, 487))
      self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    self.init_UI()

    # Set Artemis Control Widget default stylesheet
    self.set_stylesheet()

  def init_UI(self) -> None:
    # Create main layout
    artemisCtrlMainLayout = QVBoxLayout(self)
    artemisCtrlMainLayout.setObjectName(u"artemisCtrlMainLayout")

    # Create Widgets
    self._create_connection_controls()
    self._create_stacked_widget_ctrls()
    verticalSpacer = QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
    self._create_stacked_widget()

    # Add widgets to the layout & set margins
    artemisCtrlMainLayout.addLayout(self.connectionCtrlVertLayout)
    artemisCtrlMainLayout.addLayout(self.stackedWdgtBtnsHorizLayout)
    artemisCtrlMainLayout.addItem(verticalSpacer)
    artemisCtrlMainLayout.addWidget(self.manipCamStackedWidget)
    artemisCtrlMainLayout.setContentsMargins(20, 10, 20, 10)
    artemisCtrlMainLayout.setSpacing(20)

    # Create connections
    self._create_local_connects()

    # Initialize stacked widget
    self._on_page_select_button_clicked()
    self._on_manip_cam_stckd_wdgt_page_chngd()

  def set_stylesheet(self, theme: str='default', qss: str='ArtemisCtrlWidget.qss') -> None:
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

  def _create_connection_controls(self) -> None:
    # Create layout
    self.connectionCtrlVertLayout = QVBoxLayout()
    self.connectionCtrlVertLayout.setObjectName(u"connectionCtrlVertLayout")

    # Create Title Horizontal Layout
    titleHorizLayout = QHBoxLayout()
    titleHorizLayout.setObjectName(u"titleHorizLayout")

    # Create title label
    artemisTitleLabel = LabelWidget(parent=self, logger=self._logger, text=u"Artemis",
                                    minsize=QSize(275, 20), align=Qt.AlignCenter)
    artemisTitleLabel.setObjectName(u"artemisTitleLabel")

    # Create Sticky Checkbox
    self.stickyCheckBox = CheckBoxWidget(parent=self, logger=self._logger, text=u"Sticky",
                                         layout_dir=Qt.RightToLeft)
    self.stickyCheckBox.setObjectName(u"stickyCheckBox")

    # Add widgets to horizontal layout & set margins
    titleHorizLayout.addWidget(artemisTitleLabel)
    titleHorizLayout.addWidget(self.stickyCheckBox)
    titleHorizLayout.setContentsMargins(0, 0, 0, 0)
    titleHorizLayout.setSpacing(30)

    # Create Connection Horizontal Layout
    connectionHorizontalLayout = QHBoxLayout()
    connectionHorizontalLayout.setObjectName(u"connectionHorizontalLayout")

    # Create IP address Horizontal layout
    ipAddressHorizontalLayout = QHBoxLayout()
    ipAddressHorizontalLayout.setObjectName(u"ipAddressHorizontalLayout")

    # IP Address
    self.ipAddressLineEdit = LineEditWidget(parent=self, logger=self._logger,
                                            ph_text=u"IP Address", minsize=QSize(100, 20))
    self.ipAddressLineEdit.setObjectName(u"ipAddressLineEdit")

    # Ping Button
    self.pingPushButton = PushButtonWidget(parent=self, logger=self._logger, text=u"Ping",
                                           minsize=QSize(50, 20))
    self.pingPushButton.setObjectName(u"pingPushButton")

    # Add widgets to horizontal layout & set margins
    ipAddressHorizontalLayout.addWidget(self.ipAddressLineEdit)
    ipAddressHorizontalLayout.addWidget(self.pingPushButton)
    ipAddressHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    ipAddressHorizontalLayout.setSpacing(0)

    # Create Connect button horizontal layout
    connectButtonHorizLayout = QHBoxLayout()
    connectButtonHorizLayout.setObjectName(u"connectButtonHorizLayout")

    # Connect Status Label
    self.connectStatusLED = LabelWidget(parent=self, logger=self._logger, type="dummy_label",
                                        minsize=QSize(10, 0), maxsize=QSize(10, 10))
    self.connectStatusLED.setObjectName(u"connectStatusLED")

    # Connect Push Button
    self.connectPushButton = PushButtonWidget(parent=self, logger=self._logger,
                                              text=u"Connect", minsize=QSize(90, 20))
    self.connectPushButton.setObjectName(u"connectPushButton")

    # Add widgets to horizontal layout & set margins
    connectButtonHorizLayout.addWidget(self.connectStatusLED)
    connectButtonHorizLayout.addWidget(self.connectPushButton)
    connectButtonHorizLayout.setContentsMargins(0, 0, 0, 0)
    connectButtonHorizLayout.setSpacing(5)

    # Add widgets to horizontal layout & set margins
    connectionHorizontalLayout.addLayout(ipAddressHorizontalLayout)
    connectionHorizontalLayout.addLayout(connectButtonHorizLayout)
    connectionHorizontalLayout.setContentsMargins(0, 0, 0, 0)
    connectionHorizontalLayout.setSpacing(25)

    # Add widgets to vertical layout & set margins
    self.connectionCtrlVertLayout.addLayout(titleHorizLayout)
    self.connectionCtrlVertLayout.addLayout(connectionHorizontalLayout)
    self.connectionCtrlVertLayout.setContentsMargins(0, 0, 0, 0)
    self.connectionCtrlVertLayout.setSpacing(15)

  def _create_stacked_widget_ctrls(self) -> None:
    # Create layout
    self.stackedWdgtBtnsHorizLayout = QHBoxLayout()
    self.stackedWdgtBtnsHorizLayout.setObjectName(u"stackedWdgtBtnsHorizLayout")

    # Pushbuttons
    self.manipCamPushButton = PushButtonWidget(parent=self, logger=self._logger,
                                               text=u"Manipulator Location/Camera Mount",
                                               minsize=QSize(0, 20))
    self.manipCamPushButton.setObjectName(u"manipCamPushButton")

    self.manipSettingsPushButton = PushButtonWidget(parent=self, logger=self._logger,
                                                    text=u"Manipulator Settings",
                                                    minsize=QSize(0, 20))
    self.manipSettingsPushButton.setObjectName(u"manipSettingsPushButton")

    # Add widgets to horizontal layout & set margins
    self.stackedWdgtBtnsHorizLayout.addWidget(self.manipCamPushButton)
    self.stackedWdgtBtnsHorizLayout.addWidget(self.manipSettingsPushButton)
    self.stackedWdgtBtnsHorizLayout.setContentsMargins(0, 0, 0, 0)
    self.stackedWdgtBtnsHorizLayout.setSpacing(0)

  def _create_stacked_widget(self) -> None:
    # Stacked Widgets
    self.manipCamStackedWidget = QStackedWidget(self)
    self.manipCamStackedWidget.setObjectName(u"manipCamStackedWidget")

    # Create pages
    self.manipCamPage = ManipCamPage(logger=self._logger)
    self.manipSettingsPage = ManipSettingsPage(logger=self._logger)

    # Add pages
    self.manipCamStackedWidget.addWidget(self.manipCamPage)
    self.manipCamStackedWidget.addWidget(self.manipSettingsPage)

  def _create_local_connects(self) -> None:
    # Pushbuttons
    self.manipCamPushButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=0)
    )
    self.manipSettingsPushButton.clicked.connect(
      lambda: self._on_page_select_button_clicked(idx=1)
    )

    # Stacked Widget
    self.manipCamStackedWidget.currentChanged.connect(
      self._on_manip_cam_stckd_wdgt_page_chngd
    )

  def _on_page_select_button_clicked(self, idx: int=0) -> None:
    self.manipCamStackedWidget.setCurrentIndex(idx)

  def _on_manip_cam_stckd_wdgt_page_chngd(self, idx: int=0) -> None:
    if not isinstance(idx, int):
      self._logger.warning("Invalid index type received")

    if idx == 0:
      self.manipCamPushButton.setEnabled(False)
      self.manipSettingsPushButton.setEnabled(True)
    elif idx == 1:
      self.manipCamPushButton.setEnabled(True)
      self.manipSettingsPushButton.setEnabled(False)

  def save_state(self) -> None:
    pass

  def closeEvent(self, event: QCloseEvent) -> None:
    self.save_state()
    return super(ArtemisCtrlWidget, self).closeEvent(event)


class ManipCamPage(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(ManipCamPage, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"manipCamPage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    manipCamPageVerticalLayout = QVBoxLayout(self)
    manipCamPageVerticalLayout.setObjectName(u"manipCamPageVerticalLayout")

    # Create widgets
    self._create_manipulator_location_group_box()
    self._create_camera_mount_group_box()

    # Add widgets to layout & set margins
    manipCamPageVerticalLayout.addWidget(self.manipLocPresetsGroupBox)
    manipCamPageVerticalLayout.addWidget(self.camMountPresetsGroupBox)
    manipCamPageVerticalLayout.setContentsMargins(15, 0, 15, 0)
    manipCamPageVerticalLayout.setSpacing(20)

  # Manipulator location position group box
  def _create_manip_loc_pos_group_box(self, par: QWidget) -> QGroupBox:
    # create group box
    manipLocPosGroupBox = QGroupBox(parent=par, title=u"Position")
    manipLocPosGroupBox.setObjectName(u"manipLocPosGroupBox")

    # Create vertical layout
    manipLocPosVertLayout = QVBoxLayout(manipLocPosGroupBox)
    manipLocPosVertLayout.setObjectName(u"manipLocPosVertLayout")

    # Create LineEdits
    self.manipLocXPosLineEdit = LineEditWidget(parent=manipLocPosGroupBox, logger=self._logger,
                                               ph_text=u"x", type="data", minsize=QSize(0, 15))
    self.manipLocXPosLineEdit.setObjectName(u"manipLocXPosLineEdit")

    self.manipLocYPosLineEdit = LineEditWidget(parent=manipLocPosGroupBox, logger=self._logger,
                                               ph_text=u"y", type="data", minsize=QSize(0, 15))
    self.manipLocYPosLineEdit.setObjectName(u"manipLocYPosLineEdit")

    self.manipLocZPosLineEdit = LineEditWidget(parent=manipLocPosGroupBox, logger=self._logger,
                                               ph_text=u"z", type="data", minsize=QSize(0, 15))
    self.manipLocZPosLineEdit.setObjectName(u"manipLocZPosLineEdit")

    # Create CheckBox
    self.manipLocPosCheckBox = CheckBoxWidget(parent=manipLocPosGroupBox, logger=self._logger,
                                              text=u"Local", minsize=QSize(50, 15))
    self.manipLocPosCheckBox.setObjectName(u"manipLocPosCheckBox")

    # Add widget to layout & set margins
    manipLocPosVertLayout.addWidget(self.manipLocXPosLineEdit)
    manipLocPosVertLayout.addWidget(self.manipLocYPosLineEdit)
    manipLocPosVertLayout.addWidget(self.manipLocZPosLineEdit)
    manipLocPosVertLayout.addWidget(self.manipLocPosCheckBox)
    manipLocPosVertLayout.setContentsMargins(10, 20, 0, 0)
    manipLocPosVertLayout.setSpacing(3)

    return manipLocPosGroupBox

  # Manipulator location rotation group box
  def _create_manip_loc_rot_group_box(self, par: QWidget) -> QGroupBox:
    # create group box
    manipLocRotGroupBox = QGroupBox(parent=par, title=u"Rotation")
    manipLocRotGroupBox.setObjectName(u"manipLocRotGroupBox")

    # Create vertical layout
    manipLocRotVertLayout = QVBoxLayout(manipLocRotGroupBox)
    manipLocRotVertLayout.setObjectName(u"manipLocRotVertLayout")

    # Create LineEdits
    self.manipLocXRotLineEdit = LineEditWidget(parent=manipLocRotGroupBox, logger=self._logger,
                                               ph_text=u"x", type="data", minsize=QSize(0, 15))
    self.manipLocXRotLineEdit.setObjectName(u"manipLocXRotLineEdit")

    self.manipLocYRotLineEdit = LineEditWidget(parent=manipLocRotGroupBox, logger=self._logger,
                                               ph_text=u"y", type="data", minsize=QSize(0, 15))
    self.manipLocYRotLineEdit.setObjectName(u"manipLocYRotLineEdit")

    self.manipLocZRotLineEdit = LineEditWidget(parent=manipLocRotGroupBox, logger=self._logger,
                                               ph_text=u"z", type="data", minsize=QSize(0, 15))
    self.manipLocZRotLineEdit.setObjectName(u"manipLocZRotLineEdit")

    # Create horizontal layout
    manipLocRotHorizLayout = QHBoxLayout()
    manipLocRotHorizLayout.setObjectName(u"manipLocRotHorizLayout")

    # Create CheckBox
    self.manipLocRotCheckBox = CheckBoxWidget(parent=manipLocRotGroupBox, logger=self._logger,
                                              text=u"Local", minsize=QSize(50, 15))
    self.manipLocRotCheckBox.setObjectName(u"manipLocPosCheckBox")

    # Create ToolButton
    self.manipLocRotComboBox = ComboBoxWidget(parent=manipLocRotGroupBox, logger=self._logger,
                                              items=[u"x, y, z", u"a b c"], type="sub_combo_box",
                                              minsize=QSize(0, 15))
    self.manipLocRotComboBox.setObjectName(u"manipLocRotComboBox")

    # Add widgets to layout & set margins
    manipLocRotHorizLayout.addWidget(self.manipLocRotCheckBox)
    manipLocRotHorizLayout.addWidget(self.manipLocRotComboBox)
    manipLocRotHorizLayout.setContentsMargins(0, 0, 0, 0)
    manipLocRotHorizLayout.setSpacing(30)

    # Add widget to layout & set margins
    manipLocRotVertLayout.addWidget(self.manipLocXRotLineEdit)
    manipLocRotVertLayout.addWidget(self.manipLocYRotLineEdit)
    manipLocRotVertLayout.addWidget(self.manipLocZRotLineEdit)
    manipLocRotVertLayout.addLayout(manipLocRotHorizLayout)
    manipLocRotVertLayout.setContentsMargins(10, 20, 0, 0)
    manipLocRotVertLayout.setSpacing(3)

    return manipLocRotGroupBox

  def _create_manipulator_location_group_box(self) -> None:
    # Create group box
    self.manipLocPresetsGroupBox = QGroupBox(parent=self, title=u"Manipulator Location Presets")
    self.manipLocPresetsGroupBox.setObjectName(u"manipLocPresetsGroupBox")

    # Create Manipulator Location Vertical layout
    manipLocVerticalLayout = QVBoxLayout(self.manipLocPresetsGroupBox)
    manipLocVerticalLayout.setObjectName(u"manipLocVerticalLayout")

    # Create ComboBox
    self.manipLocSelectComboBox = ComboBoxWidget(parent=self.manipLocPresetsGroupBox,
                                                 logger=self._logger, items=[u"Custom", u"Auto"],
                                                 type="title_combo_box", minsize=QSize(0, 20))
    self.manipLocSelectComboBox.setObjectName(u"manipLocSelectComboBox")

    # Create sub group boxes layout
    manipLocGBhorizLayout = QHBoxLayout()
    manipLocGBhorizLayout.setObjectName(u"manipLocGBhorizLayout")

    # Create sub group boxes
    posGroupBox = self._create_manip_loc_pos_group_box(par=self.manipLocPresetsGroupBox)
    rotGroupBox = self._create_manip_loc_rot_group_box(par=self.manipLocPresetsGroupBox)

    # Add widgets to layout & set margins
    manipLocGBhorizLayout.addWidget(posGroupBox)
    manipLocGBhorizLayout.addWidget(rotGroupBox)
    manipLocGBhorizLayout.setContentsMargins(0, 0, 0, 0)
    manipLocGBhorizLayout.setSpacing(30)

    # Add widgets to layout & set margins
    manipLocVerticalLayout.addWidget(self.manipLocSelectComboBox)
    manipLocVerticalLayout.addLayout(manipLocGBhorizLayout)
    manipLocVerticalLayout.setContentsMargins(10, 20, 0, 0)
    manipLocVerticalLayout.setSpacing(5)

  # Manipulator location offset group box
  def _create_cam_mount_ofst_group_box(self, par: QWidget) -> QGroupBox:
    # create group box
    camMountOfstGroupBox = QGroupBox(parent=par, title=u"Offset")
    camMountOfstGroupBox.setObjectName(u"camMountOfstGroupBox")

    # Create vertical layout
    camMountOfstVertLayout = QVBoxLayout(camMountOfstGroupBox)
    camMountOfstVertLayout.setObjectName(u"camMountOfstVertLayout")

    # Create LineEdits
    self.camMountXOfstLineEdit = LineEditWidget(parent=camMountOfstGroupBox, logger=self._logger,
                                                ph_text=u"x", type="data", minsize=QSize(0, 15))
    self.camMountXOfstLineEdit.setObjectName(u"camMountXOfstLineEdit")

    self.camMountYOfstLineEdit = LineEditWidget(parent=camMountOfstGroupBox, logger=self._logger,
                                                ph_text=u"y", type="data", minsize=QSize(0, 15))
    self.camMountYOfstLineEdit.setObjectName(u"camMountYOfstLineEdit")

    self.camMountZOfstLineEdit = LineEditWidget(parent=camMountOfstGroupBox, logger=self._logger,
                                                ph_text=u"z", type="data", minsize=QSize(0, 15))
    self.camMountZOfstLineEdit.setObjectName(u"camMountZOfstLineEdit")

    # Create CheckBox
    self.camMountOfstCheckBox = CheckBoxWidget(parent=camMountOfstGroupBox, logger=self._logger,
                                               text=u"Local", minsize=QSize(50, 15))
    self.camMountOfstCheckBox.setObjectName(u"camMountOfstCheckBox")

    # Add widget to layout & set margins
    camMountOfstVertLayout.addWidget(self.camMountXOfstLineEdit)
    camMountOfstVertLayout.addWidget(self.camMountYOfstLineEdit)
    camMountOfstVertLayout.addWidget(self.camMountZOfstLineEdit)
    camMountOfstVertLayout.addWidget(self.camMountOfstCheckBox)
    camMountOfstVertLayout.setContentsMargins(10, 20, 0, 0)
    camMountOfstVertLayout.setSpacing(3)

    return camMountOfstGroupBox

  # Manipulator location rotation group box
  def _create_cam_mount_rot_group_box(self, par: QWidget) -> QGroupBox:
    # create group box
    camMountRotGroupBox = QGroupBox(parent=par, title=u"Rotation")
    camMountRotGroupBox.setObjectName(u"camMountRotGroupBox")

    # Create vertical layout
    camMountRotVertLayout = QVBoxLayout(camMountRotGroupBox)
    camMountRotVertLayout.setObjectName(u"camMountRotVertLayout")

    # Create LineEdits
    self.camMountXRotLineEdit = LineEditWidget(parent=camMountRotGroupBox, logger=self._logger,
                                               ph_text=u"x", type="data", minsize=QSize(0, 15))
    self.camMountXRotLineEdit.setObjectName(u"camMountXRotLineEdit")

    self.camMountYRotLineEdit = LineEditWidget(parent=camMountRotGroupBox, logger=self._logger,
                                               ph_text=u"y", type="data", minsize=QSize(0, 15))
    self.camMountYRotLineEdit.setObjectName(u"camMountYRotLineEdit")

    self.camMountZRotLineEdit = LineEditWidget(parent=camMountRotGroupBox, logger=self._logger,
                                               ph_text=u"z", type="data", minsize=QSize(0, 15))
    self.camMountZRotLineEdit.setObjectName(u"camMountZRotLineEdit")

    # Create horizontal layout
    camMountRotHorizLayout = QHBoxLayout()
    camMountRotHorizLayout.setObjectName(u"camMountRotHorizLayout")

    # Create CheckBox
    self.camMountRotCheckBox = CheckBoxWidget(parent=camMountRotGroupBox, logger=self._logger,
                                              text=u"Local", minsize=QSize(50, 15))
    self.camMountRotCheckBox.setObjectName(u"manipLocPosCheckBox")

    # Create ToolButton
    self.camMountRotComboBox = ComboBoxWidget(parent=camMountRotGroupBox, logger=self._logger,
                                              items=[u"x, y, z", u"a b c"],
                                              type="sub_combo_box", minsize=QSize(0, 15))
    self.camMountRotComboBox.setObjectName(u"camMountRotComboBox")

    # Add widgets to layout & set margins
    camMountRotHorizLayout.addWidget(self.camMountRotCheckBox)
    camMountRotHorizLayout.addWidget(self.camMountRotComboBox)
    camMountRotHorizLayout.setContentsMargins(0, 0, 0, 0)
    camMountRotHorizLayout.setSpacing(30)

    # Add widget to layout & set margins
    camMountRotVertLayout.addWidget(self.camMountXRotLineEdit)
    camMountRotVertLayout.addWidget(self.camMountYRotLineEdit)
    camMountRotVertLayout.addWidget(self.camMountZRotLineEdit)
    camMountRotVertLayout.addLayout(camMountRotHorizLayout)
    camMountRotVertLayout.setContentsMargins(10, 20, 0, 0)
    camMountRotVertLayout.setSpacing(3)

    return camMountRotGroupBox

  def _create_camera_mount_group_box(self) -> None:
    # Create group box
    self.camMountPresetsGroupBox = QGroupBox(parent=self, title=u"Camera Mount Presets")
    self.camMountPresetsGroupBox.setObjectName(u"camMountPresetsGroupBox")

    # Create Manipulator Location Vertical layout
    camMountVerticalLayout = QVBoxLayout(self.camMountPresetsGroupBox)
    camMountVerticalLayout.setObjectName(u"camMountVerticalLayout")

    # Create ComboBox
    self.camMountSelectComboBox = ComboBoxWidget(parent=self.camMountPresetsGroupBox,
                                                 logger=self._logger, items=[u"Custom", u"Auto"],
                                                 type="title_combo_box", minsize=QSize(0, 20))
    self.camMountSelectComboBox.setObjectName(u"camMountSelectComboBox")

    # Create sub group boxes layout
    camMountGBhorizLayout = QHBoxLayout()
    camMountGBhorizLayout.setObjectName(u"camMountGBhorizLayout")

    # Create sub group boxes
    posGroupBox = self._create_cam_mount_ofst_group_box(par=self.camMountPresetsGroupBox)
    rotGroupBox = self._create_cam_mount_rot_group_box(par=self.camMountPresetsGroupBox)

    # Add widgets to layout & set margins
    camMountGBhorizLayout.addWidget(posGroupBox)
    camMountGBhorizLayout.addWidget(rotGroupBox)
    camMountGBhorizLayout.setContentsMargins(0, 0, 0, 0)
    camMountGBhorizLayout.setSpacing(30)

    # Add widgets to layout & set margins
    camMountVerticalLayout.addWidget(self.camMountSelectComboBox)
    camMountVerticalLayout.addLayout(camMountGBhorizLayout)
    camMountVerticalLayout.setContentsMargins(10, 20, 0, 0)
    camMountVerticalLayout.setSpacing(5)


class ManipSettingsPage(QFrame):

  def __init__(self, **kwargs) -> None:
    self._parent = kwargs.get('parent', None)
    super(ManipSettingsPage, self).__init__(parent=self._parent)

    # logger
    self._logger = kwargs['logger']

    # Setup the page
    self.setObjectName(u"manipSettingsPage")
    if self._parent is None:
      self.resize(QSize(375, 382))

    self.init_UI()

  def init_UI(self) -> None:
    # Create widget layout
    manipSettingsPageVertLayout = QVBoxLayout(self)
    manipSettingsPageVertLayout.setObjectName(u"manipSettingsPageVertLayout")

    # Add widget
    self.manipSettingsLabel = LabelWidget(parent=self, logger=self._logger,
                                          text=u"Manipulator Settings Page")
    self.manipSettingsLabel.setObjectName(u"manipSettingsLabel")

    # Add widgets to layout & set margins
    manipSettingsPageVertLayout.addWidget(self.manipSettingsLabel)
    manipSettingsPageVertLayout.setContentsMargins(15, 0, 15, 0)
    manipSettingsPageVertLayout.setSpacing(20)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of subclassed QFrame
  artemis_ctrl_widget = ArtemisCtrlWidget()
  # Show the widget
  artemis_ctrl_widget.show()
  # Execute the program
  sys.exit(app.exec())