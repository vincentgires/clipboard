#!/usr/bin/env python3

import sys
import os
import subprocess
import json

user_folder = os.path.expanduser('~')
BOOKMARKS_FILE = os.path.join(user_folder, '.clipboard_bookmarks')



try:
    from PyQt5 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide import QtGui, QtCore
    from PySide import QtGui as QtWidgets

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        #super().__init__()
        super(SystemTrayIcon, self).__init__()
        self._parent = parent
        
        self.setToolTip('Clipboard manager')
        self.setIcon(self._parent.icon)
        self.setVisible(True)
        self.activated.connect(self.systrayActivated)
        #self.messageClicked.connect(self.messageClicked)
        
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
        self._parent.activateWindow()
        
    def hideWindow(self):
        self._parent.hide()
        
    def systrayActivated(self, reason):
        if reason == self.Trigger:
            ''' left clic '''
            self.showWindow()
    
    def messageClicked(self, *args, **kwargs):
        print('clic on message')
        
    
class ClipbordEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        #super().__init__()
        super(ClipbordEdit, self).__init__()
        self._parent = parent
        
        clipboard_text = parent.clipboard.text()
        self.setText(clipboard_text)
        
        #self.textChanged.connect(self.onTextChanged)
        
    #def onTextChanged(self):
        #self._parent.copyClicked()

class HistoryList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        #super().__init__()
        super(HistoryList, self).__init__()
        self._parent = parent
        #self.setFlow(QtWidgets.QListView().LeftToRight)
        
        clipboard_text = parent.clipboard.text()
        self.addItem(clipboard_text)
        
    def mouseDoubleClickEvent(self, event):
        current_item = self.currentItem()
        self._parent.clipbord_edit.setText(current_item.text())
    

class BookmarksList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        #super().__init__()
        super(BookmarksList, self).__init__()
        self._parent = parent
        #self.setFlow(QtWidgets.QListView().LeftToRight)
        if os.path.exists(BOOKMARKS_FILE):
            with open(BOOKMARKS_FILE, 'r') as file:
                items = json.load(file)
            for i in items:
                self.addItem(i)
        
    def mouseDoubleClickEvent(self, event):
        current_item = self.currentItem()
        self._parent.clipboard.setText(current_item.text())
        
    def addBookmark(self):
        text = self._parent.clipbord_edit.toPlainText()
        self.addItem(text)
        self.updateConfigFile()
        
    def removeBookmark(self):
        current_index = self.currentRow()
        self.takeItem(current_index)
        self.updateConfigFile()
        
    def getItems(self):
        items = []
        for i in range(self.count()):
            item = self.item(i).text()
            items.append(item)
        return items
    
    def updateConfigFile(self):
        with open(BOOKMARKS_FILE, 'w') as file:
            json.dump(self.getItems(), file)
    
class MainWindow(QtWidgets.QWidget):
    
    def __init__(self):
        #super().__init__()
        super(MainWindow, self).__init__()
        
        filedir = os.path.dirname(__file__)
        iconpath = os.path.join(filedir, 'icons',
                                'accessories-text-editor.png')
        
        self.icon = QtGui.QIcon(iconpath)
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.onNewClipboard)
        self.clipbord_edit = ClipbordEdit(self)
        self.clipbord_history = HistoryList(self)
        self.clipbord_bookmarks = BookmarksList(self)
        self.sysTray = SystemTrayIcon(self)
        
        self.initUI()
        
    def initUI(self):
        copy_btn = QtWidgets.QPushButton(self)
        copy_btn.setText('Copy to clipbord')
        copy_btn.clicked.connect(self.copyClicked)            
        normpath_btn = QtWidgets.QPushButton(self)
        normpath_btn.setText('Normpath')
        normpath_btn.clicked.connect(self.normpathClicked)
        to_slashes_btn = QtWidgets.QPushButton(self)
        to_slashes_btn.setText('/')
        to_slashes_btn.clicked.connect(self.backslashesToSlashesClicked)
        to_backslashes_btn = QtWidgets.QPushButton(self)
        to_backslashes_btn.setText('\\')
        to_backslashes_btn.clicked.connect(self.slashesToBackslashesClicked)
        execute_btn = QtWidgets.QPushButton(self)
        execute_btn.setText('Execute')
        execute_btn.clicked.connect(self.executeClicked)
        open_btn = QtWidgets.QPushButton(self)
        open_btn.setText('Open')
        open_btn.clicked.connect(self.openClicked)
        clearHistory_btn = QtWidgets.QPushButton(self)
        clearHistory_btn.setText('Clear history')
        clearHistory_btn.clicked.connect(self.clipbord_history.clear)
        addBookmark_btn = QtWidgets.QPushButton(self)
        addBookmark_btn.setText('Add bookmark')
        addBookmark_btn.clicked.connect(self.clipbord_bookmarks.addBookmark) 
        removeBookmark_btn = QtWidgets.QPushButton(self)
        removeBookmark_btn.setText('Remove bookmark')
        removeBookmark_btn.clicked.connect(self.clipbord_bookmarks.removeBookmark) 
        
        # LAYOUT -------------------
        wid_left = QtWidgets.QWidget()
        col = QtWidgets.QVBoxLayout()
        #col.setContentsMargins(0, 0, 0, 0)
        col.addWidget(self.clipbord_edit)
        col.addWidget(copy_btn)
        
        wid = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(normpath_btn)
        row.addWidget(to_slashes_btn)
        row.addWidget(to_backslashes_btn)
        wid.setLayout(row)
        col.addWidget(wid)
        
        wid = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(execute_btn)
        row.addWidget(open_btn)
        wid.setLayout(row)
        col.addWidget(wid)
        
        wid_left.setLayout(col)
        
        wid_right = QtWidgets.QWidget()
        col = QtWidgets.QVBoxLayout()
        col.addWidget(self.clipbord_history)
        col.addWidget(clearHistory_btn)
        col.addWidget(self.clipbord_bookmarks)
        col.addWidget(addBookmark_btn)
        col.addWidget(removeBookmark_btn)
        wid_right.setLayout(col)
        
        wid_main = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(wid_left)
        layout.addWidget(wid_right)
        wid_main.setLayout(layout)
        
        self.setLayout(layout)
        # ---------------------------
        

        self.setWindowIcon(self.icon)
        self.resize(500, 350)
        self.setWindowTitle('Clipboard')
    
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()
        
    def onNewClipboard(self):
        text = self.clipboard.text()
        self.clipbord_edit.setText(text)
        self.clipbord_history.addItem(text)
        #self.sysTray.showMessage('Clipboard', text)
        
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
    window.show()
    sys.exit(app.exec_())
