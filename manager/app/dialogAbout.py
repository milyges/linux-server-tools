# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui
from app.ui.dialogAbout import Ui_DialogAbout
 
class DialogAbout(QtGui.QDialog):
    def __init__(self, parent = None):
        super(DialogAbout, self).__init__(parent)

        self._ui = Ui_DialogAbout()
        self._ui.setupUi(self)
        