# -*- coding: utf-8 -*-

import os

from PyQt4 import QtCore,QtGui
from app.ui.mainWindow import Ui_MainWindow
from app.dialogAddServer import DialogAddServer
from app.dialogServerManage import DialogServerManage
from app.dialogAbout import DialogAbout

from app.server import Server

class MainWindow(QtGui.QMainWindow):
    
    def _update_list(self):
        for s in self._servers:
            s.update_uptime()
            s.update_load()
    
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self.connect(self._ui.aServerAdd, QtCore.SIGNAL("triggered()"), self._action_add_server)
        self.connect(self._ui.aServerRemove, QtCore.SIGNAL("triggered()"), self._action_remove_server)
        self.connect(self._ui.aHelpAbout, QtCore.SIGNAL("triggered()"), self._show_about)
        self.connect(self._ui.twServers, QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem *,int)"), self._action_manage_server)
                     
        self._updateTimer = QtCore.QTimer(self)
        self._updateTimer.setInterval(2000)
        self._updateTimer.setSingleShot(False)
        self.connect(self._updateTimer, QtCore.SIGNAL("timeout()"), self._update_list)
        self._updateTimer.start()
        
        self._servers = []
        
        self._settings = QtCore.QSettings("linux-server-tools", "manager")
        self._settings.beginGroup("ui")
        self.setGeometry(self._settings.value("geometry", self.geometry()).toRect())
        
        for i in range(6):
            self._ui.twServers.header().resizeSection(i, self._settings.value("col%d" % (i), self._ui.twServers.header().sectionSize(i)).toInt()[0])
            
        self._settings.endGroup()
        
        self._settings.beginGroup("servers")
        
        for server in self._settings.childGroups():
            self._settings.beginGroup(server)
            
            s = Server(self._settings.value("addr").toString(), self._settings.value("port").toInt()[0], str(self._settings.value("user").toString()), (str(self._settings.value("key1").toString()), str(self._settings.value("key2").toString())), QtGui.QTreeWidgetItem(self._ui.twServers))
            s.set_info(server, self._settings.value("desc").toString())
            self._servers.append(s)
            
            self._settings.endGroup()            
                
        self._settings.endGroup()
        
        for s in self._servers:
            s.start()
       
    def _show_about(self):
        dialog = DialogAbout()
        dialog.exec_()
        
    def _add_server(self, name, desc, addr, port, user, keys):
        server = Server(addr, port, user, keys, QtGui.QTreeWidgetItem(self._ui.twServers))        
        
        self._settings.beginGroup("servers/%s" % (name))
        
        self._settings.setValue("desc", desc)
        self._settings.setValue("addr", addr)
        self._settings.setValue("port", 22)
        self._settings.setValue("user", user)
        self._settings.setValue("key1", keys[0])
        self._settings.setValue("key2", keys[1])
        
        self._settings.endGroup()        
        
        self._servers.append(server)
        server.set_info(name, desc)
        server.start()
    
    def _save_server(self):
        dialog = self.sender()
        
        if not dialog._ui.leName.text() or not dialog._ui.leDesc.text() or not dialog._ui.leAddr.text() or not dialog._ui.leUser.text() or not dialog._ui.leKey1.text() or not dialog._ui.leKey2.text(): 
            QtGui.QMessageBox.critical(self, "Błąd", "Wszystkie pola są wymagane!")
        else:
            # TODO: Sprawdz czy edycja czy nowy oraz czy juz nie istnieje
            
            self._add_server(dialog._ui.leName.text(), dialog._ui.leDesc.text(), dialog._ui.leAddr.text(), dialog._ui.sbPort.value(), str(dialog._ui.leUser.text()), (os.path.expanduser(str(dialog._ui.leKey1.text())), os.path.expanduser(str(dialog._ui.leKey2.text()))))
        
    def _action_add_server(self):
        dialog = DialogAddServer(self)
        self.connect(dialog, QtCore.SIGNAL("accepted()"), self._save_server)
        dialog.setWindowTitle("Dodaj nowy serwer")
        dialog.show()
    
    def _action_remove_server(self):        
        if not len(self._ui.twServers.selectedItems()):
            return
        
        si = self._ui.twServers.selectedItems()[0]
        
        box = QtGui.QMessageBox()
        box.setText("Usuwanie serwera")
        box.setInformativeText("Czy na pewno usunąć serwer %s z listy?" % (si.text(1)))
        box.setStandardButtons(box.Ok | box.Cancel)
        box.setIcon(box.Question)
                       
        if box.exec_() == box.Cancel:
            return
        
        si.server.stop()
          
        self._servers.remove(si.server)
        self._ui.twServers.takeTopLevelItem(self._ui.twServers.indexOfTopLevelItem(si))

        self._settings.remove("servers/%s" % (si.text(1)))    
        si.server = None
        
    def _action_manage_server(self, item, column):        
        dialog = DialogServerManage(item.server, self)
        dialog.show()
        
    def closeEvent(self, *args, **kwargs):
        for s in self._servers:
            s.stop()
        
        self._settings.beginGroup("ui")
        self._settings.setValue("geometry", self.geometry())
        for i in range(6):
            self._settings.setValue("col%d" % (i), self._ui.twServers.header().sectionSize(i))
        self._settings.endGroup()
        
        return QtGui.QMainWindow.closeEvent(self, *args, **kwargs)
    