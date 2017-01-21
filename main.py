#!/usr/bin/env python3

import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        
        self.setIcon(self._parent.icon)
        self.setVisible(True)
        self.activated.connect(self.systrayActivated)
        
        menu = QtWidgets.QMenu(parent)
        show_action = menu.addAction("Show")
        show_action.triggered.connect(self.showWindow)
        hide_action = menu.addAction("Hide")
        hide_action.triggered.connect(self.hideWindow)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.exit)
        self.setContextMenu(menu)
        
    def exit(self):
        sys.exit()
        
    def showWindow(self):
        self._parent.show()
        
    def hideWindow(self):
        self._parent.hide()
        
    def systrayActivated(self, reason):
        if reason == self.Trigger:
            ''' left clic '''
            self.showWindow()
        

class ClipbordEdit(QtWidgets.QTextEdit):
    
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        #self.textChanged.connect(self.onTextChanged)
        
    #def onTextChanged(self):
        #self._parent.copyClicked()


class MainWindow(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.updateClicked)
        self.initUI()
        
    def initUI(self):
        
        self.clipbord_edit = ClipbordEdit(parent=self)
        self.clipbord_edit.setText(self.clipboard.text())
        copy_btn = QtWidgets.QPushButton('Copy to clipbord', self)
        copy_btn.clicked.connect(self.copyClicked)            
        normpath_btn = QtWidgets.QPushButton('Normpath', self)
        normpath_btn.clicked.connect(self.normpathClicked)
        to_slashes_btn = QtWidgets.QPushButton('/', self)
        to_slashes_btn.clicked.connect(self.backslashesToSlashesClicked)
        to_backslashes_btn = QtWidgets.QPushButton('\\', self)
        to_backslashes_btn.clicked.connect(self.slashesToBackslashesClicked)
        execute_btn = QtWidgets.QPushButton('Execute', self)
        execute_btn.clicked.connect(self.executeClicked)
        open_btn = QtWidgets.QPushButton('Open', self)
        open_btn.clicked.connect(self.openClicked)
        
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.clipbord_edit)
        grid.addWidget(copy_btn)
        grid.addWidget(normpath_btn)
        grid.addWidget(to_slashes_btn)
        grid.addWidget(to_backslashes_btn)
        grid.addWidget(execute_btn)
        grid.addWidget(open_btn)
        self.setLayout(grid) 
        
        filedir = os.path.dirname(__file__)
        iconpath = os.path.join(filedir, 'icons', 'accessories-text-editor.png')
        self.icon = QtGui.QIcon(iconpath)
        self.setWindowIcon(self.icon)
        
        self.resize(300, 200)
        self.setWindowTitle('Clipboard')    
        self.show()
        self.sysTray = SystemTrayIcon(self)
    
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()
        
    def copyClicked(self):
        text = self.clipbord_edit.toPlainText()
        self.clipboard.setText(text)
        
    def normpathClicked(self):
        text = self.clipbord_edit.toPlainText()
        text = os.path.normpath(text)
        self.clipboard.setText(text)
        
    def slashesToBackslashesClicked(self):
        text = self.clipbord_edit.toPlainText()
        text = text.replace('/', '\\')
        self.clipboard.setText(text)
    
    def backslashesToSlashesClicked(self):
        text = self.clipbord_edit.toPlainText()
        text = text.replace('\\', '/')
        self.clipboard.setText(text)
        
    def updateClicked(self):
        text = self.clipboard.text()
        self.clipbord_edit.setText(text)
        
    def executeClicked(self):
        text = self.clipbord_edit.toPlainText()
        try:
            p = subprocess.Popen(text)
        except:
            print(sys.exc_info())
        
    def openClicked(self):
        text = self.clipbord_edit.toPlainText()
        try:
            if sys.platform.startswith('linux'):
                p = subprocess.Popen(['xdg-open', text])
            elif sys.platform.startswith('win'):
                #os.system(text)
                p = subprocess.Popen(['start', text])
        except:
            print(sys.exc_info())
        




if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
