from PyQt5 import QtCore, QtWidgets
import query
import xlsx_writer
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox


class Ui_MainWindow(object):
    def __init__(self):
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.textEdit_2 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_3 = QtWidgets.QTextEdit(self.centralwidget)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.clicked.connect(self.openFile)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.__path = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(169, 256)
        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setMenuBar(self.menubar)
        MainWindow.setStatusBar(self.statusbar)
        self.textEdit.setGeometry(QtCore.QRect(10, 20, 151, 31))
        self.label.setGeometry(QtCore.QRect(10, 0, 61, 16))
        self.label.setObjectName("label")
        self.textEdit_2.setGeometry(QtCore.QRect(10, 120, 151, 31))
        self.textEdit_3.setGeometry(QtCore.QRect(10, 70, 151, 31))
        self.label_2.setGeometry(QtCore.QRect(10, 50, 61, 16))
        self.label_3.setGeometry(QtCore.QRect(10, 100, 61, 16))
        self.pushButton.setGeometry(QtCore.QRect(40, 160, 91, 23))
        self.pushButton_2.setGeometry(QtCore.QRect(40, 190, 91, 23))
        self.menubar.setGeometry(QtCore.QRect(0, 0, 169, 21))
        self.label.setText("Room code")
        self.label_2.setText("Start date")
        self.label_3.setText("End date")
        self.pushButton.setText("Extract report")
        self.pushButton_2.setText("Open report")

    def run(self):
        smrInfor = query.SummaryInformation()
        smrInfor.end_date = self.textEdit_2.toPlainText()
        smrInfor.start_date = self.textEdit_3.toPlainText()
        df = smrInfor.getData()
        writer = xlsx_writer.ExcelWriter()
        writer.room_code = self.textEdit.toPlainText()
        writer.data1 = df
        mthReport = query.MonthlyDealReport(df)
        mthReport.end_date = self.textEdit_2.toPlainText()
        df2 = mthReport.getData()
        writer.data2 = df2
        writer.data1.fillna("", inplace=True)
        writer.data2.fillna("", inplace=True)
        self.__path = writer.writeFullReport()

    def openFile(self):
        if self.__path:
            os.startfile(self.__path)
        else:
            type(self).popup(QMessageBox.Information, 'Extract report first')

    def popup(
        icon: QtWidgets.QMessageBox.Icon,
        message: str,
    ):
        messageBox = QMessageBox()
        messageBox.setIcon(icon)
        messageBox.setWindowIcon(QIcon('phs_icon.ico'))
        messageBox.setWindowTitle('Thông báo')
        messageBox.setText(message)
        messageBox.exec()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
