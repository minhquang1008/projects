from PyQt5.QtWidgets import QApplication
from gui import InputWindow
from report import Report

# import os
# os.chdir(r"C:\Users\hiepdang\PycharmProjects\DataAnalytics\automation\trading_service\giaodichluuky\TinDauGia")
app = QApplication([])
window = InputWindow(lambda fromTime, toTime: Report(fromTime,toTime).show())
window.show()
app.exec_()

r"""
BUILD

cd C:\Users\hiepdang\PycharmProjects\DataAnalytics\automation\trading_service\giaodichluuky\TinDauGia\venv_TinDauGia\Scripts
activate
cd ../..

pyinstaller __main__.py -D --icon=phs_icon.ico --noconsole -p C:\Users\hiepdang\PycharmProjects\DataAnalytics -n TinDauGia --add-data chromedriver.exe;. --add-data phs_icon.ico;. --add-data phs_logo.png;.

"""

