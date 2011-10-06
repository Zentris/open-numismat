from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

from .BaseFormLayout import BaseFormLayout, FormItem
from Collection.CollectionFields import CollectionFields
from Collection.CollectionFields import FieldTypes as Type
from .AuctionParser import getParser

class EditCoinDialog(QtGui.QDialog):
    def __init__(self, reference, record, parent=None, usedFields=None):
        super(EditCoinDialog, self).__init__(parent)
        
        self.usedFields = usedFields
        self.reference = reference
        self.record = record
        
        self.tab = QtGui.QTabWidget(self)
        
        self.createItems()

        # Create Coin page
        main = self.mainDetailsLayout()
        groupBox1 = self.__layoutToGroupBox(main, self.tr("Main details"))
        groupBox1.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        
        state = self.stateLayout()
        groupBox2 = self.__layoutToGroupBox(state, self.tr("State"))
        
        self.addTabPage(self.tr("Coin"), [groupBox1, groupBox2])

        # Create Traffic page
        self.oldTrafficIndex = 0
        parts = self.__createTrafficParts(self.oldTrafficIndex)
        self.addTabPage(self.tr("Traffic"), parts)

        # Create Parameters page
        parameters = self.parametersLayout()
        groupBox1 = self.__layoutToGroupBox(parameters, self.tr("Parameters"))
        groupBox1.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)

        minting = self.mintingLayout()
        groupBox2 = self.__layoutToGroupBox(minting, self.tr("Minting"))
        groupBox2.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)

        self.addTabPage(self.tr("Parameters"), [groupBox1, groupBox2])

        # Create Design page
        obverse = self.obverseDesignLayout()
        groupBox1 = self.__layoutToGroupBox(obverse, self.tr("Obverse"))
        
        reverse = self.reverseDesignLayout()
        groupBox2 = self.__layoutToGroupBox(reverse, self.tr("Reverse"))

        edge = self.edgeDesignLayout()
        groupBox3 = self.__layoutToGroupBox(edge, self.tr("Edge"))

        subject = self.subjectLayout()

        self.addTabPage(self.tr("Design"), [groupBox1, groupBox2, groupBox3, subject])

        # Create Classification page
        classification = self.classificationLayout()

        price = self.priceLayout()
        groupBox1 = self.__layoutToGroupBox(price, self.tr("Price"))
        groupBox1.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)

        variation = self.variationLayout()
        groupBox2 = self.__layoutToGroupBox(variation, self.tr("Variation"))

        self.addTabPage(self.tr("Classification"), [classification, groupBox1, groupBox2])

        # Create Images page
        images = self.imagesLayout()
        self.addTabPage(self.tr("Images"), images)

        self.fillItems(record)

        buttonBox = QtGui.QDialogButtonBox(Qt.Horizontal);
        buttonBox.addButton(QtGui.QDialogButtonBox.Save);
        buttonBox.addButton(QtGui.QDialogButtonBox.Cancel);
        buttonBox.accepted.connect(self.save);
        buttonBox.rejected.connect(self.reject);

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.tab)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

        settings = QtCore.QSettings()
        size = settings.value('editcoinwindow/size')
        if size:
            self.resize(size)
    
    def keyPressEvent(self, event):
        if self.items['state'].widget().data() == 'pass':
            if event.matches(QtGui.QKeySequence.Paste):
                mime = QtGui.QApplication.clipboard().mimeData()
                if mime.hasText():
                    parser = getParser(mime.text(), self)
                    lot = parser.parse()
                    if lot:
                        for key in ['payprice', 'obverseimg', 'reverseimg', 'edgeimg',
                                    'photo1', 'photo2', 'photo3', 'photo4']:
                            self.items[key].clear()
                        self.items['saleplace'].setValue(lot.place)
                        self.items['saleprice'].setValue(lot.price)
                        self.items['totalpayprice'].setValue(lot.totalPayPrice)
                        self.items['totalsaleprice'].setValue(lot.totalSalePrice)
                        self.items['saller'].setValue(lot.saller)
                        self.items['buyer'].setValue(lot.buyer)
                        self.items['saleinfo'].setValue(lot.info)
                        self.items['saledate'].setValue(lot.date)
                        self.items['grade'].setValue(lot.grade)
                        
                        # Add images
                        imageFields = ['reverseimg', 'obverseimg',
                                    'photo1', 'photo2', 'photo3', 'photo4']
                        for i, imageUrl in enumerate(lot.images):
                            if i < len(imageFields):
                                self.items[imageFields[i]].widget().loadFromUrl(imageUrl)
                            else:
                                QtGui.QMessageBox.information(self.parent(), self.tr("Parse auction lot"),
                                            self.tr("Too many images"),
                                            QtGui.QMessageBox.Ok)
                                break
    
    def __layoutToWidget(self, layout):
        widget = QtGui.QWidget(self.tab)
        widget.setLayout(layout)
        return widget
    
    def __layoutToGroupBox(self, layout, title):
        groupBox = QtGui.QGroupBox(title)
        groupBox.setLayout(layout)
        return groupBox
    
    def addTabPage(self, title, parts):
        if isinstance(parts, list):
            pageLayout = QtGui.QVBoxLayout(self)
            # Fill layout with it's parts
            for part in parts:
                if isinstance(part, QtGui.QWidget):
                    pageLayout.addWidget(part)
                else:
                    pageLayout.addLayout(part)

            # Convert layout to widget and add to tab page
            self.tab.addTab(self.__layoutToWidget(pageLayout), title)
            if len(parts) == 0:
                self.tab.setTabEnabled(1, False)
        else:
            # Convert layout to widget and add to tab page
            self.tab.addTab(self.__layoutToWidget(parts), title)

    def save(self):
        # Clear unused fields
        if self.items['state'].widget().data() == 'demo':
            for key in ['paydate', 'payprice', 'totalpayprice', 'saller',
                        'payplace', 'payinfo', 'saledate', 'saleprice',
                        'totalsaleprice', 'buyer', 'saleplace', 'saleinfo', 'grade']:
                self.items[key].clear()
        elif self.items['state'].widget().data() in ['in', 'exchange']:
            for key in ['paydate', 'payprice', 'totalpayprice', 'saller',
                        'payplace', 'payinfo']:
                self.items[key].clear()
        
        if not self.usedFields:
            if not self.items['title'].value():
                result = QtGui.QMessageBox.warning(self.parent(), self.tr("Save"),
                                 self.tr("Coin title not set. Save without title?"),
                                 QtGui.QMessageBox.Save | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                if result != QtGui.QMessageBox.Save:
                    return
            # TODO: Add checking that TotalPrice not less than Price

        for item in self.items.values():
            value = item.value()
            if isinstance(value, str):
                value = value.strip()
            self.record.setValue(item.field(), value)
    
        self.accept()
    
    def getUsedFields(self):
        for item in self.items.values():
            self.usedFields[self.record.indexOf(item.field())] = item.label().checkState()
        return self.usedFields

    def getRecord(self):
        return self.record
    
    def done(self, r):
        settings = QtCore.QSettings()
        settings.setValue('editcoinwindow/size', self.size());
        super(EditCoinDialog, self).done(r)
    
    def addItem(self, field):
        checkable = 0
        if self.usedFields:
            checkable = Type.Checkable
        reference = self.reference.section(field.name)

        item = FormItem(field.name, field.title, field.type | checkable, reference)
        self.items[field.name] = item
    
    def createItems(self):
        self.items = {}
        
        fields = CollectionFields()
        skippedFields = [fields.id,]
        for field in fields:
            if field in skippedFields:
                continue
            self.addItem(field)
        
        self.items['country'].widget().addDependent(self.items['period'].widget())
        self.items['country'].widget().addDependent(self.items['unit'].widget())
        self.items['country'].widget().addDependent(self.items['mint'].widget())
        self.items['country'].widget().addDependent(self.items['series'].widget())
    
    def fillItems(self, record):
        if not record.isEmpty():
            fields = CollectionFields()
            skippedFields = [fields.id,]
            for field in fields:
                if field in skippedFields:
                    continue
                item = self.items[field.name]
                if not record.isNull(item.field()):
                    value = record.value(item.field())
                    item.setValue(value)

            if self.usedFields:
                for item in self.items.values():
                    if self.usedFields[record.indexOf(item.field())]:
                        item.label().setCheckState(Qt.Checked)
            
        self.indexChangedState(self.oldTrafficIndex)

    def mainDetailsLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        layout.columnCount = 6
       
        btn = QtGui.QPushButton(self.tr("Generate"), parent)
        btn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        btn.clicked.connect(self.clickGenerateTitle)
        self.items['title'].widget().textChanged.connect(self.textChangedTitle)
        layout.addRow(self.items['title'], btn)

        layout.addRow(self.items['country'])
        layout.addRow(self.items['period'])
        layout.addRow(self.items['value'], self.items['unit'])
        layout.addRow(self.items['year'])
        layout.addRow(self.items['mintmark'], self.items['mint'])
        layout.addRow(self.items['type'])
        layout.addRow(self.items['series'])

        return layout

    def stateLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        self.items['state'].widget().currentIndexChanged.connect(self.indexChangedState)
        layout.addRow(self.items['state'], self.items['grade'])
        layout.addRow(self.items['note'])

        return layout

    def payLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        layout.addRow(self.items['paydate'], self.items['payprice'])

        # Add auxiliary field
        item = self.addPayCommission()

        layout.addRow(self.items['totalpayprice'], item)
        layout.addRow(self.items['saller'])
        layout.addRow(self.items['payplace'])
        layout.addRow(self.items['payinfo'])

        return layout

    def saleLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        layout.addRow(self.items['saledate'], self.items['saleprice'])

        # Add auxiliary field
        item = self.addSaleCommission()
        layout.addRow(self.items['totalsaleprice'], item)

        layout.addRow(self.items['buyer'])
        layout.addRow(self.items['saleplace'])
        layout.addRow(self.items['saleinfo'])

        return layout

    def passLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        layout.addRow(self.items['saledate'], self.items['saleprice'])

        # Add auxiliary field
        item = self.addPayCommission()
        layout.addRow(self.items['totalpayprice'], item)
        self.items['saleprice'].widget().textChanged.connect(self.items['payprice'].widget().setText)

        # Add auxiliary field
        item = self.addSaleCommission()
        layout.addRow(self.items['totalsaleprice'], item)

        layout.addRow(self.items['saller'])
        layout.addRow(self.items['buyer'])
        layout.addRow(self.items['saleplace'])
        layout.addRow(self.items['saleinfo'])

        return layout

    def parametersLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        layout.addRow(self.items['metal'])
        layout.addRow(self.items['fineness'], self.items['mass'])
        layout.addRow(self.items['diameter'], self.items['thick'])
        layout.addRow(self.items['form'])
        layout.addRow(self.items['obvrev'])

        return layout

    def mintingLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        layout.addRow(self.items['issuedate'], self.items['mintage'])
        layout.addRow(self.items['dateemis'])

        return layout

    def obverseDesignLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        layout.columnCount = 2
        
        item = self.items['obverseimg']
        layout.setColumnMinimumWidth(2, 160)
        layout.addWidget(item.widget(), 0, 2, 2, 1)
        
        layout.addRow(self.items['obversedesign'])
        layout.addRow(self.items['obversedesigner'])

        return layout

    def reverseDesignLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        layout.columnCount = 2
        
        item = self.items['reverseimg']
        layout.setColumnMinimumWidth(2, 160)
        layout.addWidget(item.widget(), 0, 2, 2, 1)
        
        layout.addRow(self.items['reversedesign'])
        layout.addRow(self.items['reversedesigner'])

        return layout

    def edgeDesignLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        layout.columnCount = 2
        
        item = self.items['edgeimg']
        layout.setColumnMinimumWidth(2, 160)
        layout.addWidget(item.widget(), 0, 2, 2, 1)
        
        layout.addRow(self.items['edge'])
        layout.addRow(self.items['edgelabel'])

        return layout

    def subjectLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        layout.columnCount = 2
        
        layout.addRow(self.items['subject'])

        return layout

    def classificationLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        layout.addRow(self.items['catalognum1'])
        layout.addRow(self.items['catalognum2'])
        layout.addRow(self.items['catalognum3'])
        layout.addRow(self.items['rarity'])

        return layout

    def priceLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        layout.addRow(self.items['price1'], self.items['price2'])
        layout.addRow(self.items['price3'], self.items['price4'])
        layout.addRow(self.items['price5'], self.items['price6'])

        return layout

    def variationLayout(self, parent=None):
        layout = BaseFormLayout(parent)
        
        layout.addRow(self.items['obversevar'])
        layout.addRow(self.items['reversevar'])
        layout.addRow(self.items['edgevar'])

        return layout

    def imagesLayout(self, parent=None):
        layout = BaseFormLayout(parent)

        item = self.items['photo1']
        item.label().setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
#        item.label().setAlignment(Qt.AlignLeft)
        layout.addWidget(item.label(), 0, 0)
        layout.addWidget(item.widget(), 1, 0)
        item = self.items['photo2']
        item.label().setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
#        item.label().setAlignment(Qt.AlignLeft)
        layout.addWidget(item.label(),0,1)
        layout.addWidget(item.widget(),1,1)
        item = self.items['photo3']
        item.label().setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
#        item.label().setAlignment(Qt.AlignLeft)
        layout.addWidget(item.label(),2,0)
        layout.addWidget(item.widget(),3,0)
        item = self.items['photo4']
        item.label().setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
#        item.label().setAlignment(Qt.AlignLeft)
        layout.addWidget(item.label(),2,1)
        layout.addWidget(item.widget(),3,1)

        layout.setRowMinimumHeight(1, 120)
        layout.setRowMinimumHeight(3, 120)
        layout.setColumnMinimumWidth(0, 160)
        layout.setColumnMinimumWidth(1, 160)

        return layout

    def clickGenerateTitle(self):
        titleParts = []
        for key in ['value', 'unit', 'year', 'mintmark']:
            value = str(self.items[key].value())
            if value:
                titleParts.append(value) 

        title = ' '.join(titleParts)
        self.items['title'].setValue(title)

    def textChangedTitle(self, text):
        if self.usedFields:
            self.setWindowTitle(self.tr("Multi edit"))
        else:
            title = [self.tr("Edit"),]
            if text:
                title.insert(0, text)
            self.setWindowTitle(' - '.join(title))
    
    def __createTrafficParts(self, index=0):
        if self.oldTrafficIndex == 0:
            pass
        elif self.oldTrafficIndex == 1:
            self.items['payprice'].widget().textChanged.disconnect(self.payCommissionChanged)
            self.items['totalpayprice'].widget().textChanged.disconnect(self.payTotalPriceChanged)
            self.payCommission.textChanged.disconnect(self.payCommissionChanged)
            self.items['saleprice'].widget().textChanged.disconnect(self.saleCommissionChanged)
            self.items['totalsaleprice'].widget().textChanged.disconnect(self.saleTotalPriceChanged)
            self.saleCommission.textChanged.disconnect(self.saleCommissionChanged)
            self.items['saleprice'].widget().textChanged.disconnect(self.items['payprice'].widget().setText)
        elif self.oldTrafficIndex == 2:
            self.items['payprice'].widget().textChanged.disconnect(self.payCommissionChanged)
            self.items['totalpayprice'].widget().textChanged.disconnect(self.payTotalPriceChanged)
            self.payCommission.textChanged.disconnect(self.payCommissionChanged)
        elif self.oldTrafficIndex == 3:
            self.items['payprice'].widget().textChanged.disconnect(self.payCommissionChanged)
            self.items['totalpayprice'].widget().textChanged.disconnect(self.payTotalPriceChanged)
            self.payCommission.textChanged.disconnect(self.payCommissionChanged)
            self.items['saleprice'].widget().textChanged.disconnect(self.saleCommissionChanged)
            self.items['totalsaleprice'].widget().textChanged.disconnect(self.saleTotalPriceChanged)
            self.saleCommission.textChanged.disconnect(self.saleCommissionChanged)
        elif self.oldTrafficIndex == 4:
            self.items['payprice'].widget().textChanged.disconnect(self.payCommissionChanged)
            self.items['totalpayprice'].widget().textChanged.disconnect(self.payTotalPriceChanged)
            self.payCommission.textChanged.disconnect(self.payCommissionChanged)

        pageParts = []
        if index == 0:
            pass
        elif index == 1:
            pass_ = self.passLayout()
            groupBox = self.__layoutToGroupBox(pass_, self.tr("Pass"))
            pageParts.append(groupBox)
        elif index == 2:
            pay = self.payLayout()
            groupBox = self.__layoutToGroupBox(pay, self.tr("Buy"))
            pageParts.append(groupBox)
        elif index == 3:
            pay = self.payLayout()
            groupBox1 = self.__layoutToGroupBox(pay, self.tr("Buy"))
            pageParts.append(groupBox1)
            
            sale = self.saleLayout()
            groupBox2 = self.__layoutToGroupBox(sale, self.tr("Sale"))
            pageParts.append(groupBox2)
        elif index == 4:
            pay = self.payLayout()
            groupBox = self.__layoutToGroupBox(pay, self.tr("Buy"))
            pageParts.append(groupBox)
        
        self.oldTrafficIndex = index
        
        return pageParts

    def indexChangedState(self, index):
        self.tab.removeTab(1)
        pageParts = self.__createTrafficParts(index)

        pageLayout = QtGui.QVBoxLayout()
        # Fill layout with it's parts
        for part in pageParts:
            pageLayout.addWidget(part)

        # Convert layout to widget and add to tab page
        self.tab.insertTab(1, self.__layoutToWidget(pageLayout), self.tr("Traffic"))
        if len(pageParts) == 0:
            self.tab.setTabEnabled(1, False)
            self.items['grade'].widget().setEnabled(False)
        else:
            self.items['grade'].widget().setEnabled(True)
    
    def addPayCommission(self):
        item = FormItem(None, self.tr("Commission"), Type.Money)
        self.payCommission = item.widget()
        validator = CommissionValidator(0, 9999999999, 2, self)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.payCommission.setValidator(validator)
        
        price = textToFloat(self.items['payprice'].value())
        totalPrice = textToFloat(self.items['totalpayprice'].value())
        self.payCommission.setText(floatToText(totalPrice - price))

        self.items['payprice'].widget().textChanged.connect(self.payCommissionChanged)
        self.payCommission.textChanged.connect(self.payCommissionChanged)
        self.items['totalpayprice'].widget().textChanged.connect(self.payTotalPriceChanged)
        
        return item
    
    def addSaleCommission(self):
        item = FormItem('', self.tr("Commission"), Type.Money)
        self.saleCommission = item.widget()
        validator = CommissionValidator(0, 9999999999, 2, self)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.saleCommission.setValidator(validator)
        
        price = textToFloat(self.items['saleprice'].value())
        totalPrice = textToFloat(self.items['totalsaleprice'].value())
        self.saleCommission.setText(floatToText(price - totalPrice))

        self.items['saleprice'].widget().textChanged.connect(self.saleCommissionChanged)
        self.saleCommission.textChanged.connect(self.saleCommissionChanged)
        self.items['totalsaleprice'].widget().textChanged.connect(self.saleTotalPriceChanged)
        
        return item
    
    def payCommissionChanged(self, text):
        self.items['totalpayprice'].widget().textChanged.disconnect(self.payTotalPriceChanged)
        
        price = textToFloat(self.items['payprice'].value())
        text = self.payCommission.text().strip()
        if len(text) > 0 and text[-1] == '%':
            commission = price * textToFloat(text[0:-1]) / 100
        else:
            commission = textToFloat(text)
        self.items['totalpayprice'].widget().setText(floatToText(price + commission))

        self.items['totalpayprice'].widget().textChanged.connect(self.payTotalPriceChanged)

    def payTotalPriceChanged(self, text):
        self.payCommission.textChanged.disconnect(self.payCommissionChanged)

        price = textToFloat(self.items['payprice'].value())
        totalPrice = textToFloat(self.items['totalpayprice'].value())
        self.payCommission.setText(floatToText(totalPrice - price))

        self.payCommission.textChanged.connect(self.payCommissionChanged)
    
    def saleCommissionChanged(self, text):
        self.items['totalsaleprice'].widget().textChanged.disconnect(self.saleTotalPriceChanged)
        
        price = textToFloat(self.items['saleprice'].value())
        text = self.saleCommission.text().strip()
        if len(text) > 0 and text[-1] == '%':
            commission = price * textToFloat(text[0:-1]) / 100
        else:
            commission = textToFloat(text)
        self.items['totalsaleprice'].widget().setText(floatToText(price - commission))

        self.items['totalsaleprice'].widget().textChanged.connect(self.saleTotalPriceChanged)

    def saleTotalPriceChanged(self, text):
        self.saleCommission.textChanged.disconnect(self.saleCommissionChanged)

        price = textToFloat(self.items['saleprice'].value())
        totalPrice = textToFloat(self.items['totalsaleprice'].value())
        self.saleCommission.setText(floatToText(price - totalPrice))

        self.saleCommission.textChanged.connect(self.saleCommissionChanged)
    
def textToFloat(text):
    return float(text.replace(' ', '') or 0)

def floatToText(value):
    return str(int((value)*100 + 0.5)/100)

# Reimplementing QDoubleValidator for replace comma with dot and accept %
class CommissionValidator(QtGui.QDoubleValidator):
    def __init__(self, bottom, top, decimals, parent=None):
        super(CommissionValidator, self).__init__(bottom, top, decimals, parent)
    
    def validate(self, input, pos):
        numericValue = input.strip()
        if len(numericValue) > 0 and numericValue[-1] == '%':
            numericValue = numericValue[0:-1]
        numericValue = numericValue.replace(',', '.')
        state, numericValue, pos = super(CommissionValidator, self).validate(numericValue, pos)
        return state, input, pos
