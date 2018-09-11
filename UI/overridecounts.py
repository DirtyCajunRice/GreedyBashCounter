# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'overridecounts.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(161, 91)
        Form.setStyleSheet("background-color: qlineargradient(spread:reflect, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(0, 0, 63, 255), stop:1 rgba(0, 88, 73, 255))")
        self.lavishlockeroverrideSpinBox = QtWidgets.QSpinBox(Form)
        self.lavishlockeroverrideSpinBox.setGeometry(QtCore.QRect(10, 10, 61, 31))
        self.lavishlockeroverrideSpinBox.setStyleSheet("color: rgb(255, 255, 255)")
        self.lavishlockeroverrideSpinBox.setDisplayIntegerBase(10)
        self.lavishlockeroverrideSpinBox.setObjectName("lavishlockeroverrideSpinBox")
        self.battleoverrideSpinBox = QtWidgets.QSpinBox(Form)
        self.battleoverrideSpinBox.setGeometry(QtCore.QRect(80, 10, 71, 31))
        self.battleoverrideSpinBox.setStyleSheet("color: rgb(255, 255, 255)")
        self.battleoverrideSpinBox.setMaximum(99)
        self.battleoverrideSpinBox.setDisplayIntegerBase(10)
        self.battleoverrideSpinBox.setObjectName("battleoverrideSpinBox")
        self.overridefixButton = QtWidgets.QPushButton(Form)
        self.overridefixButton.setGeometry(QtCore.QRect(10, 50, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans")
        font.setPointSize(12)
        font.setItalic(True)
        self.overridefixButton.setFont(font)
        self.overridefixButton.setStyleSheet("border-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")
        self.overridefixButton.setDefault(False)
        self.overridefixButton.setFlat(False)
        self.overridefixButton.setObjectName("overridefixButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Override"))
        self.lavishlockeroverrideSpinBox.setSuffix(_translate("Form", " LLs"))
        self.battleoverrideSpinBox.setSuffix(_translate("Form", " Battles"))
        self.overridefixButton.setText(_translate("Form", "Fix"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

