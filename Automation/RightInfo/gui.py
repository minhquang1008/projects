import re
import datetime as dt

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QPushButton, QWidget, QGridLayout
from PyQt5.QtGui import QFont, QIcon


class UserInputWindow(QWidget):

    def __init__(self, execFunction):
        super().__init__()
        self.execFunction = execFunction

        windowWidth = 240
        windowHeight = 80
        spaceMargin = 5

        self.setFixedSize(windowWidth, windowHeight)
        self.setWindowTitle("Quyền")
        self.setWindowIcon(QIcon('phs_icon.ico'))

        # Label: Input date
        dateLabel = QtWidgets.QLabel('Đến ngày: ')
        dateLabel.setFont(QFont('Times New Roman',15))
        # Textbox: Input date
        DateTextbox = QtWidgets.QLineEdit()
        DateTextbox.setFont(QFont('Times New Roman',15))
        DateTextbox.setText(dt.date.today().strftime('%d/%m/%Y'))
        # Button: OK
        okButton = QPushButton('OK',self)
        okButton.setFont(QFont('Times New Roman',12))
        okButton.clicked.connect(lambda: self.run(DateTextbox))
        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(spaceMargin,spaceMargin,spaceMargin,spaceMargin)
        # Set the size of the first column
        layout.setColumnMinimumWidth(0,(windowWidth-3*spaceMargin)//2)
        # Add widgets to the layout
        layout.addWidget(dateLabel,0,0)
        layout.addWidget(DateTextbox,0,1)
        layout.addWidget(okButton,1,0,1,2)
        # Set layout in the main window
        self.setLayout(layout)

    def run(
        self,
        box: QtWidgets.QLineEdit
    ):
        rawDateString = box.text()
        dateString = re.sub(r'\D','',rawDateString)
        matchRegex = re.search(r'\d{8}',dateString)
        if matchRegex:
            dateString = matchRegex.group()
            self.close()
            self.execFunction(dateString)
        else:
            type(self).popUpInvalidInput(QMessageBox.Warning,'Nhập ngày không hợp lệ.')

    @staticmethod
    def popUpInvalidInput(
        icon: QtWidgets.QMessageBox.Icon,
        message: str,
    ):
        messageBox = QMessageBox()
        messageBox.setIcon(icon)
        messageBox.setWindowIcon(QIcon('phs_icon.ico'))
        messageBox.setWindowTitle('Thông báo')
        messageBox.setText(message)
        messageBox.exec()


