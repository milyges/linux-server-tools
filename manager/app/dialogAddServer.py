# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui
from app.ui.dialogAddServer import Ui_DialogAddServer
 
class DialogAddServer(QtGui.QDialog):
    
    def _select_key1(self):
        dialog = QtGui.QFileDialog()
        
        k1 = dialog.getOpenFileName(self, "Wybierz klucz publiczny")
        if k1:
            self._ui.leKey1.setText(k1)
      
    def _select_key2(self):
        dialog = QtGui.QFileDialog()
        
        k2 = dialog.getOpenFileName(self, "Wybierz klucz prywatny")
        if k2:
            self._ui.leKey2.setText(k2)
                  
    def __init__(self, parent = None):
        super(DialogAddServer, self).__init__(parent)

        self._ui = Ui_DialogAddServer()
        self._ui.setupUi(self)
        
        self.connect(self._ui.bntSelectKey1, QtCore.SIGNAL("clicked()"), self._select_key1)
        self.connect(self._ui.bntSelectKey2, QtCore.SIGNAL("clicked()"), self._select_key2)
        