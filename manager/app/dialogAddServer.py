# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui
from app.ui.dialogAddServer import Ui_DialogAddServer
 
class DialogAddServer(QtGui.QDialog):
    
    def __init__(self, parent = None):
        super(DialogAddServer, self).__init__(parent)

        self._ui = Ui_DialogAddServer()
        self._ui.setupUi(self)
        