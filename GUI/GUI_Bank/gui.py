from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow(object):
    def __init__(self):
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.comboBox = QtWidgets.QComboBox(self.centralWidget)
        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        self.lineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.pushButton.clicked.connect(self.run)

    def setupUi(self, Window):
        Window.resize(169, 195)
        Window.setWindowTitle("Password internet banking")
        self.comboBox.setGeometry(QtCore.QRect(10, 20, 151, 31))
        self.comboBox.addItem("IVB")
        self.comboBox.addItem("FUBON")
        self.comboBox.addItem("OCB")
        self.comboBox.addItem("HUANAN")
        self.comboBox.addItem("MEGA")
        self.comboBox.addItem("FIRST")
        self.comboBox.addItem("VCB")
        self.comboBox.addItem("SINOPAC")
        self.comboBox.addItem("BIDV")
        self.comboBox.addItem("VTB")
        self.comboBox.addItem("EIB")
        self.comboBox.addItem("ESUN")
        self.comboBox.addItem("TCB")
        self.pushButton.setGeometry(QtCore.QRect(40, 120, 91, 31))
        self.pushButton.setText("Xác nhận")
        self.lineEdit.setGeometry(QtCore.QRect(10, 80, 151, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.label.setGeometry(QtCore.QRect(10, 0, 81, 16))
        self.label.setText("Chọn ngân hàng")
        self.label_2.setGeometry(QtCore.QRect(10, 60, 81, 16))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Nhập password")
        MainWindow.setCentralWidget(self.centralWidget)

    def run(self):
        print(self.comboBox.currentText())
        print(self.lineEdit.text())


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
