# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(552, 332)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        Dialog.setFont(font)
        Dialog.setStyleSheet("background-color: rgb(180, 246, 216)")
        self.auth_as = QtWidgets.QLabel(Dialog)
        self.auth_as.setGeometry(QtCore.QRect(10, 10, 531, 31))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.auth_as.setFont(font)
        self.auth_as.setStyleSheet("color: rgb(0, 0, 0);\n"
"font-size: 20px;\n"
"font: \"Arial Black\";")
        self.auth_as.setText("")
        self.auth_as.setAlignment(QtCore.Qt.AlignCenter)
        self.auth_as.setObjectName("auth_as")
        self.Delete_btn = QtWidgets.QPushButton(Dialog)
        self.Delete_btn.setGeometry(QtCore.QRect(430, 270, 90, 40))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.Delete_btn.setFont(font)
        self.Delete_btn.setStyleSheet("font-size: 16px;\n"
"font: \"Yu Gothic UI Semibold\";\n"
"background-color: rgb(245, 245, 245)")
        self.Delete_btn.setObjectName("Delete_btn")
        self.Add_btn = QtWidgets.QPushButton(Dialog)
        self.Add_btn.setGeometry(QtCore.QRect(430, 110, 90, 40))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.Add_btn.setFont(font)
        self.Add_btn.setStyleSheet("font-size: 16px;\n"
"font: \"Yu Gothic UI Semibold\";\n"
"background-color: rgb(245, 245, 245)")
        self.Add_btn.setObjectName("Add_btn")
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(10, 90, 381, 231))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.tableWidget.setFont(font)
        self.tableWidget.setStyleSheet("font-size: 16px;\n"
"font: \"Yu Gothic UI Semibold\";\n"
"background-color: rgb(245, 245, 245)")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 50, 531, 31))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("color: rgb(0, 0, 0);\n"
"font-size: 20px;\n"
"font: \"Arial Black\";")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.Update_btn = QtWidgets.QPushButton(Dialog)
        self.Update_btn.setGeometry(QtCore.QRect(430, 190, 90, 40))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(-1)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.Update_btn.setFont(font)
        self.Update_btn.setStyleSheet("font-size: 16px;\n"
"font: \"Yu Gothic UI Semibold\";\n"
"background-color: rgb(245, 245, 245)")
        self.Update_btn.setObjectName("Update_btn")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.Delete_btn.setText(_translate("Dialog", "Удалить"))
        self.Add_btn.setText(_translate("Dialog", "Добавить"))
        self.label_4.setText(_translate("Dialog", "Вернуть кредит"))
        self.Update_btn.setText(_translate("Dialog", "Обновить"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())