from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QCheckBox, QPushButton, QWidget, QGridLayout, QLabel, QApplication
from PyQt5.QtGui import QIcon
import itertools
import sys

class GUI(QWidget):


    allBanks = {'VTB','VCB','BIDV','OCB','TCB','EIB'}
    colNumber = 3
    rowNumber = len(allBanks) // colNumber

    def __init__(self):

        super().__init__()

        self.setFixedSize(300,100)
        self.setWindowTitle("Chọn ngân hàng chi tiền")
        self.setWindowIcon(QIcon('./phs_icon2.ico'))
        self.__bankBoxes = {QCheckBox(bank,self) for bank in GUI.allBanks}
        self.__selectedBanks = GUI.allBanks  # vì mặc định chọn hết

        # Set style for Widget and Label of the window
        self.setStyleSheet(
            """
            QWidget {font-family: Times New Roman; font-size: 12px;}
            QLabel {font-size: 12px; color: red}
            """
        )
        layout = QGridLayout()
        layout.setContentsMargins(5,5,5,5)

        for bankBox, coord in zip(
            self.__bankBoxes,
            itertools.product(
                range(GUI.rowNumber),
                range(GUI.colNumber)
            )
        ):
            bankBox.setChecked(True)  # mặc định chọn hết
            layout.addWidget(bankBox,*coord)

        # Add an OK push button
        okButton = QPushButton('OK')
        okButton.clicked.connect(lambda: self.selectedBanks)
        layout.addWidget(okButton,GUI.rowNumber+1,1)

        # Thêm dòng info
        infoLabel = QLabel('(*) Các ngân hàng không được chọn sẽ đi bằng VTB.',self)
        layout.addWidget(infoLabel,GUI.rowNumber,0,1,3)
        
        # Set layout
        self.setLayout(layout)


    @property
    def selectedBanks(self):
        
        selectedBoxes = filter(lambda x: x.checkState(), self.__bankBoxes)
        self.__selectedBanks = set(map(lambda x: x.text(), selectedBoxes))
        QApplication.exit()

        return self.__selectedBanks


    def closeEvent(self, event) -> None:
        sys.exit()



# if __name__ == '__main__':

#     app = QApplication(sys.argv)
#     gui = GUI()
#     gui.show()
#     app.exec()

