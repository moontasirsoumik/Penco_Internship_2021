# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'feed.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(684, 537)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_cam1 = QtWidgets.QLabel(self.centralwidget)
        self.label_cam1.setMaximumSize(QtCore.QSize(640, 480))
        self.label_cam1.setAlignment(QtCore.Qt.AlignCenter)
        self.label_cam1.setObjectName("label_cam1")
        self.horizontalLayout.addWidget(self.label_cam1)
        self.label_cam2 = QtWidgets.QLabel(self.centralwidget)
        self.label_cam2.setMaximumSize(QtCore.QSize(640, 480))
        self.label_cam2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_cam2.setObjectName("label_cam2")
        self.horizontalLayout.addWidget(self.label_cam2)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 684, 28))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Camera Feed"))
        self.label_cam1.setText(_translate("MainWindow", "Camera 1"))
        self.label_cam2.setText(_translate("MainWindow", "Camera 2"))
        self.pushButton.setText(_translate("MainWindow", "Start"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

