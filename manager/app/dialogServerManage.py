# -*- coding: utf-8 -*-

from PyQt4 import QtCore,QtGui
from app.ui.dialogServerManage import Ui_DialogServerManage
import re

class DialogServerManage(QtGui.QDialog):
    def _update_uname(self, code, stdout, stderr):
        if code != 0:
            self._ui.lUname.setText("N/A")
        else:
            self._ui.lUname.setText(stdout)
    
    def _update_load_uptime(self):
        self._ui.lUptime.setText(self._server._item.text(4))
        self._ui.lLoad.setText(self._server._item.text(5))
        
    def _update_fs(self, code, stdout, stderr):
        self._ui.twFs.clear()
        
        if code != 0:
            return
        
        for fs in stdout.split("\n")[1:]:
            tmp = fs.split()
            
            if len(tmp) != 6:
                continue
            
            if re.match("^/dev/(.*)", tmp[0]):
                item = QtGui.QTreeWidgetItem(self._ui.twFs)
                item.setText(0, tmp[0])
                item.setText(1, tmp[1])
                item.setText(2, tmp[2])
                item.setText(3, tmp[3])
                item.setText(4, tmp[4])
                item.setText(5, tmp[5])
            
                inuse = int(tmp[4][:-1])
                
                if inuse > 95:
                    color = QtGui.QColor(255, 0, 0)
                elif inuse > 90:
                    color = QtGui.QColor(255, 255, 0)
                else:
                    color = QtGui.QColor(0, 255, 0)
                
                for i in range(6):
                    item.setBackgroundColor(i, color)
                  
    def _update_raid(self, code, stdout, stderr):
        self._ui.twRaid.clear()
        
        if code != 0:
            return
      
        data = stdout.split("\n")[1:-2]
      
        i = 0
        while i < len(data):
            tmp = data[i].split()
            item = QtGui.QTreeWidgetItem(self._ui.twRaid)
            item.setText(0, tmp[0])
            item.setText(1, tmp[3])
            item.setText(2, tmp[2])
            
            blocks = float(data[i + 1].split()[0])
            unit = 'K'
            
            if blocks > 1024:
                unit = 'M'
                blocks = blocks / 1024
                
            if blocks > 1024:
                unit = 'G'
                blocks = blocks / 1024
                    
            item.setText(3, "%d%s" % (round(blocks), unit))
            i = i + 3 
            
    def _update_ifaces(self, code, stdout, stderr):
        self._ui.twIfaces.clear()
        
        if code != 0:
            return
            
        data = stdout.split("\n")
        
        i = 0
        item = None
        
        while i < len(data):
            m = re.match("^([a-zA-Z0-9]+)[ ]+Link encap(.*)", data[i])            
            if m:
                item = QtGui.QTreeWidgetItem(self._ui.twIfaces)             
                item.setText(0, m.group(1))
                
            m = re.match("^[ ]+inet addr:([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", data[i])
            if m:
                item.setText(2, m.group(1))
                
            m = re.match("[ ]+([A-Z ]+)[ ]+MTU:[0-9]+[ ]+Metric:[0-9]+", data[i])
            if m:
                flags = m.group(1).split()
                if 'UP' in flags:
                    item.setText(1, "Aktywny")
                else:
                    item.setText(1, "Nieaktywny")
                    
            m = re.match("[ ]+RX bytes:([0-9]+) \(([0-9\.]+ [a-zA-Z]+)\)[ ]+TX bytes:([0-9]+) \(([0-9\.]+ [a-zA-Z]+)\)", data[i])
            if m:
                item.setText(3, m.group(2))
                item.setText(4, m.group(4))
                
            i = i + 1
            
    def _update_mem_info(self, code, stdout, stderr):
        self._ui.lmemUsage.setText("")
        self._ui.pbMemUsage.setValue(0)
        
        if code != 0:
            return
            
        data = stdout.split("\n")
    
        total = 0
        free = 0
        cached = 0
        buffers = 0
        
        for line in data:
            tmp = line.split()
            if not tmp:
                continue
            
            if tmp[0] == "MemTotal:":
                total = int(tmp[1])
            elif tmp[0] == "MemFree:":
                free = int(tmp[1])
            elif tmp[0] == "Buffers:":
                buffers = int(tmp[1])
            elif tmp[0] == "Cached:":
                cached = int(tmp[1])
                
        self._ui.pbMemUsage.setMaximum(total)
        self._ui.pbMemUsage.setValue(total - free - cached - buffers)
        
        self._ui.lmemUsage.setText("%dM/%dM" % (self._ui.pbMemUsage.value() / 1024, total / 1024))
        
    def _update_all_info(self):
        self._update_load_uptime()
        self._server.execute("df -h", self._update_fs)
        self._server.execute("cat /proc/mdstat", self._update_raid)
        self._server.execute("/sbin/ifconfig -a", self._update_ifaces)
        self._server.execute("cat /proc/meminfo", self._update_mem_info)
        
    def __init__(self, server, parent = None):
        super(DialogServerManage, self).__init__(parent)

        self._ui = Ui_DialogServerManage()
        self._ui.setupUi(self)

        self._server = server
        self._ui.lTitle.setText("Zarządzanie serwerem %s" % (server._item.text(1)))
        self.setWindowTitle("Zarządzanie serwerem %s" % (server._item.text(1)))
        
        self._ui.lUname.setText("Loading...")
        server.execute("uname -a", self._update_uname)
     
        self._update_all_info()
        
        self._update_timer = QtCore.QTimer(self)
        self.connect(self._update_timer, QtCore.SIGNAL("timeout()"), self._update_all_info)
        self._update_timer.setInterval(2000)
        self._update_timer.setSingleShot(False)
        self._update_timer.start()
        
        