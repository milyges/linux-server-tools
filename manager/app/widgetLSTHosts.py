# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui
from app.ui.widgetLSTHosts import Ui_widgetLSTHosts
from app import config

class WidgetLSTHosts(QtGui.QWidget):
    def __init__(self, server, parent = None):
        super(WidgetLSTHosts, self).__init__(parent)
        
        self._server = server
        
        self._ui = Ui_widgetLSTHosts()
        self._ui.setupUi(self)
        
        self.connect(self._ui.bntAddHost, QtCore.SIGNAL('clicked()'), self._add_host)
        self.connect(self._ui.bntRemoveHost, QtCore.SIGNAL('clicked()'), self._remove_host)
        
    def _add_host(self):
        item = QtGui.QTreeWidgetItem(self._ui.twHosts)
        cbZones = QtGui.QComboBox()
        cbZones.addItems(self._zones)
        self._ui.twHosts.setItemWidget(item, 0, cbZones)
        item.setText(1, 'nowy')
        item.setText(2, '0.0.0.0')
        item.setText(3, '00:00:00:00:00:00')
        item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self._ui.twHosts.editItem(item, 1)
        
    def _remove_host(self):
        for idx in self._ui.twHosts.selectedIndexes():
            self._ui.twHosts.takeTopLevelItem(idx.row())
    
    def _save_config_finished(self, code, stdout, stderr):
        if code == 0:
            QtGui.QMessageBox.information(self, "Informacja", "Ustawienia zostały zapisane")
        else:
            QtGui.QMessageBox.critical(self, "Błąd", "Ustawienia nie zostały zapisane")
    
    def _save_config(self):
        data = "#\n# Hosty występujące w sieci\n#\n# Strefa\tNazwa\tip\t\tmac\t\t\tkomentarz\n"
        
        for i in range(self._ui.twHosts.topLevelItemCount()):
            item = self._ui.twHosts.topLevelItem(i)
            cbZones = self._ui.twHosts.itemWidget(item, 0)
            data = data + "%s\t\t%s\t%s\t%s\t%s\n" % (cbZones.currentText(), item.text(1), item.text(2), item.text(3), item.text(4))
                
        self._server.execute("echo \"%s\" > %s/conf/hosts.conf" % (data, self._server._lstdir), self._save_config_finished)
        
    def _read_config_finished(self, code, stdout, stderr):
        if code != 0:
            return
        
        self._ui.twHosts.clear()
        hosts = config.config_parse(stdout)
        
        for host in hosts:
            item = QtGui.QTreeWidgetItem(self._ui.twHosts)
            cbZones = QtGui.QComboBox()
            cbZones.addItems(self._zones)                
            cbZones.setCurrentIndex(cbZones.findText(host[0]))
            self._ui.twHosts.setItemWidget(item, 0, cbZones)
            item.setText(1, host[1])
            item.setText(2, host[2])
            item.setText(3, host[3])
            try:
                item.setText(4, " ".join(host[4:]))
            except:
                pass
            
            item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            
    def _read_config(self):
        self._server.execute("cat %s/conf/hosts.conf" % (self._server._lstdir), self._read_config_finished)
    
    def _read_zones_finished(self, code, stdout, stderr):
        if code != 0:
            return
        
        self._zones = [ ]
        zones = config.config_parse(stdout)
        for z in zones:
            self._zones.append(z[0])
            
        self._read_config()
        
    def _read_zones(self):
        self._server.execute("cat %s/conf/zones.conf" % (self._server._lstdir), self._read_zones_finished)
    
    def selected(self):
        self._read_zones()
                
    def cancel(self):
        self._read_config()
    
    def save(self):
        self._save_config()