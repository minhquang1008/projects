import numpy as np
import pandas as pd
import cv2
import statistics
from detect_lines import LineSpecify
from tools import Tools
from itertools import chain


class SignatureValidation(LineSpecify):
    def __init__(self) -> None:
        super().__init__()

    @property
    def alignedImg(self) -> pd.DataFrame:
        return self._alignedImg

    @alignedImg.setter
    def alignedImg(self, alignedImg) -> None:
        self._alignedImg = alignedImg

    # tìm điểm bên trái dưới cùng
    def __specifyBotLeftPoints(self):
        linesExtracted = self._linesExtract(self.alignedImg.copy(), 4)
        horizonLineCoordinates = Tools.detectHorizontalShortLines(linesExtracted, 50, 1)
        horizonLineYCoordinates = list(chain.from_iterable(np.hsplit(np.array(horizonLineCoordinates), 2)[1]))
        horizonLineYCoordinates.sort()
        ycoordinateGroupDict = dict(enumerate(Tools.grouper(horizonLineYCoordinates, 3), 0))
        xcoordinateGroupDict = self._specifyVerticalLongLines()
        lastRow = ycoordinateGroupDict[list(ycoordinateGroupDict.keys())[-1]]
        ycoordBotLeftPoint = int(statistics.median(lastRow))
        firstVerticalLine = xcoordinateGroupDict[list(xcoordinateGroupDict.keys())[0]]
        xcoordBotLeftPoint = int(statistics.median(firstVerticalLine))
        return xcoordBotLeftPoint, ycoordBotLeftPoint

    # cắt phần chữ kí của phiếu cơ sở
    def __splitSignatureCoSo(self):
        x, y = self.__specifyBotLeftPoints()
        customerSignature = self.alignedImg[y-477:y, x:x+894]
        employeeSignature = self.alignedImg[y-477:y, x+894:x+1128]
        supervisorSignature = self.alignedImg[y-477:y, x+1128:x+1461]
        headSignature = self.alignedImg[y-477:y, x+1461:x+2200]
        return customerSignature, employeeSignature, supervisorSignature, headSignature

    # cắt phần chữ kí của phiếu phái sinh
    def __splitSignaturePhaiSinh(self):
        x, y = self.__specifyBotLeftPoints()
        customerSignature = self.alignedImg[y-440:y, x:x+606]
        employeeSignature = self.alignedImg[y-440:y, x+606:x+1538]
        supervisorSignature = self.alignedImg[y-440:y, x+1538:x+2131]
        headSignature = self.alignedImg[y-440:y, x+2131:x+2707]
        return customerSignature, employeeSignature, supervisorSignature, headSignature

    # xác định có hình tròn của con dấu hay không
    def __specifyStamps(self):
        gray_image = cv2.cvtColor(self.alignedImg, cv2.COLOR_BGR2GRAY)
        output = self.alignedImg.copy()
        circles = cv2.HoughCircles(gray_image, cv2.HOUGH_GRADIENT, 1, 50, param1=100, param2=80, minRadius=200,
                                   maxRadius=400)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            if len(circles) >= 1:
                for (x, y, r) in circles:
                    cv2.circle(output, (x, y), r, (0, 255, 0), 2)
                    return True

    # bỏ màu đỏ
    @staticmethod
    def __eliminateRed(imgHasRed):
        imgHasRed[:, :, 0] = np.zeros([imgHasRed.shape[0], imgHasRed.shape[1]])
        return imgHasRed

    # xác định 1 hình có vết mực xanh hay không
    def __specifySignature(self, imgHasSignature):
        eliminatedRed = self.__eliminateRed(imgHasSignature)
        intensityGreen = eliminatedRed[:, :, 1].sum(axis=1).sum()
        intensityBlue = eliminatedRed[:, :, 2].sum(axis=1).sum()
        if intensityBlue/intensityGreen >= 1.002:
            return True

    # validate con dấu và chữ kí phiếu cơ sở
    def validateStampAndSignatureCoSo(self):
        dataList = list()
        for i in self.__splitSignatureCoSo():
            if not self.__specifySignature(i):
                dataList.append(0)
            else:
                dataList.append(1)
        if self.__specifyStamps():
            dataList.append(1)
        else:
            dataList.append(0)
        df = pd.DataFrame(
            data=np.array([dataList]),
            columns=[
                'ChuKyKhachHang',
                'ChuKyNhanVien',
                'ChuKyGiamSat',
                'ChuKyTruongChiNhanh',
                'ConDau'
            ]
        )
        return df

    # validate con dấu và chữ kí phiếu phái sinh
    def validateStampAndSignaturePhaiSinh(self):
        dataList = list()
        for i in self.__splitSignaturePhaiSinh():
            if not self.__specifySignature(i):
                dataList.append(0)
            else:
                dataList.append(1)
        if self.__specifyStamps():
            dataList.append(1)
        else:
            dataList.append(0)
        df = pd.DataFrame(
            data=np.array([dataList]),
            columns=[
                'ChuKyKhachHang',
                'ChuKyNhanVien',
                'ChuKyGiamSat',
                'ChuKyTruongChiNhanh',
                'ConDau'
            ]
        )
        return df

