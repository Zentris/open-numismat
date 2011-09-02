from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from ImageLabel import ImageLabel

class FormItem(object):
    def __init__(self, field, title, parent=None):
        self._field = field
        self._title = title
        self._widget = None
        self._label = QtGui.QLabel(title, parent)
        self._label.setAlignment(Qt.AlignRight)
    
    def field(self):
        return self._field

    def title(self):
        return self._title

    def label(self):
        return self._label

    def widget(self):
        return self._widget
    
    def setWidget(self, widget):
        self._widget = widget
        
    def value(self):
        if isinstance(self._widget, QtGui.QTextEdit):
            return self._widget.toPlainText()
        elif isinstance(self._widget, QtGui.QAbstractSpinBox):
            return self._widget.value()
        elif isinstance(self._widget, ImageLabel):
            return self._widget.data()
        else:
            return self._widget.text()

    def setValue(self, value):
        type(self._widget)
        if isinstance(self._widget, ImageLabel):
            self._widget.loadFromData(value)
        elif isinstance(self._widget, QtGui.QSpinBox):
            self._widget.setValue(int(value))
        elif isinstance(self._widget, QtGui.QDoubleSpinBox):
            self._widget.setValue(float(value))
        else: 
            self._widget.setText(str(value))

class LineEdit(QtGui.QLineEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        self.setMaxLength(1024)

class ShortLineEdit(QtGui.QLineEdit):
    def __init__(self, parent=None):
        super(ShortLineEdit, self).__init__(parent)
        self.setMaxLength(50)
        self.setMinimumWidth(100)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    
    def sizeHint(self):
        return self.minimumSizeHint()

class NumberEdit(QtGui.QSpinBox):
    def __init__(self, parent=None):
        super(NumberEdit, self).__init__(parent)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.setMinimum(0)
        self.setMaximum(9999)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setMinimumWidth(50)

class ValueEdit(QtGui.QLineEdit):
    def __init__(self, parent=None):
        super(ValueEdit, self).__init__(parent)
        validator = QtGui.QDoubleValidator(0, 9999999999, 2, parent)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.setValidator(validator)
        self.setMaxLength(50)
        self.setMinimumWidth(100)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    
    def sizeHint(self):
        return self.minimumSizeHint()

class TextEdit(QtGui.QTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)

    def sizeHint(self):
        return self.minimumSizeHint()

class BaseFormLayout(QtGui.QGridLayout):
    def __init__(self, record, parent=None):
        super(BaseFormLayout, self).__init__(parent)
        self.row = 0
        self.columnCount = 4

    def addRow(self, item1, item2=None):
        if not item2:
            self.addWidget(item1.label(), self.row, 0)
            # NOTE: columnSpan parameter in addWidget don't work with value -1
            # self.addWidget(item1.widget(), self.row, 1, 1, -1)
            if self.columnCount == 4:
                self.addWidget(item1.widget(), self.row, 1, 1, 3)
            else:
                self.addWidget(item1.widget(), self.row, 1)
        else:
            self.addWidget(item1.label(), self.row, 0)
            self.addWidget(item1.widget(), self.row, 1)
    
            self.addWidget(item2.label(), self.row, 2)
            self.addWidget(item2.widget(), self.row, 3)

        self.row = self.row + 1

if __name__ == '__main__':
    from main import run
    run()