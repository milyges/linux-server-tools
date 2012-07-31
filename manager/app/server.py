# -*- coding: utf-8 -*-

import socket
import libssh2

from PyQt4 import QtCore, QtGui

STATUS_ONLINE = 0
STATUS_OFFLINE = 1
STATUS_AUTHERR = 2

class ServerCommand:
    def __init__(self):
        self.command = None
        self.exitcode = 0        
        self.stdout = None
        self.stderr = None
        self.callback = None
        self.dataptr = None
        
class ServerThread(QtCore.QThread):
    
    def __init__(self, addr, port, user, keys, parent = None):
        super(ServerThread, self).__init__(parent)
        
        self._addr = addr
        self._port = port
        self._user = user
        self._keys = keys
        
        self._done = False
        self._socket = None
        self._session = None
        self._command_queue = []
        self._command_queue_mutex = QtCore.QMutex()
        
    def run(self):
        self.emit(QtCore.SIGNAL("updateStatus(int)"), STATUS_OFFLINE)
        while not self._done:
            
            # Probojemy sie podlaczyc
            if not self._socket:
                try:
                    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self._socket.connect((self._addr, self._port))
                except socket.error as e:
                    QtCore.qDebug("[thread] %s: unable to connect: %s" % (self._addr, e))
                    self._socket = None
                    self.sleep(5)
                    continue
                
                QtCore.qDebug("[thread] %s: connected" % (self._addr))
                
            if not self._session:
                try:
                    self._session = libssh2.Session()
                    self._session.startup(self._socket)                    
                    self._session.userauth_publickey_fromfile(self._user, self._keys[0], self._keys[1])
                    self.emit(QtCore.SIGNAL("updateStatus(int)"), STATUS_ONLINE)
                except libssh2.Error as e:
                    QtCore.qDebug("[thread] %s: unable to connect: %s" % (self._addr, e))
                    self.emit(QtCore.SIGNAL("updateStatus(int)"), STATUS_AUTHERR)
                    self._session = None
                    self._socket = None
                    self._done = True
                    continue
                
            # Sprawdzamy czy są nowe polecenia do wykonania
            self._command_queue_mutex.lock()
            if not len(self._command_queue):
                self._command_queue_mutex.unlock()
                self.sleep(1)            
                continue
                        
            cmd = self._command_queue[0]
            del self._command_queue[0]
            self._command_queue_mutex.unlock()
            
            
            chan = self._session.channel()
            chan.execute(cmd.command)            
            
            stdout = []
            stderr = []
            
            while not chan.eof:
                data = chan.read(1024)
                if data:
                    stdout.append(data)
 
                data = chan.read(1024, libssh2.STDERR)
                if data:
                    stderr.append(data)
            
            cmd.stdout = ''.join(stdout)
            cmd.stderr = ''.join(stderr)
            cmd.exitcode = chan.get_exit_status()
            
            self.emit(QtCore.SIGNAL("commandFinished(PyQt_PyObject)"), cmd)
            
            chan.wait_closed()
        
    def set_done(self):
        self._done = True
               
    def add_command(self, cmd, callback):
        sc = ServerCommand()
        sc.callback = callback
        sc.command = cmd
                
        self._command_queue_mutex.lock()
        self._command_queue.append(sc)
        self._command_queue_mutex.unlock()
    
class Server(QtCore.QObject):
    
    def _update_status_slot(self, status):
        QtCore.qDebug("%s: update status to %d" % (self._addr, status))
        self._status = status
        
        if status == STATUS_ONLINE:
            self._item.setText(0, "Online")
            color = QtGui.QColor(0, 255, 0)
        elif status == STATUS_AUTHERR:
            self._item.setText(0, "Blad autoryzacji")
            color = QtGui.QColor(255, 255, 0)
        elif status == STATUS_OFFLINE:
            self._item.setText(0, "Offline")
            color = QtGui.QColor(255, 0, 0)
        else:
            self._item.setText(0, "Nieznany")
            color = QtGui.QColor(255, 255, 255)
        
        for i in range(6):
            self._item.setBackgroundColor(i, color)
        
    def _command_finished(self, sc):
#        QtCore.qDebug("%s: command %s exited with status %d" % (self._addr, sc.command, sc.exitcode))
        if sc.callback:
            sc.callback(sc.exitcode, sc.stdout, sc.stderr)
    
    def __init__(self, addr, port, user, keys, item, parent = None):
        QtCore.QObject.__init__(self, parent)

        self._addr = addr
        self._status = STATUS_OFFLINE        
        self._thread = ServerThread(addr, port, user, keys, self)
        self.connect(self._thread, QtCore.SIGNAL("updateStatus(int)"), self._update_status_slot)
        self.connect(self._thread, QtCore.SIGNAL("commandFinished(PyQt_PyObject)"), self._command_finished)
        
        self._item = item
        item.server = self
        
        self._item.setText(3, self._addr)
        
    def start(self):
        self._thread.start()
    
    def stop(self):
        self._thread.set_done()
        self._thread.terminate()
        self._thread.wait()
        
    def set_info(self, name, desc):
        self._item.setText(1, name)
        self._item.setText(2, desc)
       
    def status(self):
        return self._status
    
    def execute(self, cmd, callback):
        self._thread.add_command(cmd, callback)
    
    def _update_load_cb(self, code, stdout, stderr):
        if code != 0:
            self._item.setText(5, "N/A")
        else:
            self._item.setText(5, ", ".join(stdout.split(" ")[0:3]))
            
    def _update_uptime_cb(self, code, stdout, stderr):
        if code != 0:
            self._item.setText(4, "N/A")
        else:
            tmp = int(round(float(stdout.split(" ")[0])))
            uptime = "%ds" % (tmp % 60)
            
            tmp = tmp / 60
            if tmp > 0:
                uptime = "%dm " % (tmp % 60) + uptime
                tmp = tmp / 60
                
            if tmp > 0:
                uptime = "%dh " % (tmp % 24) + uptime
                tmp = tmp / 24
                
            if tmp > 0:
                uptime = "%dd " % (tmp) + uptime
                
            self._item.setText(4, uptime)
            
    def update_load(self):
        if self._status != STATUS_ONLINE:
            self._item.setText(5, "N/A")
        else:
            self.execute("cat /proc/loadavg", self._update_load_cb)
        
    def update_uptime(self):
        if self._status != STATUS_ONLINE:
            self._item.setText(4, "N/A")
        else:
            self.execute("cat /proc/uptime", self._update_uptime_cb)
