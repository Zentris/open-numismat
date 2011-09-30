from PyQt4 import QtGui, QtCore
from PyQt4.QtSql import QSqlDatabase, QSqlQuery, QSqlRecord
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4 import QtSql

class ReferenceDialog(QtGui.QDialog):
    def __init__(self, model, parent=None):
        super(ReferenceDialog, self).__init__(parent)
        
        self.model = model

        self.listWidget = QtGui.QListView(self)
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.listWidget.setModel(self.model)
        self.listWidget.setModelColumn(1)

        # TODO: Customize edit buttons
        editButtonBox = QtGui.QDialogButtonBox(Qt.Horizontal)
        self.addButton = QtGui.QPushButton(self.tr("Add"))
        editButtonBox.addButton(self.addButton, QtGui.QDialogButtonBox.ActionRole)
        self.delButton = QtGui.QPushButton(self.tr("Del"))
        editButtonBox.addButton(self.delButton, QtGui.QDialogButtonBox.ActionRole)
        editButtonBox.clicked.connect(self.clicked)

        buttonBox = QtGui.QDialogButtonBox(Qt.Horizontal)
        buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.accepted.connect(self.model.submitAll)
        buttonBox.rejected.connect(self.reject)
        buttonBox.rejected.connect(self.model.revertAll)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.listWidget)
        layout.addWidget(editButtonBox)
        layout.addWidget(buttonBox)

        self.setLayout(layout)
    
    def clicked(self, button):
        index = self.listWidget.currentIndex()
        if button == self.addButton:
            row = self.model.rowCount()
            self.model.insertRow(row)
            index = self.model.index(row, 1)
            self.model.setData(index, self.tr("Enter value"))
            self.listWidget.edit(index)
        elif button == self.delButton:
            if index.isValid() and index in self.listWidget.selectedIndexes():
                self.model.removeRow(index.row())
                self.listWidget.setRowHidden(index.row(), True)

class ReferenceSection(QtCore.QObject):
    changed = pyqtSignal(object)

    def __init__(self, name, letter='', parent=None):
        super(ReferenceSection, self).__init__(parent)

        if isinstance(name, QSqlRecord):
            record = name
            self.id = record.value('id')
            self.name = record.value('name')
            self.letter = record.value('letter')
        else:
            self.name = name
            self.letter = letter
        self.parentName = None
    
    def load(self, db):
        sql = "CREATE TABLE IF NOT EXISTS %s (\
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\
            value CHAR)" % self.name
        QSqlQuery(sql, db)

        self.model = QtSql.QSqlRelationalTableModel(None, db)
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model.setTable(self.name)
        self.model.select()
    
    def button(self, parent=None):
        self.parent = parent
        button = QtGui.QPushButton(self.letter, parent)
        button.setFixedWidth(25)
        button.clicked.connect(self.clickedButton)
        return button
    
    def clickedButton(self):
        dialog = ReferenceDialog(self.model, self.parent)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            index = dialog.listWidget.currentIndex()
            if index in dialog.listWidget.selectedIndexes():
                self.changed.emit(index.data())

class Reference(QtCore.QObject):
    def __init__(self, parent=None):
        super(Reference, self).__init__(parent)

        self.db = QSqlDatabase.addDatabase('QSQLITE', "reference")
    
    def create(self):
        sql = "CREATE TABLE IF NOT EXISTS sections (\
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\
            name CHAR,\
            icon BLOB,\
            letter CHAR(1),\
            parent CHAR)"
        QSqlQuery(sql, self.db)

        sections = [
                ReferenceSection('country', self.tr("C")),
                ReferenceSection('type', self.tr("T")),
                ReferenceSection('grade', self.tr("G")),
                ReferenceSection('place'),
                ReferenceSection('metal', self.tr("M")),
                ReferenceSection('form', self.tr("F")),
                ReferenceSection('obvrev'),
                ReferenceSection('edge', self.tr("E"))
            ]
        for section in sections:
            query = QSqlQuery(self.db)
            query.prepare("INSERT INTO sections (name, letter) "
                          "VALUES (?, ?)")
            query.addBindValue(section.name)
            query.addBindValue(section.letter)
            query.exec_()
    
    def open(self, fileName):
        file = QtCore.QFileInfo(fileName)
        if file.isFile():
            self.db.setDatabaseName(fileName)
            if not self.db.open():
                print(self.db.lastError().text())
                QtGui.QMessageBox.critical(self.parent(), self.tr("Open reference"), self.tr("Can't open reference"))
                return False
        else:
            QtGui.QMessageBox.critical(self.parent(), self.tr("Open reference"), self.tr("Can't open reference"))
            self.db.setDatabaseName(fileName)
            self.db.open()
            self.create()
            return False
        
        self.fileName = fileName
        
        return True
    
    def section(self, name):
        section = None
        
        if name in ['payplace', 'saleplace']:
            name = 'place'
        
        query = QSqlQuery(self.db)
        query.prepare("SELECT * FROM sections WHERE name=?")
        query.addBindValue(name)
        query.exec_()
        
        if query.first():
            section = ReferenceSection(query.record())
            section.load(self.db)
        
        return section