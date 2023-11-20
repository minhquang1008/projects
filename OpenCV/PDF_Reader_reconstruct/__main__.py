import pandas as pd
from gui import Window
import sys
from PyQt5 import QtWidgets
pd.set_option('display.max_colwidth', None)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    demo = Window()
    demo.main_win.show()
    sys.exit(app.exec())

'''
 --noconsole
D:
cd D:\ProjectCompany\DataAnalytics\automation\flex_gui\PDF_Reader_reconstruct>
venv_PhieuThuPhi\Scripts\activate
pyinstaller __main__.py -D --icon=phs_icon.ico -p D:\ProjectCompany\DataAnalytics -n PDF_Reader_reconstruct --add-data phs_icon.ico;. --add-data picture;. 
'''

