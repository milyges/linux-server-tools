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

    def selected(self):
        pass

    def cancel(self):
        pass
    
    def save(self):
        pass
            