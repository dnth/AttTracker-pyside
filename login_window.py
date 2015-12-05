# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created: Sat Dec  5 23:17:35 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(484, 190)
        Dialog.setModal(True)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 20, 311, 161))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit_username = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.gridLayout.addWidget(self.lineEdit_username, 1, 1, 1, 1)
        self.lineEdit_password = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_password.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.gridLayout.addWidget(self.lineEdit_password, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.pushButton_login = QtGui.QPushButton(self.groupBox)
        self.pushButton_login.setObjectName("pushButton_login")
        self.verticalLayout.addWidget(self.pushButton_login)
        self.loginlabel = QtGui.QLabel(self.groupBox)
        self.loginlabel.setText("")
        self.loginlabel.setObjectName("loginlabel")
        self.verticalLayout.addWidget(self.loginlabel)
        self.loginlogo = QtGui.QLabel(Dialog)
        self.loginlogo.setGeometry(QtCore.QRect(340, 30, 100, 100))
        self.loginlogo.setText("")
        self.loginlogo.setObjectName("loginlogo")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Authentication", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Login Details", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Password", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "User", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_login.setText(QtGui.QApplication.translate("Dialog", "Login!", None, QtGui.QApplication.UnicodeUTF8))

