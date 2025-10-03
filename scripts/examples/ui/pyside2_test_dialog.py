from PySide6 import QtCore
from PySide6 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui


def maya_main_window():
  """
  Return the Maya main window widget as a Python object
  """
  main_window_ptr = omui.MQtUtil.mainWindow()
  return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class TestDialog(QtWidgets.QDialog):

  def __init__(self, parent=maya_main_window()):
    super(TestDialog, self).__init__(parent)

    self.setWindowTitle("Test Dialog")
    self.setMinimumWidth(200)
    self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)


if __name__ == '__main__':
  dialog = TestDialog()
  dialog.show()
