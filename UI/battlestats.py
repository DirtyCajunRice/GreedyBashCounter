# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'battlestats.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(311, 261)
        self.battlestatsTable = QtWidgets.QTableWidget(Form)
        self.battlestatsTable.setGeometry(QtCore.QRect(0, 0, 311, 261))
        self.battlestatsTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.battlestatsTable.setAlternatingRowColors(True)
        self.battlestatsTable.setColumnCount(3)
        self.battlestatsTable.setObjectName("battlestatsTable")
        self.battlestatsTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.battlestatsTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.battlestatsTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.battlestatsTable.setHorizontalHeaderItem(2, item)
        self.battlestatsTable.horizontalHeader().setCascadingSectionResizes(True)
        self.battlestatsTable.horizontalHeader().setStretchLastSection(True)
        self.battlestatsTable.verticalHeader().setCascadingSectionResizes(True)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Battle Stats"))
        self.battlestatsTable.setSortingEnabled(True)
        item = self.battlestatsTable.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Battle"))
        item = self.battlestatsTable.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Ship"))
        item = self.battlestatsTable.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Greedies"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

