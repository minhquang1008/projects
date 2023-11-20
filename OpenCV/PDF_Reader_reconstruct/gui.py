import datetime
import os
from PyQt5.QtWidgets import QMainWindow, QListWidget, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from pdf2image import convert_from_path
from preprocessing import Alignment
from validation import SignatureValidation
from reader import ReadFile
from tools import Tools
import pandas as pd


class ListBoxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.resize(720, 240)
        self.links = list()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    self.links.append(str(url.toLocalFile()))
                    links.append(str(url.toLocalFile()))
                else:
                    self.links.append(str(url.toString()))
                    links.append(str(url.toString()))
            self.addItems(links)
        else:
            event.ignore()


class AppDemo(QMainWindow):

    def setupUi(self, MainWindow):

        MainWindow.resize(477, 294)
        MainWindow.setWindowTitle("Chương trình ghi thông tin phiếu thu phí chứng khoán")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setWindowIcon(QIcon('phs_icon.ico'))
        # chỉnh font chữ
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        # nút run
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(320, 220, 130, 31))
        self.pushButton.setFont(font)
        self.pushButton.setText("Thao tác")
        # nút xóa nội dung widget
        self.pushButton_2 = QPushButton('Clear', MainWindow)
        self.pushButton_2.setGeometry(QtCore.QRect(20, 220, 130, 31))
        self.pushButton_2.setFont(font)
        self.pushButton_2.setText("Xóa")
        # nút xuất file excel
        self.pushButton_3 = QPushButton('Extract', MainWindow)
        self.pushButton_3.setGeometry(QtCore.QRect(170, 220, 130, 31))
        self.pushButton_3.setFont(font)
        self.pushButton_3.setText("Xem trước")
        # ô drag drop
        self.listbox_view = ListBoxWidget(MainWindow)
        self.listbox_view.setGeometry(QtCore.QRect(10, 10, 461, 201))
        self.listbox_view.setStyleSheet(
            """
            ListBoxWidget {
                background-image: url("drag_file_here.png");
                background-repeat: no-repeat;
                background-position: bottom;
            }
            """
        )
        MainWindow.setCentralWidget(self.centralwidget)


class Window:

    def __init__(self):
        self.main_win = QtWidgets.QMainWindow()
        self.uic = AppDemo()
        self.uic.setupUi(self.main_win)
        self.uic.pushButton_3.clicked.connect(self.df_extract)
        self.uic.pushButton_2.clicked.connect(self.clearListWidget)
        self.uic.pushButton.clicked.connect(self.write)
        self.__data = None
        self.__img = None
        self.df_validation = None
        self.df_content = None
        self.df = None
        self.df_total = pd.DataFrame()

    # hàm này để clear nội dung widget
    def clearListWidget(self):
        self.uic.listbox_view.clear()
        self.uic.listbox_view.links.clear()
        self.df_total = pd.DataFrame()

    @staticmethod
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

    def df_extract(self):
        self.df_total = pd.DataFrame()
        if len(self.uic.listbox_view.links) != 0:
            for i in self.uic.listbox_view.links:
                try:
                    self.__data = convert_from_path(
                        pdf_path=f'{i}',
                        dpi=400,
                        poppler_path=r'poppler-0.68.0\bin'
                    )
                    idx, detectedLines = Tools.detectPage(self.__data)
                    if detectedLines > 200:
                        self.__img = self.__data[idx]
                        self.__img = Alignment(self.__img)
                        self.__img = self.__img.rotateSheet()
                        read = ReadFile()
                        read.alignedImg = self.__img
                        if read.identifyFormKind() == 'cơ sở':
                            validation = SignatureValidation()
                            validation.alignedImg = self.__img.copy()
                            self.df_validation = validation.validateStampAndSignatureCoSo()
                            self.df_content = read.readCoSo()
                            if len(self.df_content) == 0:
                                type(self).popup(QMessageBox.Warning, 'không đủ cơ sở trích xuất dữ liệu')
                            else:
                                self.df = pd.concat([self.df_content, self.df_validation], axis=1)
                                self.df['ThoiGianChay'] = datetime.datetime.now()
                                self.df_total = self.df_total.append(self.df)
                        elif read.identifyFormKind() == 'phái sinh':
                            validation = SignatureValidation()
                            validation.alignedImg = self.__img.copy()
                            self.df_validation = validation.validateStampAndSignaturePhaiSinh()
                            self.df_content = read.readPhaiSinh()
                            if len(self.df_content) == 0:
                                type(self).popup(QMessageBox.Warning, 'không đủ cơ sở trích xuất dữ liệu')
                            else:
                                self.df = pd.concat([self.df_content, self.df_validation], axis=1)
                                self.df['ThoiGianChay'] = datetime.datetime.now()
                                self.df_total = self.df_total.append(self.df)
                        else:
                            type(self).popup(QMessageBox.Warning, 'Không phát hiện phiếu thu phí')
                            continue
                    else:
                        type(self).popup(QMessageBox.Warning, 'Không phát hiện phiếu thu phí')
                        continue
                except (ValueError, Exception):
                    type(self).popup(QMessageBox.Warning, 'Có lỗi xảy ra!')
            self.df_total.to_excel(os.path.join(os.getcwd(), 'preview.xlsx'))
            os.startfile('preview.xlsx')
            type(self).popup(QMessageBox.Information, 'Hoàn thành kết xuất file excel')
        else:
            type(self).popup(QMessageBox.Information, 'Vui lòng input file pdf')

    def write(self):
        if len(self.df_total) == 0:
            self.df_extract()
        try:
            lengthTookRows = Tools.insertToDatabase(self.df_total)
            if lengthTookRows != 0:
                type(self).popup(QMessageBox.Information, 'Hoàn thành')
            else:
                type(self).popup(QMessageBox.Information, 'Dữ liệu đã tồn tại trong database')
        except (KeyError, ValueError, Exception):
            pass


