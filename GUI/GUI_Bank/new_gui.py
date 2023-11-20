from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class Ui_MainWindow(object):
    def __init__(self):
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.label_3 = QtWidgets.QLabel(self.centralWidget)
        self.label_4 = QtWidgets.QLabel(self.centralWidget)
        self.label_5 = QtWidgets.QLabel(self.centralWidget)
        self.lineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.comboBox = QtWidgets.QComboBox(self.centralWidget)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.centralWidget)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_2.clicked.connect(self.run)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_3.clicked.connect(self.update)
        # ----------------------------------------
        self.lineEdit_5.textChanged.connect(self.edit_text_changed)
        self.pushButton_3.setEnabled(False)
        MainWindow.setCentralWidget(self.centralWidget)

    def setupUi(self, Window):
        Window.resize(350, 210)
        Window.setWindowTitle("Password internet banking")
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setGeometry(QtCore.QRect(10, 10, 141, 21))
        self.label.setFont(font)
        self.label.setText("Mật khẩu nâng cấp")
        self.label_2.setGeometry(QtCore.QRect(10, 70, 141, 21))
        self.label_2.setFont(font)
        self.label_2.setText("Ngân hàng")
        self.label_3.setGeometry(QtCore.QRect(10, 100, 141, 21))
        self.label_3.setFont(font)
        self.label_3.setText("Mật khẩu NH cũ")
        self.label_4.setGeometry(QtCore.QRect(10, 130, 141, 21))
        self.label_4.setFont(font)
        self.label_4.setText("Mật khẩu NH mới")
        self.label_5.setGeometry(QtCore.QRect(10, 40, 161, 21))
        self.label_5.setFont(font)
        self.label_5.setText("Mật khẩu nâng cấp mới")
        self.lineEdit.setGeometry(QtCore.QRect(180, 10, 161, 21))
        self.lineEdit.setFont(font)
        self.comboBox.setGeometry(QtCore.QRect(180, 70, 161, 21))
        self.comboBox.setFont(font)
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
        self.lineEdit_3.setGeometry(QtCore.QRect(180, 100, 161, 21))
        self.lineEdit_3.setFont(font)
        self.lineEdit_4.setGeometry(QtCore.QRect(180, 130, 161, 21))
        self.lineEdit_4.setFont(font)
        self.lineEdit_5.setGeometry(QtCore.QRect(180, 40, 161, 21))
        self.lineEdit_5.setFont(font)
        self.pushButton_2.setGeometry(QtCore.QRect(30, 160, 111, 31))
        self.pushButton_2.setFont(font)
        self.pushButton_2.setText("Xác nhận")
        self.pushButton_3.setGeometry(QtCore.QRect(190, 160, 111, 31))
        self.pushButton_3.setFont(font)
        self.pushButton_3.setText("Cập nhật")
        MainWindow.setCentralWidget(self.centralWidget)

    def run(self):
        print(self.comboBox.currentText())
        print(self.lineEdit.text())

    def update(self):
        print(self.lineEdit_5.text())

    def edit_text_changed(self):
        if self.lineEdit_5.text() == '':
            self.pushButton_3.setEnabled(False)
        else:
            self.pushButton_3.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
