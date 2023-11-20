from automation.flex_gui.RightInfo.crawlers import TinChungQuyenHOSE


if __name__ == '__main__':

    import warnings; warnings.filterwarnings('ignore')
    import datetime as dt
    from datawarehouse import BDATE
    from automation.flex_gui.RightInfo.crawlers import TinThucHienQuyenVSD, TinChungQuyenHOSE
    from automation.flex_gui.RightInfo import screen, query, gui
    from automation.flex_gui.RightInfo.worker import Worker
    from PyQt5.QtWidgets import QApplication

    def clientCall(inputDateString):

        # lấy danh sách địa chỉ mail nhận report
        with open('./MailRecipients.txt','r') as file:
            mailRecipients = file.readline()

        # Lấy thông tin đăng nhập
        with open('./Login.txt','r') as file:
            username, password = [line.strip() for line in file.readlines()[:2]]

        inputDate = dt.datetime.strptime(inputDateString,r'%d%m%Y')
        # Crawl dữ liệu
        try: TinThucHienQuyenVSD.run(inputDate,dt.datetime(2100,12,31))
        except (TinThucHienQuyenVSD.NoDataException,) as e: print(e)
        processedDateString = f'{inputDateString[-4:]}-{inputDateString[2:4]}-{inputDateString[:2]}'
        prevDate = dt.datetime.strptime(BDATE(processedDateString,-1),r'%Y-%m-%d') 
        nextDate = dt.datetime.strptime(BDATE(processedDateString,+1),r'%Y-%m-%d')
        TinChungQuyenHOSE.run(prevDate,nextDate)  # không có lỗi NoData

        # Tạo worker
        worker = Worker(
            queryFromVSD = query.DanhSachQuyenVSD(atDate=inputDate),
            queryFromF220001 = query.F220001(),
            queryFromRSE0008 = query.ChungKhoanRSE0008(atDate=inputDate),
            queryFromLog = query.LogTable(),
            mainScreen = screen.MainScreen(username,password), # 1727_1, LI26EJ95
            mailRecipients = mailRecipients
        )
        # Do jobs
        worker.doJob1()
        worker.doJob2()
        worker.doJob3()
        worker.doJob4()
        worker.doJob5()
        worker.doJob6()
        worker.doJob7()
        worker.doJob8()

    app = QApplication([])
    window = gui.UserInputWindow(clientCall)
    window.show()
    app.exec_()


r"""
BUILD

cd %PYTHONPATH%\automation\flex_gui\RightInfo\venv_RightInfo\Scripts
activate
cd ../..

pyinstaller __main__.py -D --icon=phs_icon.ico -p %PYTHONPATH% -n RightInfo --add-data chromedriver.exe;. --add-data phs_icon.ico;. --add-data regex.json;. --add-data MailRecipients.txt;. --add-data Login.txt;.

"""