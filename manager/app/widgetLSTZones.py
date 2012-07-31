# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui
from app.ui.widgetLSTZones import Ui_widgetLSTZones
from app import config

class WidgetLSTZones(QtGui.QWidget):
    def __init__(self, server, parent = None):
        super(WidgetLSTZones, self).__init__(parent)
        
        self._server = server
        
        self._ui = Ui_widgetLSTZones()
        self._ui.setupUi(self)

        self.connect(self._ui.bntAddZone, QtCore.SIGNAL('clicked()'), self._add_zone)
        self.connect(self._ui.bntRemoveZone, QtCore.SIGNAL('clicked()'), self._remove_zone)
        
        self._read_config()
        
    def _add_zone(self):
        item = QtGui.QTreeWidgetItem(self._ui.twZones)
        item.setText(0, "Nazwa")
        item.setText(1, "iface")
        item.setText(2, "0.0.0.0/0")
        item.setText(3, "")
        item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self._ui.twZones.editItem(item, 0)
        
    def _remove_zone(self):
        for idx in self._ui.twZones.selectedIndexes():
            self._ui.twZones.takeTopLevelItem(idx.row())
    
    def _read_config_finished(self, code, stdout, stderr):
        if code != 0:
            return
        
        self._ui.twZones.clear()
        zones = config.config_parse(stdout)
        for z in zones:
            item = QtGui.QTreeWidgetItem(self._ui.twZones)
            
            item.setText(0, z[0])
            item.setText(1, z[1])
            item.setText(2, z[2])
            
            try:
                item.setText(3, " ".join(z[3:]))
            except:
                pass
            
            item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
    def _read_config(self):
        self._server.execute("cat %s/conf/zones.conf" % (self._server._lstdir), self._read_config_finished)
        
    def _save_config_finished(self, code, stdout, stderr):
        if code == 0:
            QtGui.QMessageBox.information(self, "Informacja", "Ustawienia zostały zapisane")
        else:
            QtGui.QMessageBox.critical(self, "Błąd", "Ustawienia nie zostały zapisane")
    
    def _save_config(self):
        data = "#\n# Strefy występujące w sieci\n#\n# Nazwa\tinterfejs\tadres\t\tkomentarz\n"
        
        for i in range(self._ui.twZones.topLevelItemCount()):
            item = self._ui.twZones.topLevelItem(i)
            
            data = data + "%s\t%s\t\t%s\t%s\n" % (item.text(0), item.text(1), item.text(2), item.text(3))
                
        self._server.execute("echo \"%s\" > %s/conf/zones.conf" % (data, self._server._lstdir), self._save_config_finished)
        
    def selected(self):
        pass

    def cancel(self):
        self._read_config()
    
    def save(self):
        self._save_config()
            