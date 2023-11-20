import numpy as np
import pandas as pd
from itertools import chain
from tools import Tools
import cv2


class LineSpecify:
    def __init__(self) -> None:
        self._alignedImg = None

    @property
    def alignedImg(self) -> pd.DataFrame:
        return self._alignedImg

    @alignedImg.setter
    def alignedImg(self, alignedImg) -> None:
        self._alignedImg = alignedImg

    # tạo ra 1 hình chỉ có đường kẻ ngang đường kẻ dọc
    @staticmethod
    def _linesExtract(img, kernel_len_coefficient=6):
        kernel = np.ones((2, 3), np.uint8)
        img = cv2.erode(img, kernel, iterations=4)
        thresh, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
        img_bin = 255 - img_bin
        kernel_len = np.array(img).shape[1] // 100
        ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len*3))
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len * kernel_len_coefficient, 1))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        image_1 = cv2.erode(img_bin, ver_kernel, iterations=3)
        vertical_lines = cv2.dilate(image_1, ver_kernel, iterations=3)
        image_2 = cv2.erode(img_bin, hor_kernel, iterations=3)
        horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=3)
        img_vh = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
        img_vh = cv2.erode(~img_vh, kernel, iterations=2)
        thresh, img_vh = cv2.threshold(img_vh, 128, 255, cv2.THRESH_BINARY)
        # cv2.imwrite("img_vh.jpg", img_vh)
        return img_vh

    # xác định số lượng đường kẻ đọc
    def _specifyVerticalLongLines(self):
        linesExtracted = self._linesExtract(self.alignedImg.copy())
        verticalLineCoordinates = Tools.detectVerticalShortLines(linesExtracted)
        verticalXCoordinates = list(chain.from_iterable(np.hsplit(np.array(verticalLineCoordinates), 2)[0]))
        verticalXCoordinates.sort()
        xcoordinateGroupDict = dict(enumerate(Tools.grouper(verticalXCoordinates, 3), 0))
        return xcoordinateGroupDict

    # xác định số lượng đường kẻ ngang
    def _specifyHorizontalLongLines(self, number_of_elements, number_of_lines=51):
        kernel_len_coefficient = 6
        while True:
            if kernel_len_coefficient > 1:
                linesExtracted = self._linesExtract(self.alignedImg.copy(), kernel_len_coefficient)
                horizonLineCoordinates = Tools.detectHorizontalShortLines(linesExtracted, 50, 1)
                horizonLineYCoordinates = list(chain.from_iterable(np.hsplit(np.array(horizonLineCoordinates), 2)[1]))
                horizonLineYCoordinates.sort()
                ycoordinateGroupDict = dict(enumerate(Tools.grouper(horizonLineYCoordinates, number_of_elements), 0))
                if len(ycoordinateGroupDict) >= number_of_lines or kernel_len_coefficient == 1:
                    return ycoordinateGroupDict
                else:
                    kernel_len_coefficient = kernel_len_coefficient - 1

