# standard libraries
import os
import sys
import copy
import itertools
# third party libraries
from PyQt4 import QtGui, QtCore
from serial.tools.list_ports import comports as list_serial_ports
try:
    import _winreg as winreg
except ImportError:
    pass
try:
    import win32api
except ImportError:
    pass
# first party libraries
from . import qmatplotlib as matplotlib

_where = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_where, '..', 'VERSION'), 'rb') as f:
    __version__ = f.read()

class QConsoleLog(QtGui.QPlainTextEdit):

    def __init__(self, stdout=True, stderr=True, *args, **kwargs):
        super(QConsoleLog, self).__init__(*args, **kwargs)
        # only allow reads
        self.setReadOnly(True)
        # change default colors
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(0, 0, 0))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        self.setPalette(palette)
        # capture outputs, as appropriate
        if stdout:
            sys.stdout = self
        if stderr:
            sys.stderr = self

    def flush(self):
        pass

    def write(self, s):
        self.moveCursor(QtGui.QTextCursor.End)
        self.insertPlainText(s)

    def _get_text(self):
        return self.toPlainText()
    text = property(_get_text)

class QFormLayout(QtGui.QFormLayout):

    def __init__(self, *args, **kwargs):
        super(QFormLayout, self).__init__(*args, **kwargs)
        self.fieldLabel = {}

    def disableField(self, field):
        field.setDisabled(True)
        label = self.fieldLabel[field]
        label.setDisabled(True)

    def enableField(self, field):
        field.setEnabled(True)
        label = self.fieldLabel[field]
        label.setEnabled(True)

    def addRow(self, label, widget, stretch=True):
        layout = QtGui.QHBoxLayout()
        if issubclass(type(widget), QtGui.QLayout):
            layout.addLayout(widget)
        elif issubclass(type(widget), QtGui.QWidget):
            layout.addWidget(widget)
        else:
            raise ValueError()
        if stretch:
            layout.addStretch()
        super(QFormLayout, self).addRow(label, layout)
        self.fieldLabel[widget] = self.labelForField(layout)

class QViewComboBox(QtGui.QWidget):

    def __init__(self, view, add_selected=True, sleep=None, editable=False, *args, **kwargs):
        super(QViewComboBox, self).__init__(*args, **kwargs)
        self.ComboBox = QtGui.QComboBox()
        self.ComboBox.setEditable(editable)
        main_layout = QtGui.QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self._view = view
        self.add_selected = add_selected
        self._sleep = sleep

        if self._sleep is not None:
            assert type(self._sleep) == int
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_items)
            self.timer.start(1000*int(self._sleep))

        self.update_items()

        self.refreshButton = QtGui.QPushButton()
        fname = os.path.join(_where, 'reload.png')
        self.refreshButton.setIcon(QtGui.QIcon(fname))
        self.refreshButton.setFixedSize(24, 24)

        self.refreshButton.clicked.connect(self.update_items)

        self.setLayout(main_layout)
        main_layout.addWidget(self.ComboBox)
        main_layout.addWidget(self.refreshButton)

    def update_items(self):
        self.ComboBox.blockSignals(True)
        current_item_selected = copy.deepcopy(self.selected_item)
        new_items = self._view()
        self.ComboBox.clear()
        self.ComboBox.addItems(list(new_items))
        current_item_reselected = False
        for indx in range(self.ComboBox.count()):
            if self.ComboBox.itemText(indx) == current_item_selected:
                self.ComboBox.setCurrentIndex(indx)
                current_item_reselected = True
                break
        self.ComboBox.blockSignals(False)
        if not current_item_reselected:
            indx = 0
        self.ComboBox.currentIndexChanged.emit(indx)

    def currentIndex(self):
        indx = self.ComboBox.currentIndex()
        return int(indx)

    def itemText(self, indx):
        item = self.ComboBox.itemText(indx)
        return str(item)

    def _get_selected_item(self):
        indx = self.currentIndex()
        item = self.itemText(indx)
        return str(item)
    selected_item = property(_get_selected_item)


class QSerialPortSelector(QViewComboBox):

    def __init__(self, *args, **kwargs):
        super(QSerialPortSelector, self).__init__(self.available_serial_ports, *args, **kwargs)

    def available_serial_ports(self):
        ports = []
        if sys.platform.startswith('win'):
            path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            except:
                return []
            for i in itertools.count():
                try:
                    port = str(winreg.EnumValue(key, i)[1])
                    ports.append(port)
                except EnvironmentError:
                    break
        else:
          for port, _, _ in list_serial_ports():
            ports.append(port)
        return ports

class QPeripheralDriveSelector(QViewComboBox):

    def __init__(self, *args, **kwargs):
        super(QPeripheralDriveSelector, self).__init__(self.available_peripheral_drives, *args, **kwargs)

    def available_peripheral_drives(self):
        """ NB: this is only set up for Windows machines currently.
        """
        try:
            drives = win32api.GetLogicalDriveStrings()
            drives = [drive for drive in drives.split('\000') if drive and drive != 'C:\\']
            return drives
        except:
            return []