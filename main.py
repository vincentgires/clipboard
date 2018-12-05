#!/usr/bin/env python3

import sys
import os
import subprocess
import json
from PySide2 import QtWidgets, QtGui, QtCore

_user_folder = os.path.expanduser('~')
BOOKMARKS_FILE = os.path.join(_user_folder, '.clipboard_bookmarks')


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent

        self.setToolTip('Clipboard manager')
        self.setIcon(self._parent.icon)
        self.setVisible(True)
        self.activated.connect(self.systray_activated)

        menu = QtWidgets.QMenu(parent)
        open_action = menu.addAction('Open clipboard')
        open_action.triggered.connect(self._parent.open_clicked)
        execute_action = menu.addAction('Execute clipboar')
        execute_action.triggered.connect(self._parent.execute_clicked)
        show_action = menu.addAction('Show window')
        show_action.triggered.connect(self.show_window)
        hide_action = menu.addAction('Hide window')
        hide_action.triggered.connect(self.hide_window)
        exit_action = menu.addAction('Exit')
        exit_action.triggered.connect(self.exit)
        self.setContextMenu(menu)

    def exit(self):
        sys.exit()

    def show_window(self):
        self._parent.show()
        self._parent.activateWindow()
        self._parent.setWindowState(
            self._parent.windowState()
            & ~QtCore.Qt.WindowMinimized
            | QtCore.Qt.WindowActive)

    def hide_window(self):
        self._parent.hide()

    def systray_activated(self, reason):
        if reason == self.Trigger:
            self.show_window()


class ClipbordEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent

        clipboard_text = parent.clipboard.text()
        self.setText(clipboard_text)


class HistoryList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent

        clipboard_text = parent.clipboard.text()
        self.addItem(clipboard_text)

    def mouseDoubleClickEvent(self, event):
        current_item = self.currentItem()
        self._parent.clipbord_edit.setText(current_item.text())


class BookmarksList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        if os.path.exists(BOOKMARKS_FILE):
            with open(BOOKMARKS_FILE, 'r') as file:
                items = json.load(file)
            for i in items:
                self.addItem(i)

    def mouseDoubleClickEvent(self, event):
        current_item = self.currentItem()
        self._parent.clipboard.setText(current_item.text())

    def add_bookmark(self):
        text = self._parent.clipbord_edit.toPlainText()
        self.addItem(text)
        self.update_config_file()

    def remove_bookmark(self):
        current_index = self.currentRow()
        self.takeItem(current_index)
        self.update_config_file()

    def get_items(self):
        items = []
        for i in range(self.count()):
            item = self.item(i).text()
            items.append(item)
        return items

    def update_config_file(self):
        with open(BOOKMARKS_FILE, 'w') as file:
            json.dump(self.get_items(), file)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        filedir = os.path.dirname(__file__)
        iconpath = os.path.join(
            filedir, 'icons', 'accessories-text-editor.png')
        self.icon = QtGui.QIcon(iconpath)
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.dataChanged.connect(
            self.on_new_clipboard)
        self.clipbord_edit = ClipbordEdit(self)
        self.clipbord_history = HistoryList(self)
        self.clipbord_bookmarks = BookmarksList(self)

        # QWidget has to keep access to SystemTrayIcon
        # this is why it is set as object attribute
        self.systray = SystemTrayIcon(self)

        self.init_ui()

    def init_ui(self):
        copy_btn = QtWidgets.QPushButton(self)
        copy_btn.setText('Copy to clipbord')
        copy_btn.clicked.connect(
            self.copy_clicked)
        normpath_btn = QtWidgets.QPushButton(self)
        normpath_btn.setText('Normpath')
        normpath_btn.clicked.connect(
            self.normpath_clicked)
        to_slashes_btn = QtWidgets.QPushButton(self)
        to_slashes_btn.setText('/')
        to_slashes_btn.clicked.connect(
            self.backslashes_to_slashes_clicked)
        to_backslashes_btn = QtWidgets.QPushButton(self)
        to_backslashes_btn.setText('\\')
        to_backslashes_btn.clicked.connect(
            self.slashes_to_backslashes_clicked)
        execute_btn = QtWidgets.QPushButton(self)
        execute_btn.setText('Execute')
        execute_btn.clicked.connect(
            self.execute_clicked)
        open_btn = QtWidgets.QPushButton(self)
        open_btn.setText('Open')
        open_btn.clicked.connect(
            self.open_clicked)
        clear_history_btn = QtWidgets.QPushButton(self)
        clear_history_btn.setText('Clear history')
        clear_history_btn.clicked.connect(
            self.clipbord_history.clear)
        add_bookmark_btn = QtWidgets.QPushButton(self)
        add_bookmark_btn.setText('Add bookmark')
        add_bookmark_btn.clicked.connect(
            self.clipbord_bookmarks.add_bookmark)
        remove_bookmark_btn = QtWidgets.QPushButton(self)
        remove_bookmark_btn.setText('Remove bookmark')
        remove_bookmark_btn.clicked.connect(
            self.clipbord_bookmarks.remove_bookmark)

        wid_left = QtWidgets.QWidget()
        col = QtWidgets.QVBoxLayout()
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
        col.addWidget(clear_history_btn)
        col.addWidget(self.clipbord_bookmarks)
        col.addWidget(add_bookmark_btn)
        col.addWidget(remove_bookmark_btn)
        wid_right.setLayout(col)

        wid_main = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(wid_left)
        layout.addWidget(wid_right)
        wid_main.setLayout(layout)

        self.setLayout(layout)

        self.setWindowIcon(self.icon)
        self.resize(500, 350)
        self.setWindowTitle('Clipboard')

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def on_new_clipboard(self):
        text = self.clipboard.text()
        self.clipbord_edit.setText(text)
        self.clipbord_history.addItem(text)

    def copy_clicked(self):
        text = self.clipbord_edit.toPlainText()
        self.clipboard.setText(text)

    def normpath_clicked(self):
        text = self.clipbord_edit.toPlainText()
        text = os.path.normpath(text)
        self.clipboard.setText(text)

    def slashes_to_backslashes_clicked(self):
        text = self.clipbord_edit.toPlainText()
        text = text.replace('/', '\\')
        self.clipboard.setText(text)

    def backslashes_to_slashes_clicked(self):
        text = self.clipbord_edit.toPlainText()
        text = text.replace('\\', '/')
        self.clipboard.setText(text)

    def execute_clicked(self):
        text = self.clipbord_edit.toPlainText()
        subprocess.Popen(text)

    def open_clicked(self):
        text = self.clipbord_edit.toPlainText()
        text = os.path.normpath(text)
        if sys.platform.startswith('linux'):
            subprocess.Popen(['xdg-open', text])
        elif sys.platform.startswith('win'):
            if os.path.isdir(text):
                subprocess.Popen(['explorer', text])
            else:
                os.system(text)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
