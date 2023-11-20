import re
import datetime as dt

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QPushButton, QWidget, QGridLayout
from PyQt5.QtGui import QFont, QIcon

class InputWindow(QWidget):

    def __init__(self, execFunction):
        super().__init__()
        self.execFunction = execFunction
        self.setFixedSize(270, 100)
        self.setWindowTitle("Quyền")
        self.setWindowIcon(QIcon('phs_icon.ico'))

        now = dt.datetime.now()
        # Label: Từ lúc
        fromTimeLabel = QtWidgets.QLabel('Từ lúc: ')
        fromTimeLabel.setFont(QFont('Times New Roman',15))
        # Text box: Từ lúc
        fromTimeBox = QtWidgets.QLineEdit()
        fromTimeBox.setFont(QFont('Times New Roman',15))
        fromTimeBox.setText(f"{now.strftime('%d/%m/%Y')} 00:00:00")
        # Label: Đến lúc
        toTimeLabel = QtWidgets.QLabel('Đến lúc: ')
        toTimeLabel.setFont(QFont('Times New Roman',15))
        # Text box: Đến lúc
        toTimeBox = QtWidgets.QLineEdit()
        toTimeBox.setFont(QFont('Times New Roman',15))
        toTimeBox.setText(now.strftime('%d/%m/%Y %H:%M:%S'))
        
        # Button: OK
        okButton = QPushButton('OK',self)
        okButton.setFont(QFont('Times New Roman',12))
        okButton.clicked.connect(lambda: self.run(fromTimeBox,toTimeBox))
        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(5,5,5,5)
        # Set the size of the first column
        layout.setColumnMinimumWidth(1,180)
        # Add widgets to the layout
        layout.addWidget(fromTimeLabel,0,0)
        layout.addWidget(fromTimeBox,0,1)
        layout.addWidget(toTimeLabel,1,0)
        layout.addWidget(toTimeBox,1,1)
        layout.addWidget(okButton,2,0,1,2)
        # Set layout in the main window
        self.setLayout(layout)

    def run(
        self,
        fromTimeBox: QtWidgets.QLineEdit,
        toTimeBox: QtWidgets.QLineEdit,
    ):
        fromTimeText = fromTimeBox.text()
        fromTimeText = re.sub(r'\D','',fromTimeText)
        fromTimeMatch = re.search(r'\d{14}',fromTimeText)
        toTimeText = toTimeBox.text()
        toTimeText = re.sub(r'\D','',toTimeText)
        toTimeMatch = re.search(r'\d{14}',toTimeText)
        if fromTimeMatch and toTimeMatch:
            fromTime = dt.datetime.strptime(fromTimeMatch.group(),'%d%m%Y%H%M%S')
            toTime = dt.datetime.strptime(toTimeMatch.group(),'%d%m%Y%H%M%S')
            self.execFunction(fromTime, toTime)
        else:
            type(self).popUpInvalidInput(QMessageBox.Warning,'Nhập thời gian không đúng định dạng.')

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

