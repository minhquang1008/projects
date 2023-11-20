import re
import time
import traceback
import cv2 as cv
import numpy as np
import pandas as pd
from abc import ABC
import datetime as dt
from win32com.client import Dispatch
from automation.flex_gui.base import Flex
from pywinauto.application import Application
from request import connect_DWH_ThiTruong, connect_DWH_CoSo
import warnings
warnings.filterwarnings("ignore")
import os
import pickle
from query import *
from factory import *


SLEEP_TIME = 3

class F020004(Flex):
    def __init__(self,username,password):
        super().__init__()
        self.start(existing=False)  # Tạo Flex instance mới
        self.login(username,password)
        self.insertFuncCode('020004')
        self.funcWindow = self.app.window(auto_id='frmSearch')
        self.insertWindow = self.app.window(auto_id='frmMaster')
        self.innerWindow = self.app.window(title="Danh sách chứng khoán")
        self.dataWindow = None
        self.__outlook = Dispatch('outlook.application')
        self.__dateRun = dt.datetime(2022,12,1).strftime('%Y-%m-%d')
        self.__mailDate = dt.datetime(2022,12,1).strftime('%d/%m/%Y')
        self.__history = './history.pickle'
        if not os.path.isfile(self.__history): # nếu chưa có file history -> tạo
            with open(self.__history,'wb') as file:
                pickle.dump(pd.DataFrame(columns=['MaChungKhoan']),file)

    def writeHistory(self,fileName):
        data = self.readHistory()
        data=data.append(fileName,ignore_index=True)
        with open(self.__history,'wb') as file:
            pickle.dump(data,file)

    def readHistory(self):
        with open(self.__history,'rb') as file:
            return pickle.load(file)

    def updateNewStock(self):
        def __findTopLeftPoint(containingImage, templateImage):
            containingImage = np.array(containingImage)  # đảm bảo image để được đưa về numpy array
            templateImage = np.array(templateImage)  # đảm bảo image để được đưa về numpy array
            matchResult = cv.matchTemplate(containingImage, templateImage, cv.TM_CCOEFF)
            _, _, _, topLeft = cv.minMaxLoc(matchResult)
            return topLeft[1], topLeft[0]  # cho compatible với openCV

        def __findColumnCoords(colName):
            if colName == 'TenVietTat':
                fileName = 'TenVietTat.png'
            else:
                raise ValueError('colName must be either "TenVietTat"')

            tempImage = cv.imread(fr".\{fileName}")
            tempImage = cv.cvtColor(tempImage, cv.COLOR_RGB2BGR)
            headerTop, headerLeft = __findTopLeftPoint(dataImage, tempImage)
            columnLeft = headerLeft  # left của header và column là giống nhau
            columnRight = columnLeft + tempImage.shape[1]
            columnTop = headerTop + tempImage.shape[0]  # top của của cột là bottom của header

            return (columnTop, columnLeft), (columnTop, columnRight)

        def __processFlexImage(image, threshold):
            flexGrayImg = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
            _, flexBinaryImg = cv.threshold(flexGrayImg, threshold, 255, cv.THRESH_BINARY)
            return flexBinaryImg

        def __findRowHeight(binaryRecordImage):
            sumIntensity = binaryRecordImage.sum(axis=1)
            minLocArray = np.asarray(sumIntensity == sumIntensity.min()).nonzero()
            minLocArray = np.insert(minLocArray, 0, 0)
            rowHeightArray = np.diff(minLocArray)
            rowHeightArray = rowHeightArray[rowHeightArray < 30]  # row height ko thể lớn hơn 30 pixel
            rowHeight = np.median(rowHeightArray).astype(int)
            return rowHeight

        def __cropColumn(colName):
            topLeft, topRight = __findColumnCoords(colName)
            top = topLeft[0]
            left = topLeft[1]
            right = topRight[1]
            bottom = dataImage.shape[0]
            return dataImage[top:bottom, left:right, :]

        def __clickRow(rowNumber, rowHeight):
            topLeft, topRight = __findColumnCoords('TenVietTat')
            left = topLeft[1]
            right = topRight[1]
            top = topLeft[0]
            midPoint = (int(left * 0.9 + right * 0.1), int(top + rowHeight / 2 * (2 * rowNumber - 1)))
            Flex.setFocus(self.funcWindow)
            self.dataWindow.click_input(coords=midPoint, absolute=False)

        def __takeFlexScreenshot(window):
            Flex.setFocus(window)
            return cv.cvtColor(np.array(window.capture_as_image()), cv.COLOR_RGB2BGR)

        def __clickCreateButton():
            Flex.setFocus(self.funcWindow)
            while True:  # đợi maximize window xong
                if self.funcWindow.rectangle() == self.mainWindow.rectangle():
                    break
                time.sleep(0.5)
            actionWindow = self.funcWindow.child_window(title='SMS')
            actionImage = __takeFlexScreenshot(actionWindow)
            actionImage = actionImage[:,:-10,:]
            unique, count = np.unique(actionImage,return_counts=True, axis=1)
            mostFrequentColumn = unique[:,np.argmax(count),:]
            columnMask = ~(actionImage == mostFrequentColumn[:,np.newaxis,:]).all(axis=(0,2))
            lastColumn = np.argwhere(columnMask).max()
            croppedImage = actionImage[:,:lastColumn,:]
            midPoint = croppedImage.shape[1]//7,croppedImage.shape[0]//2
            actionWindow.click_input(coords=midPoint)
            self.insertWindow.wait('exists',timeout=30)

        def __clickModifyButton():
            Flex.setFocus(self.funcWindow)
            while True:  # đợi maximize window xong
                if self.funcWindow.rectangle() == self.mainWindow.rectangle():
                    break
                time.sleep(0.5)
            actionWindow = self.funcWindow.child_window(title='SMS')
            actionImage = __takeFlexScreenshot(actionWindow)
            actionImage = actionImage[:,:-10,:]
            unique, count = np.unique(actionImage,return_counts=True,axis=1)
            mostFrequentColumn = unique[:,np.argmax(count),:]
            columnMask = ~(actionImage == mostFrequentColumn[:,np.newaxis,:]).all(axis=(0, 2))
            lastColumn = np.argwhere(columnMask).max()
            croppedImage = actionImage[:,:lastColumn,:]
            midPoint = int(croppedImage.shape[1]/2.2),croppedImage.shape[0]//2
            actionWindow.click_input(coords=midPoint)
            self.insertWindow.wait('exists', timeout=30)

        def __clickSearchButton():
            Flex.setFocus(self.funcWindow)
            while True:  # đợi maximize window xong
                if self.funcWindow.rectangle() == self.mainWindow.rectangle():
                    break
                time.sleep(0.5)
            searchBox = self.funcWindow.child_window(auto_id='btnSearch')
            searchBox.click()

        def __clickAcceptButton():
            Flex.setFocus(self.insertWindow)
            acceptButton = self.insertWindow.child_window(auto_id='btnOK')
            acceptButton.click_input()

        def __clickSuccess():
            successWindow = self.app.window(title='FlexCustodian')
            successWindow.wait('exists', timeout=45)  # chờ ghi nhận dữ liệu xong
            okButton = successWindow.child_window(title='OK')
            okButton.click_input()

        def __clickBtnRemoveAll():
            Flex.setFocus(self.funcWindow)
            btnRemoveAll = self.funcWindow.child_window(auto_id='btnRemoveAll')
            btnRemoveAll.click_input()

        def __clickBtnAdd():
            Flex.setFocus(self.funcWindow)
            btnNext = self.funcWindow.child_window(auto_id='btnAdd')
            btnNext.click_input()

        def __selectTieuChi(textString):
            Flex.setFocus(self.funcWindow)
            self.funcWindow.window(best_match='Tiêu chí:ComboBox').select(textString)
            time.sleep(1)

        def __selectGiaTri(textString):
            Flex.setFocus(self.funcWindow)
            textBox = self.funcWindow.child_window(auto_id='txtValue')
            Flex.sendTextByKeyboard(textBox,textString)

        def __fillTabTTChung(object):
            Flex.setFocus(self.insertWindow)
            # click chuột vào @ của Mã TCPH
            self.insertWindow.child_window(auto_id='btnDataISSUERID').click()
            # điền các trường thông tin cần thiết
            Flex.sendTextByKeyboard(self.insertWindow.child_window(auto_id='mskDataSHORTNAME'),object.getTenVietTat())
            Flex.sendTextByKeyboard(self.insertWindow.child_window(auto_id='mskDataFULLNAME'),object.getTCPH())
            Flex.sendTextByKeyboard(self.insertWindow.child_window(auto_id='mskDataOFFICENAME'),object.getTenGD())
            Flex.sendTextByKeyboard(self.insertWindow.child_window(auto_id='mskDataEN_OFFICENAME'),object.getTenGDTA())
            Flex.sendTextByKeyboard(self.insertWindow.child_window(auto_id='mskDataEN_FULLNAME'),object.getTenTA())
            Flex.sendTextByClipboard(self.insertWindow.child_window(auto_id='mskDataMARKETSIZE'),'Trong nước')
            Flex.sendTextByClipboard(self.insertWindow.child_window(auto_id='mskDataVSDPLACE'),object.getNoiQuanLyVSD())
            Flex.sendTextByKeyboard(self.insertWindow.child_window(auto_id='mskDataISINCODE'),object.getMaISIN())

        def __fillSuaCoPhieu(object):
            Flex.setFocus(self.innerWindow)
            self.innerWindow.child_window(auto_id='btnDataCODEID').click_input()
            # điền các trường thông tin cần thiết
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataSECTYPE'),'Cổ phiếu')
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskDataSYMBOL'),object.getMaCK())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataTRADEPLACE'),object.getNoiGD())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataBONDTYPE'),object.getLoaiTraiPhieu())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataISSEDEPOFEE'),'Có')
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataPARVALUE'),object.getMenhGia())

        def __fillSuaChungChiQuy(object):
            Flex.setFocus(self.innerWindow)
            self.innerWindow.child_window(auto_id='btnDataCODEID').click_input()
            # điền các trường thông tin cần thiết
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataSECTYPE'),'Chứng chỉ quỹ')
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskDataSYMBOL'),object.getMaCK())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataTRADEPLACE'),object.getNoiGD())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataBONDTYPE'),object.getLoaiTraiPhieu())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataISSEDEPOFEE'),'Có')
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataPARVALUE'),object.getMenhGia())

        def __fillSuaTraiPhieu(object):
            Flex.setFocus(self.innerWindow)
            self.innerWindow.child_window(auto_id='btnDataCODEID').click_input()
            # điền các trường thông tin cần thiết
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataSECTYPE'),'Trái phiếu')
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskDataSYMBOL'),object.getMaCK())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataTRADEPLACE'),'BOND')
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataBONDTYPE'),object.getLoaiTraiPhieu())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataISSEDEPOFEE'),'Có')
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataPARVALUE'),object.getMenhGia())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataTYPETERM'),object.getLoaiKyHan())
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskDataTERM'),object.getKyHan())

        def __fillSuaChungQuyen(object):
            Flex.setFocus(self.innerWindow)
            self.innerWindow.child_window(auto_id='btnDataCODEID').click_input()
            # điền các trường thông tin cần thiết
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataSECTYPE'),'Chứng quyền')
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskDataSYMBOL'),object.getMaCK())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataTRADEPLACE'),object.getNoiGD())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataBONDTYPE'),object.getLoaiTraiPhieu())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataISSEDEPOFEE'),'Có')
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskDataPARVALUE'),'10000')
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskData011UNDERLYINGTYPE'),'cổ phiếu')
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskData011UNDERLYINGSYMBOL'),object.getMaCKCS())
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskData011ISSUERNAME'),object.getToChucPhatHanhMaCKCS())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskData011COVEREDWARRANTTYPE'), object.getLoaiChungQuyen())
            Flex.sendTextByClipboard(self.innerWindow.child_window(auto_id='mskData011SETTLEMENTTYPE'),object.getPhuongThucThanhToan())
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskData011EXERCISEPRICE'),object.getGiaThucHien())
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskData011EXERCISERATIO'),object.getTyLeChuyenDoi())
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskData011CWTERM'),object.getThoiHan())
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskData011MATURITYDATE'),object.getNgayDaoHan())
            Flex.sendTextByKeyboard(self.innerWindow.child_window(auto_id='mskData011LASTTRADINGDATE'), object.getGiaoDichCuoiCung())


        def __emailBatThuong():
            """
            Hàm dùng để kiểm tra xem các mã mới từ điện trả về trên 154000 đã có trong 020004 chưa
            Nếu có thì gửi mail cảnh báo bất thường
            """
            query = query020004()
            query._dateRun = self.__dateRun
            table=query.query
            if not table.empty:
                contentHTML = ', '.join(table['MaChungKhoan'])
                htmlBody = f"""
                <html>
                    <head></head>
                    <body>
                        <p style="font-family:Times New Roman; font-size:100%">
                            Ngày {self.__mailDate} các mã {contentHTML} 
                            chưa được thêm mới nhưng đã có trên màn hình 020004
                        </p>
                        <p style="font-family:Times New Roman; font-size:80%"><i>
                            -- Generated by Reporting System
                        </i></p>
                    </body>
                </html>
                """
                self.__mail = self.__outlook.CreateItem(0)
                self.__mail.To = 'quangpham@phs.vn'
                self.__mail.Subject = f"Ngày {self.__mailDate} các mã {contentHTML} bất thường"
                self.__mail.HTMLBody = htmlBody
                self.__mail.Send()

        def __emailHoanTatNhap(stockList):
            """
            Hàm dùng để gửi email thông báo khi phần mềm hoàn tất quá trình nhập thông
            tin mã chứng khoán (tới bước duyệt thứ nhất)
            """
            contentHTML = ', '.join(stockList)
            htmlBody = f"""
            <html>
                <head></head>
                <body>
                    <p style="font-family:Times New Roman; font-size:100%">
                        Ngày {self.__mailDate} các mã chứng khoán: {contentHTML} đã được thêm đầy đủ 
                        các thông tin vào màn hình 020004
                    </p>
                    <p style="font-family:Times New Roman; font-size:80%"><i>
                        -- Generated by Reporting System
                    </i></p>
                </body>
            </html>
            """
            self.__mail = self.__outlook.CreateItem(0)
            self.__mail.To = 'quangpham@phs.vn'
            self.__mail.Subject = f"Ngày {self.__mailDate} các mã {contentHTML} bất thường"
            self.__mail.HTMLBody = htmlBody
            self.__mail.Send()

        print('::: WELCOME :::')
        print('Flex GUI Automation - Author: Hiep Dang')
        print('===========================================\n')

        # gửi mail trường hợp bất thường
        # __emailBatThuong()
        # kiểm tra trên 154000 xem có mã nào mới ko
        query=query154000()
        query._dateRun=self.__dateRun
        table = query.query
        # tạo 1 list rỗng để chứa các stock đã thêm thành công
        stockList = []
        # query xem nã CK mới từ điện VSD trả về có nằm trong màn hình 020004 không
        dfNewStock = table
        history_table=self.readHistory().drop_duplicates(inplace=True)
        table = table.merge(history_table, on=['MaChungKhoan'],how='left', indicator=True)
        table = table[table['_merge'] == 'left_only']
        if history_table.shape[0]!=0:
            for i in range(history_table.shape[0]):
                loaiCK, typeObject = findTypeStock(table['MaChungKhoan'].iloc[i])
                if loaiCK == 'Chưa có thông tin trên VSD hoặc chưa crawl data':
                    continue
                else:
                    typeObject.ticker = table['MaChungKhoan'].iloc[i]
                    # click nút Thêm mới
                    __clickCreateButton()
                    # Điền thông tin
                    __fillTabTTChung(typeObject)
                    # Click Chấp Nhận
                    __clickAcceptButton()
                    # Click OK "Thêm dữ liệu thành công"
                    __clickSuccess()
                    # Nghỉ 2 giây sau khi vừa thêm mới
                    time.sleep(SLEEP_TIME)
                    # Reset lại danh sách điều kiện tìm kiếm
                    __clickBtnRemoveAll()
                    # Chọn loại tiêu chí
                    __selectTieuChi('Tên viết tắt')
                    __selectGiaTri(table['MaChungKhoan'].iloc[i])
                    __clickBtnAdd()
                    # Click "Tìm kiếm" để kiểm tra mã đã có trên Flex chưa
                    __clickSearchButton()
                    # Screen shot khung dữ liệu
                    self.dataWindow = self.funcWindow.child_window(auto_id='pnlSearchResult')
                    dataImage = __takeFlexScreenshot(self.dataWindow)
                    codeIsInImage = __cropColumn('TenVietTat')
                    # Click chọn mã trên khung dữ liệu
                    codeISINBinaryImage = __processFlexImage(codeIsInImage, 200)
                    rowHeight = __findRowHeight(codeISINBinaryImage)
                    __clickRow(1, rowHeight)
                    # Click "Sửa"
                    __clickModifyButton()
                    # trõ vào tab panel và chọn sang tab Chứng khoán
                    self.insertWindow.child_window(auto_id="tabMaster").select('TabControlChứng khoán')
                    self.insertWindow.child_window(auto_id="btnTabPage_SASECURITIES_Insert").click_input()
                    print(loaiCK)
                    if loaiCK == 'Cổ phiếu thường':
                        __fillSuaCoPhieu(typeObject)
                    elif loaiCK == 'Chứng chỉ quỹ':
                        __fillSuaChungChiQuy(typeObject)
                    elif loaiCK == 'Trái phiếu':
                        __fillSuaTraiPhieu(typeObject)
                    elif loaiCK == 'Chứng quyền':
                        __fillSuaChungQuyen(typeObject)
                    else:
                        raise NoType('Không nằm trong 4 loại cơ bản')
                    self.innerWindow.child_window(auto_id="btnOK").click_input()
                    __clickSuccess()
                    self.insertWindow.child_window(auto_id="btnOK").click_input()
                    __clickSuccess()
                    history_table.drop([i],inplace=True).reset_index()
                    self.writeHistory(history_table)
        for i in range(table.shape[0]):
            # nếu mã CK trong 154000 có trong 020004 rồi thì bỏ qua
            # if dfNewStock['MaChungKhoan'].str.contains(table['MaChungKhoan'].iloc[i]).any():
            #     continue
            # chọn loại CK tương ứng
            loaiCK, typeObject = findTypeStock(table['MaChungKhoan'].iloc[i])
            print("in ra: ",loaiCK)
            if loaiCK=='Chưa có thông tin trên VSD hoặc chưa crawl data':
                self.writeHistory(table)
                continue
            else:
                typeObject.ticker = table['MaChungKhoan'].iloc[i]
                # click nút Thêm mới
                __clickCreateButton()
                # Điền thông tin
                __fillTabTTChung(typeObject)
                # Click Chấp Nhận
                __clickAcceptButton()
                # Click OK "Thêm dữ liệu thành công"
                __clickSuccess()
                # Nghỉ 2 giây sau khi vừa thêm mới
                time.sleep(SLEEP_TIME)
                # Reset lại danh sách điều kiện tìm kiếm
                __clickBtnRemoveAll()
                # Chọn loại tiêu chí
                __selectTieuChi('Tên viết tắt')
                __selectGiaTri(table['MaChungKhoan'].iloc[i])
                __clickBtnAdd()
                # Click "Tìm kiếm" để kiểm tra mã đã có trên Flex chưa
                __clickSearchButton()
                # Screen shot khung dữ liệu
                self.dataWindow = self.funcWindow.child_window(auto_id='pnlSearchResult')
                dataImage = __takeFlexScreenshot(self.dataWindow)
                codeIsInImage = __cropColumn('TenVietTat')
                # Click chọn mã trên khung dữ liệu
                codeISINBinaryImage = __processFlexImage(codeIsInImage, 200)
                rowHeight = __findRowHeight(codeISINBinaryImage)
                __clickRow(1, rowHeight)
                # Click "Sửa"
                __clickModifyButton()
                #trõ vào tab panel và chọn sang tab Chứng khoán
                self.insertWindow.child_window(auto_id="tabMaster").select('TabControlChứng khoán')
                self.insertWindow.child_window(auto_id="btnTabPage_SASECURITIES_Insert").click_input()
                self.insertWindow.print_control_identifiers()
                print(loaiCK)
                if loaiCK=='Cổ phiếu thường':
                    __fillSuaCoPhieu(typeObject)
                elif loaiCK=='Chứng chỉ quỹ':
                    __fillSuaChungChiQuy(typeObject)
                elif loaiCK=='Trái phiếu':
                    __fillSuaTraiPhieu(typeObject)
                elif loaiCK=='Chứng quyền':
                    __fillSuaChungQuyen(typeObject)
                else:
                    raise NoType('Không nằm trong 4 loại cơ bản')

                self.innerWindow.child_window(auto_id="btnOK").click_input()
                __clickSuccess()
                self.insertWindow.child_window(auto_id="btnOK").click_input()
                __clickSuccess()

if __name__ == '__main__':
    try:
        flexObject = F020004('admin','123456')
        flexObject.updateNewStock()
    except (Exception,):  # để debug
        print(traceback.format_exc())
        input('Press any key to quit: ')
        try:  # Khi cửa sổ Flex còn mở
            app = Application().connect(title_re=r'^\.::.*Flex.*', timeout=10)
            app.kill()
        except (Exception,):  # Khi cửa sổ Flex đã đóng sẵn
            pass

