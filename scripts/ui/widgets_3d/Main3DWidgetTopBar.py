## -*- coding: utf-8 -*- #
##
##############################################################################################
##
## Software: ArteMotion
## Company: Brosky Media GmBH
## Developed By: Ravi Sharma
## Year: 2022
## Description: Script including classes to manage the top 3D area widget.
##
##############################################################################################
##
import os
import sys

from typing import Dict, List

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QApplication, QWidget, QFrame, QGridLayout, QHBoxLayout

try:
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget
except:
  # For development purpose only
  sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))))
  )
  from scripts.settings.Logger import Logger
  from scripts.ui.widgets_sub.SubWidgets import LabelWidget


class DummyLogger(Logger):

  pass


class Main3DWidgetTopBar(QFrame):

  update_label_value = Signal(dict)

  def __init__(self, parent: QWidget=None, logger: Logger=DummyLogger, height: int=30) -> None:
    super(Main3DWidgetTopBar, self).__init__(parent=parent)

    self._logger = logger
    self._height = height

    # Setup the top bar
    self.setObjectName(u"main3DTopRibbonFrame")
    self.setMinimumSize(QSize(0, self._height))
    self.setMaximumSize(QSize(16777215, self._height))
    self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
    
    self.init_UI()

    # Connections
    self._create_local_connects()

  def init_UI(self) -> None:
    # Create top bar layout
    main3DTopRibbonHorizLayout = QHBoxLayout(self)
    main3DTopRibbonHorizLayout.setObjectName(u"main3DTopRibbonHorizLayout")

    # Create axis grid layout
    axesLabelsGridLayout = QGridLayout()
    axesLabelsGridLayout.setObjectName(u"axesLabelsGridLayout")

    # Create labels
    # Simulate Axes labels
    sim_axes_labels = self._create_sim_axes_vars_labels()
    for idx, lbl in enumerate(sim_axes_labels):
      axesLabelsGridLayout.addWidget(lbl, 0, idx, 1, 1)
    # Actual Axes Labels
    act_axes_labels = self._create_act_axes_vars_labels()
    for idx, lbl in enumerate(act_axes_labels):
      axesLabelsGridLayout.addWidget(lbl, 1, idx, 1, 1)

    # Add widgets to grid layout & set margins
    axesLabelsGridLayout.setContentsMargins(0, 5, 0, 5)
    axesLabelsGridLayout.setSpacing(10)

    # Create cartesian grid layout
    cartLabelsGridLayout = QGridLayout()
    cartLabelsGridLayout.setObjectName(u"cartLabelsGridLayout")

    # Simulate Cartesian Labels
    sim_cart_labels = self._create_sim_cart_vars_labels()
    for idx, lbl in enumerate(sim_cart_labels):
      cartLabelsGridLayout.addWidget(lbl, 0, idx, 1, 1)
    # Actual Cartesian Labels
    act_cart_labels = self._create_act_cart_vars_labels()
    for idx, lbl in enumerate(act_cart_labels):
      cartLabelsGridLayout.addWidget(lbl, 1, idx, 1, 1)

    # Add widgets to grid layout & set margins
    cartLabelsGridLayout.setContentsMargins(0, 5, 0, 5)
    cartLabelsGridLayout.setSpacing(10)

    # Add widgets to the layout & set margins
    main3DTopRibbonHorizLayout.addLayout(axesLabelsGridLayout)
    main3DTopRibbonHorizLayout.addLayout(cartLabelsGridLayout)
    main3DTopRibbonHorizLayout.setContentsMargins(30, 0, 30, 0)
    main3DTopRibbonHorizLayout.setSpacing(50)

  def _create_sim_axes_vars_labels(self) -> List:
    # Create labels
    # Sim A1
    self.simA1Label = LabelWidget(parent=self, logger=self._logger, text=u"A1: 0000.000",
                                  type="data_label")
    self.simA1Label.setObjectName(u"simA1Label")

    # Sim A2
    self.simA2Label = LabelWidget(parent=self, logger=self._logger, text=u"A2: 0000.000",
                                  type="data_label")
    self.simA2Label.setObjectName(u"simA2Label")

    # Sim A3
    self.simA3Label = LabelWidget(parent=self, logger=self._logger, text=u"A3: 0000.000",
                                  type="data_label")
    self.simA3Label.setObjectName(u"simA3Label")

    # Sim A4
    self.simA4Label = LabelWidget(parent=self, logger=self._logger, text=u"A4: 0000.000",
                                  type="data_label")
    self.simA4Label.setObjectName(u"simA4Label")

    # Sim A5
    self.simA5Label = LabelWidget(parent=self, logger=self._logger, text=u"A5: 0000.000",
                                  type="data_label")
    self.simA5Label.setObjectName(u"simA5Label")

    # Sim A6
    self.simA6Label = LabelWidget(parent=self, logger=self._logger, text=u"A6: 0000.000",
                                  type="data_label")
    self.simA6Label.setObjectName(u"simA6Label")

    return  [self.simA1Label, self.simA2Label, self.simA3Label, self.simA4Label,
             self.simA5Label, self.simA6Label]

  def _create_act_axes_vars_labels(self) -> List:
    # Create labels
    # Act A1
    self.actA1Label = LabelWidget(parent=self, logger=self._logger, text=u"A1: 0000.000",
                                  type="data_label")
    self.actA1Label.setObjectName(u"actA1Label")

    # Act A2
    self.actA2Label = LabelWidget(parent=self, logger=self._logger, text=u"A2: 0000.000",
                                  type="data_label")
    self.actA2Label.setObjectName(u"actA2Label")

    # Act A3
    self.actA3Label = LabelWidget(parent=self, logger=self._logger, text=u"A3: 0000.000",
                                  type="data_label")
    self.actA3Label.setObjectName(u"actA3Label")

    # Act A4
    self.actA4Label = LabelWidget(parent=self, logger=self._logger, text=u"A4: 0000.000",
                                  type="data_label")
    self.actA4Label.setObjectName(u"actA4Label")

    # Act A5
    self.actA5Label = LabelWidget(parent=self, logger=self._logger, text=u"A5: 0000.000",
                                  type="data_label")
    self.actA5Label.setObjectName(u"actA5Label")

    # Act A6
    self.actA6Label = LabelWidget(parent=self, logger=self._logger, text=u"A6: 0000.000",
                                  type="data_label")
    self.actA6Label.setObjectName(u"actA6Label")

    return  [self.actA1Label, self.actA2Label, self.actA3Label, self.actA4Label,
             self.actA5Label, self.actA6Label]

  def _create_sim_cart_vars_labels(self) -> List:
    # Sim X
    self.simXLabel = LabelWidget(parent=self, logger=self._logger, text=u"X: 0000.000",
                                 type="data_label")
    self.simXLabel.setObjectName(u"simXLabel")

    # Sim Y
    self.simYLabel = LabelWidget(parent=self, logger=self._logger, text=u"Y: 0000.000",
                                 type="data_label")
    self.simYLabel.setObjectName(u"simYLabel")

    # Sim Z
    self.simZLabel = LabelWidget(parent=self, logger=self._logger, text=u"Z: 0000.000",
                                 type="data_label")
    self.simZLabel.setObjectName(u"simZLabel")

    # Sim A
    self.simALabel = LabelWidget(parent=self, logger=self._logger, text=u"A: 0000.000",
                                 type="data_label")
    self.simALabel.setObjectName(u"simALabel")

    # Sim B
    self.simBLabel = LabelWidget(parent=self, logger=self._logger, text=u"B: 0000.000",
                                 type="data_label")
    self.simBLabel.setObjectName(u"simBLabel")

    # Sim C
    self.simCLabel = LabelWidget(parent=self, logger=self._logger, text=u"C: 0000.000",
                                 type="data_label")
    self.simCLabel.setObjectName(u"simCLabel")

    # Sim RollUp
    self.simRollUpLabel = LabelWidget(parent=self, logger=self._logger, text=u"RollUp: 0000.000",
                                      type="data_label")
    self.simRollUpLabel.setObjectName(u"simRollUpLabel")

    # Sim Pol
    self.simPolLabel = LabelWidget(parent=self, logger=self._logger, text=u"Pol: 0000.000",
                                   type="data_label")
    self.simPolLabel.setObjectName(u"simPolLabel")

    return  [self.simXLabel, self.simYLabel, self.simZLabel, self.simALabel,
             self.simBLabel, self.simCLabel, self.simRollUpLabel, self.simPolLabel]

  def _create_act_cart_vars_labels(self) -> List:
    # Sim X
    self.actXLabel = LabelWidget(parent=self, logger=self._logger, text=u"X: 0000.000",
                                 type="data_label")
    self.actXLabel.setObjectName(u"actXLabel")

    # Act Y
    self.actYLabel = LabelWidget(parent=self, logger=self._logger, text=u"Y: 0000.000",
                                 type="data_label")
    self.actYLabel.setObjectName(u"actYLabel")

    # Act Z
    self.actZLabel = LabelWidget(parent=self, logger=self._logger, text=u"Z: 0000.000",
                                 type="data_label")
    self.actZLabel.setObjectName(u"actZLabel")

    # Act A
    self.actALabel = LabelWidget(parent=self, logger=self._logger, text=u"A: 0000.000",
                                 type="data_label")
    self.actALabel.setObjectName(u"actALabel")

    # Act B
    self.actBLabel = LabelWidget(parent=self, logger=self._logger, text=u"B: 0000.000",
                                 type="data_label")
    self.actBLabel.setObjectName(u"actBLabel")

    # Act C
    self.actCLabel = LabelWidget(parent=self, logger=self._logger, text=u"C: 0000.000",
                                 type="data_label")
    self.actCLabel.setObjectName(u"actCLabel")

    # Act RollUp
    self.actRollUpLabel = LabelWidget(parent=self, logger=self._logger, text=u"RollUp: 0000.000",
                                      type="data_label")
    self.actRollUpLabel.setObjectName(u"actRollUpLabel")

    # Act Pol
    self.actPolLabel = LabelWidget(parent=self, logger=self._logger, text=u"Pol: 0000.000",
                                   type="data_label")
    self.actPolLabel.setObjectName(u"actPolLabel")

    return  [self.actXLabel, self.actYLabel, self.actZLabel, self.actALabel,
             self.actBLabel, self.actCLabel, self.actRollUpLabel, self.actPolLabel]

  def _create_local_connects(self) -> None:
    # Signals
    self.update_label_value.connect(self._on_updated_label_value_recvd)

  def _on_updated_label_value_recvd(self, data: Dict) -> None:
    if not isinstance(data, dict):
      self._logger.warning("Invalid data received")
      return
    if 'label_name' not in data:
      self._logger.warning("Data does not contain label name")
      return
    if 'label_value' not in data:
      self._logger.warning("Data does not contain label value")
      return

    # Simulate Axes labels
    if data['label_name'] == 'sim_a1_label':
      self.simA1Label.setText(f"A1: {data['label_value']}")
    if data['label_name'] == 'sim_a2_label':
      self.simA2Label.setText(f"A2: {data['label_value']}")
    if data['label_name'] == 'sim_a3_label':
      self.simA3Label.setText(f"A3: {data['label_value']}")
    if data['label_name'] == 'sim_a4_label':
      self.simA4Label.setText(f"A4: {data['label_value']}")
    if data['label_name'] == 'sim_a5_label':
      self.simA5Label.setText(f"A5: {data['label_value']}")
    if data['label_name'] == 'sim_a6_label':
      self.simA6Label.setText(f"A6: {data['label_value']}")

    # Actual Axes labels
    if data['label_name'] == 'act_a1_label':
      self.actA1Label.setText(f"A1: {data['label_value']}")
    if data['label_name'] == 'act_a2_label':
      self.actA2Label.setText(f"A2: {data['label_value']}")
    if data['label_name'] == 'act_a3_label':
      self.actA3Label.setText(f"A3: {data['label_value']}")
    if data['label_name'] == 'act_a4_label':
      self.actA4Label.setText(f"A4: {data['label_value']}")
    if data['label_name'] == 'act_a5_label':
      self.actA5Label.setText(f"A5: {data['label_value']}")
    if data['label_name'] == 'act_a6_label':
      self.actA6Label.setText(f"A6: {data['label_value']}")

    # Simulate cartesian labels
    if data['label_name'] == 'sim_x_label':
      self.simXLabel.setText(f"X: {data['label_value']}")
    if data['label_name'] == 'sim_y_label':
      self.simYLabel.setText(f"Y: {data['label_value']}")
    if data['label_name'] == 'sim_z_label':
      self.simZLabel.setText(f"Z: {data['label_value']}")
    if data['label_name'] == 'sim_a_label':
      self.simALabel.setText(f"A: {data['label_value']}")
    if data['label_name'] == 'sim_b_label':
      self.simBLabel.setText(f"B: {data['label_value']}")
    if data['label_name'] == 'sim_c_label':
      self.simCLabel.setText(f"C: {data['label_value']}")
    if data['label_name'] == 'sim_rollup_label':
      self.simRollUpLabel.setText(f"RollUp: {data['label_value']}")
    if data['label_name'] == 'sim_pol_label':
      self.simPolLabel.setText(f"Pol: {data['label_value']}")

    # Actual cartesian labels
    if data['label_name'] == 'act_x_label':
      self.actXLabel.setText(f"X: {data['label_value']}")
    if data['label_name'] == 'act_y_label':
      self.actYLabel.setText(f"Y: {data['label_value']}")
    if data['label_name'] == 'act_z_label':
      self.actZLabel.setText(f"Z: {data['label_value']}")
    if data['label_name'] == 'act_a_label':
      self.actALabel.setText(f"A: {data['label_value']}")
    if data['label_name'] == 'act_b_label':
      self.actBLabel.setText(f"B: {data['label_value']}")
    if data['label_name'] == 'act_c_label':
      self.actCLabel.setText(f"C: {data['label_value']}")
    if data['label_name'] == 'act_rollup_label':
      self.actRollUpLabel.setText(f"RollUp: {data['label_value']}")
    if data['label_name'] == 'act_pol_label':
      self.actPolLabel.setText(f"Pol: {data['label_value']}")

  def closeEvent(self, event: QCloseEvent) -> None:
    return super(Main3DWidgetTopBar, self).closeEvent(event)


if __name__ == '__main__':
  """For development purpose only"""
  # Create an instance of QApplication
  app = QApplication(sys.argv)
  # Create an instance of top bar
  top_bar = Main3DWidgetTopBar()
  # It helps to delete old/empty log files
  top_bar._logger.remove_log_files()
  # Show the top bar
  top_bar.show()
  # execute the program
  sys.exit(app.exec())