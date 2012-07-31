# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from app.ui.dialogSettings import Ui_DialogSettings
 
class DialogSettings(QtGui.QDialog):
    def __init__(self, parent = None):
        super(DialogSettings, self).__init__(parent)

        self._ui = Ui_DialogSettings()
        self._ui.setupUi(self)
        