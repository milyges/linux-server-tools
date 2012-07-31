# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui
from app.ui.widgetLSTModules import Ui_widgetLSTModules
from app import config

class WidgetLSTModules(QtGui.QWidget):
    def __init__(self, server, parent = None):
        super(WidgetLSTModules, self).__init__(parent)
        
        self._server = server
        
        self._ui = Ui_widgetLSTModules()
        self._ui.setupUi(self)
    
        self._read_config()
        
    def _read_config_finished(self, code, stdout, stderr):
        if code != 0:
            return
    
        self._ui.lwModules.clear()
        modules = config.config_parse(stdout)        
        for m in modules:
            mi = QtGui.QListWidgetItem(self._ui.lwModules)
            miw = QtGui.QCheckBox()
            miw.setText(m[0][1:])
            if m[0][0] == '+':
                miw.setChecked(True)
            else:
                miw.setChecked(False)                
            self._ui.lwModules.setItemWidget(mi, miw)
        
    def _read_config(self):
        self._server.execute("cat %s/conf/modules.conf" % (self._server._lstdir), self._read_config_finished)
    
    def _save_config_finished(self, code, stdout, stderr):
        if code == 0:
            QtGui.QMessageBox.information(self, "Informacja", "Ustawienia zostały zapisane")
        else:
            QtGui.QMessageBox.critical(self, "Błąd", "Ustawienia nie zostały zapisane")
    
    def _save_config(self):
        data = "#\n# Lista modułów aktywnych(+) oraz nieaktywnych(-) na serwerze\n#\n\n"
        
        for i in range(self._ui.lwModules.count()):
            mi = self._ui.lwModules.item(i)
            miw = self._ui.lwModules.itemWidget(mi)
            
            if miw.isChecked():
                data = data + "+"
            else:
                data = data + "-"
                
            data = data + miw.text() + "\n"
            
        self._server.execute("echo \"%s\" > %s/conf/modules.conf" % (data, self._server._lstdir), self._save_config_finished)
        
    
    def selected(self):
        pass
    
    def cancel(self):
        self._read_config()
    
    def save(self):
        self._save_config()