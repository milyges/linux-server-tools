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
        
    def selected(self):
        pass

    def cancel(self):
        pass
    
    def save(self):
        pass