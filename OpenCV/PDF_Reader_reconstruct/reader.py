import numpy as np
import pandas as pd
import cv2
import pytesseract
import statistics
import os
import re
from detect_lines import LineSpecify
import json
from datetime import datetime
pytesseract.pytesseract.tesseract_cmd = fr"Tesseract-OCR\tesseract.exe"


class ReadFile(LineSpecify):
    def __init__(self) -> None:
        super().__init__()
        self.__templatePhaiSinh = cv2.imread("picture/PhaiSinh.png", cv2.IMREAD_GRAYSCALE)
        self.__templateCoSo = cv2.imread("picture/CoSo.png", cv2.IMREAD_GRAYSCALE)

    @property
    def alignedImg(self) -> pd.DataFrame:
        return self._alignedImg

    @alignedImg.setter
    def alignedImg(self, alignedImg) -> None:
        self._alignedImg = alignedImg

    # tìm tọa độ hình trong hình
    def getTextFromTemplateImage(
            self,
            image: np.array,
            templateType: str
    ):
        if 'PhaiSinh' in templateType:
            templateImg = self.__templatePhaiSinh
        elif 'CoSo' in templateType:
            templateImg = self.__templateCoSo
        else:
            return ''
        widthCoSo, heightCoSo = templateImg.shape[::-1]
        matchResult = cv2.matchTemplate(image, templateImg, cv2.TM_CCOEFF)
        x, y = cv2.minMaxLoc(matchResult)[-1]
        croppedImage = image[y - 30: y + heightCoSo + 30, x - 50: x + widthCoSo + 50]
        return pytesseract.image_to_string(
            image=croppedImage,
            lang='eng',
            config='--psm 6'
        )

    # xác định file là cơ sở hay phái sinh
    def identifyFormKind(self):
        image = self.alignedImg.copy()[:, :, 0]
        textCoSo = self.getTextFromTemplateImage(image, r'CoSo')
        textPhaiSinh = self.getTextFromTemplateImage(image, r'PhaiSinh')
        if 'RECEIPT' in textCoSo:
            return "cơ sở"
        elif 'PHAI SINH' in textPhaiSinh:
            return "phái sinh"
        else:
            return ''

    # đọc chữ
    @staticmethod
    def __tesseractReadWord(cut_img):
        kernel = np.ones((2, 2), np.uint8)
        cut_img = cv2.erode(cut_img, kernel)
        return pytesseract.image_to_string(cut_img, lang="vie+eng", config='--psm 11')

    # đọc số
    @staticmethod
    def __tesseractReadNumber(cut_img):
        kernel = np.ones((2, 2), np.uint8)
        cut_img = cv2.erode(cut_img, kernel)
        return pytesseract.image_to_string(cut_img, config='--psm 11 -c tessedit_char_whitelist=0123456789')

    # đọc số tài khoản, thường chỉ có chữ viết hoa và số
    @staticmethod
    def __tesseractReadAccount(cut_img):
        kernel = np.ones((2, 2), np.uint8)
        cut_img = cv2.erode(cut_img, kernel)
        return pytesseract.image_to_string(cut_img, lang="eng",
                       config='--psm 11 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

    # xóa một số kí tự thừa do pytesseract trả ra nhầm
    @staticmethod
    def __parseOutput(tesseractOutput):
        return tesseractOutput.replace("\n", "").replace(".", "").replace("_", "").replace("-", "").replace("—", "")

    # parse ra trường account
    @staticmethod
    def __parseAccount(tesseractOutput):
        regex = ''.join(re.findall("[A-Z0-9]", tesseractOutput))
        if regex:
            return regex
        return ''

    # parse kết quả chỉ chứa chữ
    @staticmethod
    def __parseOnlyWord(tesseractOutput):
        regex = ''.join(re.findall("\D+", tesseractOutput))
        if regex:
            return regex
        return ''

    # xóa các đường kẻ màu đen khi cắt hình để tránh đọc nhầm
    @staticmethod
    def __eraseBlackLines(image):
        result = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(result, [c], -1, (255, 255, 255), 5)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(result, [c], -1, (255, 255, 255), 5)
        # cv2.imwrite('pic.png', result)
        return result

    # lấy ra vị trí của chữ cần lấy trong hình cắt
    @staticmethod
    def __cutCell(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
        dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        im2 = img.copy()
        croppedList = list()
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cropped = im2[y:y + h, x:x + w]
            croppedList.append(cropped)
        densityList = [(i.sum(axis=1).sum(axis=1).sum())/(i.shape[0]*i.shape[1]) for i in croppedList]
        idx = densityList.index(min(densityList))
        return croppedList[idx]

    # đọc file cơ sở
    def readCoSo(self):
        imgCode = self.alignedImg.sum().sum().sum()
        xcoordinateGroupDict = self._specifyVerticalLongLines()
        ycoordinateGroupDict = self._specifyHorizontalLongLines(1, 51)
        if len(ycoordinateGroupDict) != 51:
            ycoordinateGroupDict = self._specifyHorizontalLongLines(0, 51)
        if len(ycoordinateGroupDict) == 51:
            # ----------------width--------------------------------------------------------------------
            firstVerticalLine = xcoordinateGroupDict[list(xcoordinateGroupDict.keys())[0]]
            x = int(statistics.median(firstVerticalLine))
            width = int(statistics.median(xcoordinateGroupDict[list(xcoordinateGroupDict.keys())[-1]])) - \
                    int(statistics.median(xcoordinateGroupDict.get(0)))
            column1 = int(width*0.2808)
            column2 = int(width*0.5197)
            column3 = int(width*0.6667)
            column4 = int(width)
            self.alignedImg = self.__eraseBlackLines(self.alignedImg)
            top = int(statistics.median(ycoordinateGroupDict.get(0)))
            bot = int(statistics.median(ycoordinateGroupDict.get(1)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            regex = re.findall("(?<=:).*", self.__tesseractReadWord(cut_img))
            tenChiNhanh_3_0 = None
            Ngay_3_0 = None
            if len(regex) == 2:
                tenChiNhanh_3_0 = str(regex[0]).strip()
                Ngay_3_0 = str(regex[1]).strip()
                tenChiNhanh_3_0 = self.__parseOutput(tenChiNhanh_3_0)
                Ngay_3_0 = self.__parseOutput(Ngay_3_0)
                if len(tenChiNhanh_3_0) == 0:
                    tenChiNhanh_3_0 = None
                if re.match('\d\d\/\d\d\/\d\d\d\d', Ngay_3_0):
                    Ngay_3_0 = datetime.strptime(Ngay_3_0, '%m/%d/%y')
                else:
                    Ngay_3_0 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(1)))
            bot = int(statistics.median(ycoordinateGroupDict.get(2)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tenKhachHang_1_1 = self.__tesseractReadWord(cut_img)
            tenKhachHang_1_1 = self.__parseOutput(tenKhachHang_1_1)
            if len(tenKhachHang_1_1) == 0:
                tenKhachHang_1_1 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(1)))
            bot = int(statistics.median(ycoordinateGroupDict.get(2)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soTaiKhoan_3_1 = None
            else:
                soTaiKhoan_3_1 = self.__tesseractReadAccount(cut_img)
                soTaiKhoan_3_1 = self.__parseAccount(soTaiKhoan_3_1)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(5)))
            bot = int(statistics.median(ycoordinateGroupDict.get(6)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maChungKhoan_0_5 = None
            else:
                maChungKhoan_0_5 = self.__tesseractReadWord(cut_img)
                maChungKhoan_0_5 = self.__parseOutput(maChungKhoan_0_5)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(5)))
            bot = int(statistics.median(ycoordinateGroupDict.get(6)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            soLuongCoPhieu_1_5 = self.__tesseractReadNumber(cut_img)
            soLuongCoPhieu_1_5 = self.__parseOutput(soLuongCoPhieu_1_5)
            if len(soLuongCoPhieu_1_5) != 0 and re.match('\d{4,}', soLuongCoPhieu_1_5):
                pass
            else:
                soLuongCoPhieu_1_5 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(5)))
            bot = int(statistics.median(ycoordinateGroupDict.get(6)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_5 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_5 = self.__parseOutput(phiThucThu_3_5)
            if len(phiThucThu_3_5) != 0 and re.match('\d{4,}', phiThucThu_3_5):
                pass
            else:
                phiThucThu_3_5 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(8)))
            bot = int(statistics.median(ycoordinateGroupDict.get(9)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maChungKhoan_0_8 = None
            else:
                maChungKhoan_0_8 = self.__tesseractReadWord(cut_img)
                maChungKhoan_0_8 = self.__parseOutput(maChungKhoan_0_8)
            if maChungKhoan_0_8 and len(maChungKhoan_0_8) >= 3:
                pass
            else:
                maChungKhoan_0_8 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(8)))
            bot = int(statistics.median(ycoordinateGroupDict.get(9)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            soLuongCoPhieu_1_8 = self.__tesseractReadNumber(cut_img)
            soLuongCoPhieu_1_8 = self.__parseOutput(soLuongCoPhieu_1_8)
            if len(soLuongCoPhieu_1_8) != 0 and re.match('\d{4,}', soLuongCoPhieu_1_8):
                pass
            else:
                soLuongCoPhieu_1_8 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(8)))
            bot = int(statistics.median(ycoordinateGroupDict.get(9)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_8 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_8 = self.__parseOutput(phiThucThu_3_8)
            if len(phiThucThu_3_8) != 0 and re.match('\d{4,}', phiThucThu_3_8):
                pass
            else:
                phiThucThu_3_8 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(9)))
            bot = int(statistics.median(ycoordinateGroupDict.get(10)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maChungKhoan_0_9 = None
            else:
                maChungKhoan_0_9 = self.__tesseractReadWord(cut_img)
                maChungKhoan_0_9 = self.__parseOutput(maChungKhoan_0_9)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(9)))
            bot = int(statistics.median(ycoordinateGroupDict.get(10)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            soLuongCoPhieu_1_9 = self.__tesseractReadNumber(cut_img)
            soLuongCoPhieu_1_9 = self.__parseOutput(soLuongCoPhieu_1_9)
            if len(soLuongCoPhieu_1_9) != 0 and re.match('\d{4,}', soLuongCoPhieu_1_9):
                pass
            else:
                soLuongCoPhieu_1_9 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(9)))
            bot = int(statistics.median(ycoordinateGroupDict.get(10)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_9 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_9 = self.__parseOutput(phiThucThu_3_9)
            if len(phiThucThu_3_9) != 0 and re.match('\d{4,}', phiThucThu_3_9):
                pass
            else:
                phiThucThu_3_9 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(10)))
            bot = int(statistics.median(ycoordinateGroupDict.get(11)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_3_9 = self.__tesseractReadNumber(cut_img)
            tongCong_3_9 = self.__parseOutput(tongCong_3_9)
            if len(tongCong_3_9) != 0 and re.match('\d{4,}', tongCong_3_9):
                pass
            else:
                tongCong_3_9 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(11)))
            bot = int(statistics.median(ycoordinateGroupDict.get(12)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            chuyenNhuongQuyenMua_0_11 = self.__tesseractReadWord(cut_img)
            chuyenNhuongQuyenMua_0_11 = self.__parseOutput(chuyenNhuongQuyenMua_0_11)
            if len(chuyenNhuongQuyenMua_0_11) == 0:
                chuyenNhuongQuyenMua_0_11 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(13)))
            bot = int(statistics.median(ycoordinateGroupDict.get(14)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLanChuyen_1_13 = None
            else:
                soLanChuyen_1_13 = self.__tesseractReadNumber(cut_img)
                soLanChuyen_1_13 = self.__parseOutput(soLanChuyen_1_13)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(13)))
            bot = int(statistics.median(ycoordinateGroupDict.get(14)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_13 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_13 = self.__parseOutput(phiThucThu_3_13)
            if len(phiThucThu_3_13) != 0 and re.match('\d{4,}', phiThucThu_3_13):
                pass
            else:
                phiThucThu_3_13 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(14)))
            bot = int(statistics.median(ycoordinateGroupDict.get(15)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLanChuyen_1_14 = None
            else:
                soLanChuyen_1_14 = self.__tesseractReadNumber(cut_img)
                soLanChuyen_1_14 = self.__parseOutput(soLanChuyen_1_14)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(14)))
            bot = int(statistics.median(ycoordinateGroupDict.get(15)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_14 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_14 = self.__parseOutput(phiThucThu_3_14)
            if len(phiThucThu_3_14) != 0 and re.match('\d{4,}', phiThucThu_3_14):
                pass
            else:
                phiThucThu_3_14 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(15)))
            bot = int(statistics.median(ycoordinateGroupDict.get(16)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_3_15 = self.__tesseractReadNumber(cut_img)
            tongCong_3_15 = self.__parseOutput(tongCong_3_15)
            if len(tongCong_3_15) != 0 and re.match('\d{4,}', tongCong_3_15):
                pass
            else:
                tongCong_3_15 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(16)))
            bot = int(statistics.median(ycoordinateGroupDict.get(17)))
            left = x
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            thueChuyenNhuongQM_0_16 = self.__tesseractReadWord(cut_img)
            thueChuyenNhuongQM_0_16 = self.__parseOutput(thueChuyenNhuongQM_0_16)
            if len(thueChuyenNhuongQM_0_16) == 0:
                thueChuyenNhuongQM_0_16 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(18)))
            bot = int(statistics.median(ycoordinateGroupDict.get(19)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuong_0_18 = None
            else:
                soLuong_0_18 = self.__tesseractReadNumber(cut_img)
                soLuong_0_18 = self.__parseOutput(soLuong_0_18)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(18)))
            bot = int(statistics.median(ycoordinateGroupDict.get(19)))
            left = x + column1
            right = x + column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            giaThucThu_1_18 = self.__tesseractReadNumber(cut_img)
            giaThucThu_1_18 = self.__parseOutput(giaThucThu_1_18)
            if len(giaThucThu_1_18) != 0 and re.match('\d{4,}', giaThucThu_1_18):
                pass
            else:
                giaThucThu_1_18 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(18)))
            bot = int(statistics.median(ycoordinateGroupDict.get(19)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                thueSuat_2_18 = None
            else:
                thueSuat_2_18 = self.__tesseractReadNumber(cut_img)
                thueSuat_2_18 = self.__parseOutput(thueSuat_2_18)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(18)))
            bot = int(statistics.median(ycoordinateGroupDict.get(19)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_18 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_18 = self.__parseOutput(phiThucThu_3_18)
            if len(phiThucThu_3_18) != 0 and re.match('\d{4,}', phiThucThu_3_18):
                pass
            else:
                phiThucThu_3_18 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(21)))
            bot = int(statistics.median(ycoordinateGroupDict.get(22)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maChungKhoan_0_21 = None
            else:
                maChungKhoan_0_21 = self.__tesseractReadWord(cut_img)
                maChungKhoan_0_21 = self.__parseOutput(maChungKhoan_0_21)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(21)))
            bot = int(statistics.median(ycoordinateGroupDict.get(22)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLanRut_1_21 = None
            else:
                soLanRut_1_21 = self.__tesseractReadNumber(cut_img)
                soLanRut_1_21 = self.__parseOutput(soLanRut_1_21)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(21)))
            bot = int(statistics.median(ycoordinateGroupDict.get(22)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_21 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_21 = self.__parseOutput(phiThucThu_3_21)
            if len(phiThucThu_3_21) != 0 and re.match('\d{4,}', phiThucThu_3_21):
                pass
            else:
                phiThucThu_3_21 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(24)))
            bot = int(statistics.median(ycoordinateGroupDict.get(25)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maChungKhoan_0_24 = None
            else:
                maChungKhoan_0_24 = self.__tesseractReadWord(cut_img)
                maChungKhoan_0_24 = self.__parseOutput(maChungKhoan_0_24)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(24)))
            bot = int(statistics.median(ycoordinateGroupDict.get(25)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuongCoPhieu_1_24 = None
            else:
                soLuongCoPhieu_1_24 = self.__tesseractReadNumber(cut_img)
                soLuongCoPhieu_1_24 = self.__parseOutput(soLuongCoPhieu_1_24)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(24)))
            bot = int(statistics.median(ycoordinateGroupDict.get(25)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_24 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_24 = self.__parseOutput(phiThucThu_3_24)
            if len(phiThucThu_3_24) != 0 and re.match('\d{4,}', phiThucThu_3_24):
                pass
            else:
                phiThucThu_3_24 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(27)))
            bot = int(statistics.median(ycoordinateGroupDict.get(28)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maChungKhoan_0_27 = None
            else:
                maChungKhoan_0_27 = self.__tesseractReadWord(cut_img)
                maChungKhoan_0_27 = self.__parseOutput(maChungKhoan_0_27)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(27)))
            bot = int(statistics.median(ycoordinateGroupDict.get(28)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuongCoPhieu_1_27 = None
            else:
                soLuongCoPhieu_1_27 = self.__tesseractReadNumber(cut_img)
                soLuongCoPhieu_1_27 = self.__parseOutput(soLuongCoPhieu_1_27)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(27)))
            bot = int(statistics.median(ycoordinateGroupDict.get(28)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_27 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_27 = self.__parseOutput(phiThucThu_3_27)
            if len(phiThucThu_3_27) != 0 and re.match('\d{4,}', phiThucThu_3_27):
                pass
            else:
                phiThucThu_3_27 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(30)))
            bot = int(statistics.median(ycoordinateGroupDict.get(31)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuong_0_30 = None
            else:
                soLuong_0_30 = self.__tesseractReadNumber(cut_img)
                soLuong_0_30 = self.__parseOutput(soLuong_0_30)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(30)))
            bot = int(statistics.median(ycoordinateGroupDict.get(31)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            mucPhi_1_30 = self.__tesseractReadNumber(cut_img)
            mucPhi_1_30 = self.__parseOutput(mucPhi_1_30)
            if len(mucPhi_1_30) != 0 and re.match('\d{4,}', mucPhi_1_30):
                pass
            else:
                mucPhi_1_30 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(30)))
            bot = int(statistics.median(ycoordinateGroupDict.get(31)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soNgay_2_30 = None
            else:
                soNgay_2_30 = self.__tesseractReadNumber(cut_img)
                soNgay_2_30 = self.__parseOutput(soNgay_2_30)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(30)))
            bot = int(statistics.median(ycoordinateGroupDict.get(31)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_30 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_30 = self.__parseOutput(phiThucThu_3_30)
            if len(phiThucThu_3_30) != 0 and re.match('\d{4,}', phiThucThu_3_30):
                pass
            else:
                phiThucThu_3_30 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(33)))
            bot = int(statistics.median(ycoordinateGroupDict.get(34)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLan_0_33 = None
            else:
                soLan_0_33 = self.__tesseractReadNumber(cut_img)
                soLan_0_33 = self.__parseOutput(soLan_0_33)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(33)))
            bot = int(statistics.median(ycoordinateGroupDict.get(34)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            mucThuPhi_1_33 = self.__tesseractReadNumber(cut_img)
            mucThuPhi_1_33 = self.__parseOutput(mucThuPhi_1_33)
            if len(mucThuPhi_1_33) != 0 and re.match('\d{4,}', mucThuPhi_1_33):
                pass
            else:
                mucThuPhi_1_33 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(33)))
            bot = int(statistics.median(ycoordinateGroupDict.get(34)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                loai_2_33 = None
            else:
                loai_2_33 = self.__tesseractReadWord(cut_img)
                loai_2_33 = self.__parseOutput(loai_2_33)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(33)))
            bot = int(statistics.median(ycoordinateGroupDict.get(34)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_33 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_33 = self.__parseOutput(phiThucThu_3_33)
            if len(phiThucThu_3_33) != 0 and re.match('\d{4,}', phiThucThu_3_33):
                pass
            else:
                phiThucThu_3_33 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(34)))
            bot = int(statistics.median(ycoordinateGroupDict.get(35)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLan_0_34 = None
            else:
                soLan_0_34 = self.__tesseractReadNumber(cut_img)
                soLan_0_34 = self.__parseOutput(soLan_0_34)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(34)))
            bot = int(statistics.median(ycoordinateGroupDict.get(35)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            mucThuPhi_1_34 = self.__tesseractReadNumber(cut_img)
            mucThuPhi_1_34 = self.__parseOutput(mucThuPhi_1_34)
            if len(mucThuPhi_1_34) != 0 and re.match('\d{4,}', mucThuPhi_1_34):
                pass
            else:
                mucThuPhi_1_34 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(34)))
            bot = int(statistics.median(ycoordinateGroupDict.get(35)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                loai_2_34 = None
            else:
                loai_2_34 = self.__tesseractReadWord(cut_img)
                loai_2_34 = self.__parseOutput(loai_2_34)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(34)))
            bot = int(statistics.median(ycoordinateGroupDict.get(35)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_34 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_34 = self.__parseOutput(phiThucThu_3_34)
            if len(phiThucThu_3_34) != 0 and re.match('\d{4,}', phiThucThu_3_34):
                pass
            else:
                phiThucThu_3_34 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(35)))
            bot = int(statistics.median(ycoordinateGroupDict.get(36)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_3_35 = self.__tesseractReadNumber(cut_img)
            tongCong_3_35 = self.__parseOutput(tongCong_3_35)
            if len(tongCong_3_35) != 0 and re.match('\d{4,}', tongCong_3_35):
                pass
            else:
                tongCong_3_35 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(38)))
            bot = int(statistics.median(ycoordinateGroupDict.get(39)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            mucThuPhi_1_38 = self.__tesseractReadNumber(cut_img)
            mucThuPhi_1_38 = self.__parseOutput(mucThuPhi_1_38)
            if len(mucThuPhi_1_38) != 0 and re.match('\d{4,}', mucThuPhi_1_38):
                pass
            else:
                mucThuPhi_1_38 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(38)))
            bot = int(statistics.median(ycoordinateGroupDict.get(39)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_38 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_38 = self.__parseOutput(phiThucThu_3_38)
            if len(phiThucThu_3_38) != 0 and re.match('\d{4,}', phiThucThu_3_38):
                pass
            else:
                phiThucThu_3_38 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(39)))
            bot = int(statistics.median(ycoordinateGroupDict.get(40)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            mucThuPhi_1_39 = self.__tesseractReadNumber(cut_img)
            mucThuPhi_1_39 = self.__parseOutput(mucThuPhi_1_39)
            if len(mucThuPhi_1_39) != 0 and re.match('\d{4,}', mucThuPhi_1_39):
                pass
            else:
                mucThuPhi_1_39 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(39)))
            bot = int(statistics.median(ycoordinateGroupDict.get(40)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_39 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_39 = self.__parseOutput(phiThucThu_3_39)
            if len(phiThucThu_3_39) != 0 and re.match('\d{4,}', phiThucThu_3_39):
                pass
            else:
                phiThucThu_3_39 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(40)))
            bot = int(statistics.median(ycoordinateGroupDict.get(41)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            mucThuPhi_1_40 = self.__tesseractReadNumber(cut_img)
            mucThuPhi_1_40 = self.__parseOutput(mucThuPhi_1_40)
            if len(mucThuPhi_1_40) != 0 and re.match('\d{4,}', mucThuPhi_1_40):
                pass
            else:
                mucThuPhi_1_40 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(40)))
            bot = int(statistics.median(ycoordinateGroupDict.get(41)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_40 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_40 = self.__parseOutput(phiThucThu_3_40)
            if len(phiThucThu_3_40) != 0 and re.match('\d{4,}', phiThucThu_3_40):
                pass
            else:
                phiThucThu_3_40 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(41)))
            bot = int(statistics.median(ycoordinateGroupDict.get(42)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            mucThuPhi_1_41 = self.__tesseractReadNumber(cut_img)
            mucThuPhi_1_41 = self.__parseOutput(mucThuPhi_1_41)
            if len(mucThuPhi_1_41) != 0 and re.match('\d{4,}', mucThuPhi_1_41):
                pass
            else:
                mucThuPhi_1_41 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(41)))
            bot = int(statistics.median(ycoordinateGroupDict.get(42)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_41 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_41 = self.__parseOutput(phiThucThu_3_41)
            if len(phiThucThu_3_41) != 0 and re.match('\d{4,}', phiThucThu_3_41):
                pass
            else:
                phiThucThu_3_41 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(42)))
            bot = int(statistics.median(ycoordinateGroupDict.get(43)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_1_42 = self.__tesseractReadNumber(cut_img)
            tongCong_1_42 = self.__parseOutput(tongCong_1_42)
            if len(tongCong_1_42) != 0 and re.match('\d{4,}', tongCong_1_42):
                pass
            else:
                tongCong_1_42 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(42)))
            bot = int(statistics.median(ycoordinateGroupDict.get(43)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_3_42 = self.__tesseractReadNumber(cut_img)
            tongCong_3_42 = self.__parseOutput(tongCong_3_42)
            if len(tongCong_3_42) != 0 and re.match('\d{4,}', tongCong_3_42):
                pass
            else:
                tongCong_3_42 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(45)))
            bot = int(statistics.median(ycoordinateGroupDict.get(46)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                noiDung_0_45 = None
            else:
                noiDung_0_45 = self.__tesseractReadWord(cut_img)
                noiDung_0_45 = self.__parseOutput(noiDung_0_45)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(45)))
            bot = int(statistics.median(ycoordinateGroupDict.get(46)))
            left = x+column1
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            mucThuPhi_1_45 = self.__tesseractReadNumber(cut_img)
            mucThuPhi_1_45 = self.__parseOutput(mucThuPhi_1_45)
            if len(mucThuPhi_1_45) != 0 and re.match('\d{4,}', mucThuPhi_1_45):
                pass
            else:
                mucThuPhi_1_45 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(45)))
            bot = int(statistics.median(ycoordinateGroupDict.get(46)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_45 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_45 = self.__parseOutput(phiThucThu_3_45)
            if len(phiThucThu_3_45) != 0 and re.match('\d{4,}', phiThucThu_3_45):
                pass
            else:
                phiThucThu_3_45 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(46)))
            bot = int(statistics.median(ycoordinateGroupDict.get(47)))
            left = x+column1
            right = x+column3 - 200
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongPhiPhaiThu_2_46 = self.__tesseractReadNumber(cut_img)
            tongPhiPhaiThu_2_46 = self.__parseOutput(tongPhiPhaiThu_2_46)
            if len(tongPhiPhaiThu_2_46) != 0 and re.match('\d{4,}', tongPhiPhaiThu_2_46):
                pass
            else:
                tongPhiPhaiThu_2_46 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(47)))
            bot = int(statistics.median(ycoordinateGroupDict.get(48)))
            left = x+column1
            right = x+column3 - 200
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            bangChu_1_47 = self.__tesseractReadWord(cut_img)
            bangChu_1_47 = self.__parseOutput(bangChu_1_47)
            bangChu_1_47 = self.__parseOnlyWord(bangChu_1_47)
            if len(bangChu_1_47) == 0:
                bangChu_1_47 = None
            jsonDict = {'CloseAccount': {'SecuritiesCodeUnder': maChungKhoan_0_5,
                                         'NumberOfSharesUnder': soLuongCoPhieu_1_5,
                                         'ActualFeeUnder': phiThucThu_3_5,
                                         'SecuritiesCodeFrom': [maChungKhoan_0_8, maChungKhoan_0_9],
                                         'NumberOfSharesFrom': [soLuongCoPhieu_1_8, soLuongCoPhieu_1_9],
                                         'ActualFeeFrom': [phiThucThu_3_8, phiThucThu_3_9],
                                         'Total': tongCong_3_9},
                        'RightIssueTransfer': {'Header': chuyenNhuongQuyenMua_0_11,
                                               'SameCompanyTransferTimes': soLanChuyen_1_13,
                                               'SameCompanyActualFee': phiThucThu_3_13,
                                               'DifferentCompanyTransferTimes': soLanChuyen_1_14,
                                               'DifferentCompanyActualFee': phiThucThu_3_14,
                                               'Total': tongCong_3_15},
                        'TaxForRightIssueTransfer': {'Header': thueChuyenNhuongQM_0_16,
                                                     'Amount': soLuong_0_18,
                                                     'ActualPrice': giaThucThu_1_18,
                                                     'Tax': thueSuat_2_18,
                                                     'ActualFee': phiThucThu_3_18},
                        'WithdrawConsignedSecurities': {'SecuritiesCode': maChungKhoan_0_21,
                                                        'Times': soLanRut_1_21,
                                                        'ActualFee': phiThucThu_3_21},
                        'SellingTransferOutside': {'SecuritiesCode': maChungKhoan_0_24,
                                                   'NumberOfShares': soLuongCoPhieu_1_24,
                                                   'ActualFee': phiThucThu_3_24},
                        'TaxOfSellingTransferOutside': {'SecuritiesCode': maChungKhoan_0_27,
                                                        'NumberOfShares': soLuongCoPhieu_1_27,
                                                        'ActualFee': phiThucThu_3_27},
                        'DepositoryFee': {'Amount': soLuong_0_30,
                                          'Charge': mucPhi_1_30,
                                          'NumberOfDays': soNgay_2_30,
                                          'ActualFee': phiThucThu_3_30},
                        'BalanceConfirmation': {'Times': [soLan_0_33, soLan_0_34],
                                                'ChargeRate': [mucThuPhi_1_33, mucThuPhi_1_34],
                                                'Type': [loai_2_33, loai_2_34],
                                                'ActualFee': [phiThucThu_3_33, phiThucThu_3_34],
                                                'Total': tongCong_3_35},
                        'MortgageBlockUnblock': {'ChargeRateMortgageConfirmation': mucThuPhi_1_38,
                                                 'ActualFeeMortgageConfirmation': phiThucThu_3_38,
                                                 'ChargeRateMortgageManagement': mucThuPhi_1_39,
                                                 'ActualFeeMortgageManagement': phiThucThu_3_39,
                                                 'ChargeRateBlockSecurities': mucThuPhi_1_40,
                                                 'ActualFeeBlockSecurities': phiThucThu_3_40,
                                                 'ChargeRateUnblockSecurities': mucThuPhi_1_41,
                                                 'ActualFeeUnblockSecurities': phiThucThu_3_41,
                                                 'ChargeRateTotal': tongCong_1_42,
                                                 'ActualFeeTotal': tongCong_3_42},
                        'Other': {'TypeOfService': noiDung_0_45,
                                  'ChargeRate': mucThuPhi_1_45,
                                  'ActualFee': phiThucThu_3_45},
                        'TotalFees': {'Total': tongPhiPhaiThu_2_46,
                                      'InWord': bangChu_1_47}}
            df = pd.DataFrame(
                data=np.array([[imgCode, tenChiNhanh_3_0, Ngay_3_0, tenKhachHang_1_1, soTaiKhoan_3_1, json.dumps(jsonDict, ensure_ascii=False)]]),
                columns=['Code', 'TenChiNhanh', 'Ngay', 'TenKhachHang', 'SoTaiKhoan', 'NoiDung'])
            return df
        else:
            df = pd.DataFrame(columns=['Code', 'TenChiNhanh', 'Ngay', 'TenKhachHang', 'SoTaiKhoan', 'NoiDung'])
            return df

    # đọc file phái sinh
    def readPhaiSinh(self):
        imgCode = self.alignedImg.sum().sum().sum()
        xcoordinateGroupDict = self._specifyVerticalLongLines()
        ycoordinateGroupDict = self._specifyHorizontalLongLines(3, 36)
        if len(ycoordinateGroupDict) != 36:
            ycoordinateGroupDict = self._specifyHorizontalLongLines(0, 36)
        if len(ycoordinateGroupDict) == 36:
            self.alignedImg = self.__eraseBlackLines(self.alignedImg)
            # ----------------width--------------------------------------------------------------------
            firstVerticalLine = xcoordinateGroupDict[list(xcoordinateGroupDict.keys())[0]]
            x = int(statistics.median(firstVerticalLine))
            width = int(statistics.median(xcoordinateGroupDict[list(xcoordinateGroupDict.keys())[-1]])) - \
                    int(statistics.median(xcoordinateGroupDict.get(0)))
            column1 = int(width*0.329771555)
            column2 = int(width*0.565585851)
            column3 = int(width*0.786293294)
            column4 = int(width)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(0)))
            bot = int(statistics.median(ycoordinateGroupDict.get(1)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            regex = re.findall("(?<=:).*", self.__tesseractReadWord(cut_img))
            tenChiNhanh_3_0 = None
            Ngay_3_0 = None
            if len(regex) == 2:
                tenChiNhanh_3_0 = str(regex[0]).strip()
                Ngay_3_0 = str(regex[1]).strip()
                tenChiNhanh_3_0 = self.__parseOutput(tenChiNhanh_3_0)
                Ngay_3_0 = self.__parseOutput(Ngay_3_0)
                if len(tenChiNhanh_3_0) == 0:
                    tenChiNhanh_3_0 == None
                if re.match('\d\d\/\d\d\/\d\d\d\d', Ngay_3_0):
                    Ngay_3_0 = datetime.strptime(Ngay_3_0, '%m/%d/%y')
                else:
                    Ngay_3_0 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(1)))
            bot = int(statistics.median(ycoordinateGroupDict.get(2)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tenKhachHang_1_1 = self.__tesseractReadWord(cut_img)
            tenKhachHang_1_1 = self.__parseOutput(tenKhachHang_1_1)
            if len(tenKhachHang_1_1) == 0:
                tenKhachHang_1_1 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(1)))
            bot = int(statistics.median(ycoordinateGroupDict.get(2)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            soTaiKhoan_3_1 = self.__tesseractReadAccount(cut_img)
            soTaiKhoan_3_1 = self.__parseAccount(soTaiKhoan_3_1)
            if len(soTaiKhoan_3_1) == 0:
                soTaiKhoan_3_1 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(5)))
            bot = int(statistics.median(ycoordinateGroupDict.get(6)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maHopDong_0_4 = None
            else:
                maHopDong_0_4 = self.__tesseractReadWord(cut_img)
                maHopDong_0_4 = self.__parseAccount(maHopDong_0_4)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(5)))
            bot = int(statistics.median(ycoordinateGroupDict.get(6)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuongViThe_1_4 = None
            else:
                soLuongViThe_1_4 = self.__tesseractReadWordr(cut_img)
                soLuongViThe_1_4 = self.__parseAccount(soLuongViThe_1_4)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(5)))
            bot = int(statistics.median(ycoordinateGroupDict.get(6)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_4 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_4 = self.__parseOutput(phiThucThu_2_4)
            if len(phiThucThu_2_4) != 0 and re.match('\d{4,}', phiThucThu_2_4):
                pass
            else:
                phiThucThu_2_4 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(6)))
            bot = int(statistics.median(ycoordinateGroupDict.get(7)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maHopDong_0_5 = None
            else:
                maHopDong_0_5 = self.__tesseractReadWord(cut_img)
                maHopDong_0_5 = self.__parseAccount(maHopDong_0_5)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(6)))
            bot = int(statistics.median(ycoordinateGroupDict.get(7)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuongViThe_1_5 = None
            else:
                soLuongViThe_1_5 = self.__tesseractReadWord(cut_img)
                soLuongViThe_1_5 = self.__parseAccount(soLuongViThe_1_5)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(6)))
            bot = int(statistics.median(ycoordinateGroupDict.get(7)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_5 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_5 = self.__parseOutput(phiThucThu_2_5)
            if len(phiThucThu_2_5) != 0 and re.match('\d{4,}', phiThucThu_2_5):
                pass
            else:
                phiThucThu_2_5 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(7)))
            bot = int(statistics.median(ycoordinateGroupDict.get(8)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_2_6 = self.__tesseractReadNumber(cut_img)
            tongCong_2_6 = self.__parseOutput(tongCong_2_6)
            if len(tongCong_2_6) != 0 and re.match('\d{4,}', tongCong_2_6):
                pass
            else:
                tongCong_2_6 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(10)))
            bot = int(statistics.median(ycoordinateGroupDict.get(11)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maHopDong_0_8 = None
            else:
                maHopDong_0_8 = self.__tesseractReadWord(cut_img)
                maHopDong_0_8 = self.__parseAccount(maHopDong_0_8)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(10)))
            bot = int(statistics.median(ycoordinateGroupDict.get(11)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuongViThe_1_8 = None
            else:
                soLuongViThe_1_8 = self.__tesseractReadNumber(cut_img)
                soLuongViThe_1_8 = self.__parseAccount(soLuongViThe_1_8)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(10)))
            bot = int(statistics.median(ycoordinateGroupDict.get(11)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_8 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_8 = self.__parseOutput(phiThucThu_2_8)
            if len(phiThucThu_2_8) != 0 and re.match('\d{4,}', phiThucThu_2_8):
                pass
            else:
                phiThucThu_2_8 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(11)))
            bot = int(statistics.median(ycoordinateGroupDict.get(12)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maHopDong_0_9 = None
            else:
                maHopDong_0_9 = self.__tesseractReadWord(cut_img)
                maHopDong_0_9 = self.__parseAccount(maHopDong_0_9)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(11)))
            bot = int(statistics.median(ycoordinateGroupDict.get(12)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuongViThe_1_9 = None
            else:
                soLuongViThe_1_9 = self.__tesseractReadNumber(cut_img)
                soLuongViThe_1_9 = self.__parseAccount(soLuongViThe_1_9)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(11)))
            bot = int(statistics.median(ycoordinateGroupDict.get(12)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_9 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_9 = self.__parseOutput(phiThucThu_2_9)
            if len(phiThucThu_2_9) != 0 and re.match('\d{4,}', phiThucThu_2_9):
                pass
            else:
                phiThucThu_2_9 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(12)))
            bot = int(statistics.median(ycoordinateGroupDict.get(13)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_2_10 = self.__tesseractReadNumber(cut_img)
            tongCong_2_10 = self.__parseOutput(tongCong_2_10)
            if len(tongCong_2_10) != 0 and re.match('\d{4,}', tongCong_2_10):
                pass
            else:
                tongCong_2_10 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(15)))
            bot = int(statistics.median(ycoordinateGroupDict.get(16)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maHopDong_0_12 = None
            else:
                maHopDong_0_12 = self.__tesseractReadWord(cut_img)
                maHopDong_0_12 = self.__parseAccount(maHopDong_0_12)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(15)))
            bot = int(statistics.median(ycoordinateGroupDict.get(16)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLanBuTru_1_12 = None
            else:
                soLanBuTru_1_12 = self.__tesseractReadNumber(cut_img)
                soLanBuTru_1_12 = self.__parseAccount(soLanBuTru_1_12)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(15)))
            bot = int(statistics.median(ycoordinateGroupDict.get(16)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_12 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_12 = self.__parseOutput(phiThucThu_2_12)
            if len(phiThucThu_2_12) != 0 and re.match('\d{4,}', phiThucThu_2_12):
                pass
            else:
                phiThucThu_2_12 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(16)))
            bot = int(statistics.median(ycoordinateGroupDict.get(17)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                maHopDong_0_13 = None
            else:
                maHopDong_0_13 = self.__tesseractReadWord(cut_img)
                maHopDong_0_13 = self.__parseAccount(maHopDong_0_13)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(16)))
            bot = int(statistics.median(ycoordinateGroupDict.get(17)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLanBuTru_1_13 = None
            else:
                soLanBuTru_1_13 = self.__tesseractReadNumber(cut_img)
                soLanBuTru_1_13 = self.__parseAccount(soLanBuTru_1_13)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(16)))
            bot = int(statistics.median(ycoordinateGroupDict.get(17)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_13 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_13 = self.__parseOutput(phiThucThu_2_13)
            if len(phiThucThu_2_13) != 0 and re.match('\d{4,}', phiThucThu_2_13):
                pass
            else:
                phiThucThu_2_13 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(17)))
            bot = int(statistics.median(ycoordinateGroupDict.get(18)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_2_14 = self.__tesseractReadNumber(cut_img)
            tongCong_2_14 = self.__parseOutput(tongCong_2_14)
            if len(tongCong_2_14) != 0 and re.match('\d{4,}', tongCong_2_14):
                pass
            else:
                tongCong_2_14 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(20)))
            bot = int(statistics.median(ycoordinateGroupDict.get(21)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                giaTriLuyKe_0_16 = None
            else:
                giaTriLuyKe_0_16 = self.__tesseractReadNumber(cut_img)
                giaTriLuyKe_0_16 = self.__parseAccount(giaTriLuyKe_0_16)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(20)))
            bot = int(statistics.median(ycoordinateGroupDict.get(21)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                tyLePhanTram_1_16 = None
            else:
                tyLePhanTram_1_16 = self.__tesseractReadWord(cut_img)
                tyLePhanTram_1_16 = self.__parseAccount(tyLePhanTram_1_16)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(20)))
            bot = int(statistics.median(ycoordinateGroupDict.get(21)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_16 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_16 = self.__parseOutput(phiThucThu_2_16)
            if len(phiThucThu_2_16) != 0 and re.match('\d{4,}', phiThucThu_2_16):
                pass
            else:
                phiThucThu_2_16 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(21)))
            bot = int(statistics.median(ycoordinateGroupDict.get(22)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                giaTriLuyKe_0_17 = None
            else:
                giaTriLuyKe_0_17 = self.__tesseractReadWord(cut_img)
                giaTriLuyKe_0_17 = self.__parseAccount(giaTriLuyKe_0_17)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(21)))
            bot = int(statistics.median(ycoordinateGroupDict.get(22)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                tyLePhanTram_1_17 = None
            else:
                tyLePhanTram_1_17 = self.__tesseractReadWord(cut_img)
                tyLePhanTram_1_17 = self.__parseAccount(tyLePhanTram_1_17)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(21)))
            bot = int(statistics.median(ycoordinateGroupDict.get(22)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_17 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_17 = self.__parseOutput(phiThucThu_2_17)
            if len(phiThucThu_2_17) != 0 and re.match('\d{4,}', phiThucThu_2_17):
                pass
            else:
                phiThucThu_2_17 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(22)))
            bot = int(statistics.median(ycoordinateGroupDict.get(23)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_2_18 = self.__tesseractReadNumber(cut_img)
            tongCong_2_18 = self.__parseOutput(tongCong_2_18)
            if len(tongCong_2_18) != 0 and re.match('\d{4,}', tongCong_2_18):
                pass
            else:
                tongCong_2_18 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(25)))
            bot = int(statistics.median(ycoordinateGroupDict.get(26)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuongHopDong_0_20 = None
            else:
                soLuongHopDong_0_20 = self.__tesseractReadNumber(cut_img)
                soLuongHopDong_0_20 = self.__parseAccount(soLuongHopDong_0_20)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(25)))
            bot = int(statistics.median(ycoordinateGroupDict.get(26)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                mucPhi_1_20 = None
            else:
                mucPhi_1_20 = self.__tesseractReadNumber(cut_img)
                mucPhi_1_20 = self.__parseAccount(mucPhi_1_20)
            # -----------------------------------------------------------------------------------------.
            top = int(statistics.median(ycoordinateGroupDict.get(25)))
            bot = int(statistics.median(ycoordinateGroupDict.get(26)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_20 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_20 = self.__parseOutput(phiThucThu_2_20)
            if len(phiThucThu_2_20) != 0 and re.match('\d{4,}', phiThucThu_2_20):
                pass
            else:
                phiThucThu_2_20 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(26)))
            bot = int(statistics.median(ycoordinateGroupDict.get(27)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLuongHopDong_0_21 = None
            else:
                soLuongHopDong_0_21 = self.__tesseractReadNumber(cut_img)
                soLuongHopDong_0_21 = self.__parseAccount(soLuongHopDong_0_21)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(26)))
            bot = int(statistics.median(ycoordinateGroupDict.get(27)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                mucPhi_1_21 = None
            else:
                mucPhi_1_21 = self.__tesseractReadNumber(cut_img)
                mucPhi_1_21 = self.__parseAccount(mucPhi_1_21)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(26)))
            bot = int(statistics.median(ycoordinateGroupDict.get(27)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_2_21 = self.__tesseractReadNumber(cut_img)
            phiThucThu_2_21 = self.__parseOutput(phiThucThu_2_21)
            if len(phiThucThu_2_21) != 0 and re.match('\d{4,}', phiThucThu_2_21):
                pass
            else:
                phiThucThu_2_21 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(27)))
            bot = int(statistics.median(ycoordinateGroupDict.get(28)))
            left = x+column2
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_2_22 = self.__tesseractReadNumber(cut_img)
            tongCong_2_22 = self.__parseOutput(tongCong_2_22)
            if len(tongCong_2_22) != 0 and re.match('\d{4,}', tongCong_2_22):
                pass
            else:
                tongCong_2_22 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(30)))
            bot = int(statistics.median(ycoordinateGroupDict.get(31)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLan_0_24 = None
            else:
                soLan_0_24 = self.__tesseractReadNumber(cut_img)
                soLan_0_24 = self.__parseAccount(soLan_0_24)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(30)))
            bot = int(statistics.median(ycoordinateGroupDict.get(31)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                mucThuPhi_1_24 = None
            else:
                mucThuPhi_1_24 = self.__tesseractReadNumber(cut_img)
                mucThuPhi_1_24 = self.__parseAccount(mucThuPhi_1_24)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(30)))
            bot = int(statistics.median(ycoordinateGroupDict.get(31)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_24 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_24 = self.__parseOutput(phiThucThu_3_24)
            if len(phiThucThu_3_24) != 0 and re.match('\d{4,}', phiThucThu_3_24):
                pass
            else:
                phiThucThu_3_24 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(31)))
            bot = int(statistics.median(ycoordinateGroupDict.get(32)))
            left = x
            right = x+column1
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                soLan_0_25 = None
            else:
                soLan_0_25 = self.__tesseractReadNumber(cut_img)
                soLan_0_25 = self.__parseAccount(soLan_0_25)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(31)))
            bot = int(statistics.median(ycoordinateGroupDict.get(32)))
            left = x+column1
            right = x+column2
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            intensity = np.sum(cut_img, axis=1).sum(axis=1).sum()/(cut_img.shape[0]*cut_img.shape[1])
            if intensity > 740:
                mucThuPhi_1_25 = None
            else:
                mucThuPhi_1_25 = self.__tesseractReadNumber(cut_img)
                mucThuPhi_1_25 = self.__parseAccount(mucThuPhi_1_25)
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(31)))
            bot = int(statistics.median(ycoordinateGroupDict.get(32)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            phiThucThu_3_25 = self.__tesseractReadNumber(cut_img)
            phiThucThu_3_25 = self.__parseOutput(phiThucThu_3_25)
            if len(phiThucThu_3_25) != 0 and re.match('\d{4,}', phiThucThu_3_25):
                pass
            else:
                phiThucThu_3_25 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(32)))
            bot = int(statistics.median(ycoordinateGroupDict.get(33)))
            left = x+column3
            right = x+column4
            cut_img = self.alignedImg[top:bot, left:right]
            cut_img = self.__cutCell(cut_img)
            tongCong_3_26 = self.__tesseractReadNumber(cut_img)
            tongCong_3_26 = self.__parseOutput(tongCong_3_26)
            if len(tongCong_3_26) != 0 and re.match('\d{4,}', tongCong_3_26):
                pass
            else:
                tongCong_3_26 = None
            # -----------------------------------------------------------------------------------------
            top = int(statistics.median(ycoordinateGroupDict.get(33)))
            bot = int(statistics.median(ycoordinateGroupDict.get(34)))
            left = x
            right = x+column3
            cut_img = self.alignedImg[top:bot, left:right]
            regex = re.findall("(?<=:).*", self.__tesseractReadWord(cut_img))
            soTienBangSo_0_28 = None
            soTienBangChu_0_29 = None
            lyDo_0_30 = None
            if len(regex) == 4:
                soTienBangSo_0_28 = str(regex[1]).strip()
                soTienBangChu_0_29 = str(regex[2]).strip()
                lyDo_0_30 = str(regex[3]).strip()
                soTienBangSo_0_28 = self.__parseOutput(soTienBangSo_0_28)
                soTienBangChu_0_29 = self.__parseOutput(soTienBangChu_0_29)
                lyDo_0_30 = self.__parseOutput(lyDo_0_30)
            # -----------------------------------------------------------------------------------------
            jsonDict = {'CloseAccount': {'ContractCodeUnder': [maHopDong_0_4, maHopDong_0_5],
                                         'PositionVolumeUnder': [soLuongViThe_1_4, soLuongViThe_1_5],
                                         'ActualFeeUnder': [phiThucThu_2_4, phiThucThu_2_5],
                                         'TotalUnder': tongCong_2_6,
                                         'ContractCodeFrom': [maHopDong_0_8, maHopDong_0_9],
                                         'PositionVolumeFrom': [soLuongViThe_1_8, soLuongViThe_1_9],
                                         'ActualFeeFrom': [phiThucThu_2_8, phiThucThu_2_9],
                                         'TotalFrom': tongCong_2_10},
                        'PositionClearing': {'ContractCode': [maHopDong_0_12, maHopDong_0_13],
                                             'ClearNo': [soLanBuTru_1_12, soLanBuTru_1_13],
                                             'ActualFee': [phiThucThu_2_12, phiThucThu_2_13],
                                             'Total': tongCong_2_14},
                        'CollateralManagementFee': {'AccumulatedValue': [giaTriLuyKe_0_16, giaTriLuyKe_0_17],
                                                    'Percentage': [tyLePhanTram_1_16, tyLePhanTram_1_17],
                                                    'ActualFee': [phiThucThu_2_16, phiThucThu_2_17],
                                                    'Total': tongCong_2_18},
                        'PositionManagementFee': {'ContractVolume': [soLuongHopDong_0_20, soLuongHopDong_0_21],
                                                  'Charges': [mucPhi_1_20, mucPhi_1_21],
                                                  'ActualFee': [phiThucThu_2_20, phiThucThu_2_21],
                                                  'Total': tongCong_2_22},
                        'StockBalanceConfirmation': {'TheNumberOfTime': [soLan_0_24, soLan_0_25],
                                                     'Charges': [mucThuPhi_1_24, mucThuPhi_1_25],
                                                     'ActualFee': [phiThucThu_3_24, phiThucThu_3_25],
                                                     'Total': tongCong_3_26},
                        'AmountInFigures': soTienBangSo_0_28,
                        'AmountInWords': soTienBangChu_0_29,
                        'Reason': lyDo_0_30
                        }
            df = pd.DataFrame(
                data=np.array([[imgCode, tenChiNhanh_3_0, Ngay_3_0, tenKhachHang_1_1, soTaiKhoan_3_1, json.dumps(jsonDict, ensure_ascii=False)]]),
                columns=['Code', 'TenChiNhanh', 'Ngay', 'TenKhachHang', 'SoTaiKhoan', 'NoiDung'])
            return df
        else:
            df = pd.DataFrame(columns=['Code', 'TenChiNhanh', 'Ngay', 'TenKhachHang', 'SoTaiKhoan', 'NoiDung'])
            return df


