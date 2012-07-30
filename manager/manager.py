# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore,QtGui
from app.mainWindow import MainWindow

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("UTF-8"))
    QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForName("UTF-8"))
    
    QtCore.qDebug("Starting...")

    wnd = MainWindow()
    wnd.show()
    
    sys.exit(app.exec_())