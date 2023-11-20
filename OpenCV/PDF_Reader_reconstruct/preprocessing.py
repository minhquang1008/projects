import numpy as np
from itertools import chain
from tools import Tools
import cv2
import statistics


class Alignment:

    def __init__(self, inputFile):
        self.__inputFile = inputFile

    # xóa các đường kẻ màu do lỗi máy scan tạo ra để tránh nhiễu
    @staticmethod
    def __eliminateNoise(noiseImg):
        rightEdge = noiseImg[0:noiseImg.shape[0], noiseImg.shape[1] - 101:noiseImg.shape[1] - 100]
        leftEdge = noiseImg[0:noiseImg.shape[0], 100:101]
        lst1 = np.sum(rightEdge, axis=1).sum(axis=1).tolist()
        lst2 = np.sum(leftEdge, axis=1).sum(axis=1).tolist()
        indexList1 = [i for i in range(len(lst1)) if lst1[i] < 700]
        indexList2 = [i for i in range(len(lst2)) if lst1[i] < 700]
        linesList = [i for i in indexList1 if i in indexList2]
        if linesList:
            clusteringLines = dict(enumerate(Tools.grouper(linesList, 0), 0))
            for line in clusteringLines.keys():
                top = min(clusteringLines.get(line))-2
                bot = max(clusteringLines.get(line))+2
                left = 0
                right = noiseImg.shape[1]
                cutNoise = noiseImg[top:bot, left:right]
                for data in cutNoise:
                    for pixel in data:
                        if pixel[0] > 40 and pixel[1] > 40 and pixel[2] > 40:
                            pixel[0] = 255
                            pixel[1] = 255
                            pixel[2] = 255

    @staticmethod
    def __linesExtract(img):
        kernel = np.ones((2, 3), np.uint8)
        img = cv2.erode(img, kernel, iterations=4)
        # img = cv2.dilate(img, kernel, iterations=2)
        thresh, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
        img_bin = 255 - img_bin
        kernel_len = np.array(img).shape[1] // 100
        ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len*3))
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len * 6, 1))
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

    # xoay hình
    def rotateSheet(self):
        img = np.array(self.__inputFile)
        self.__eliminateNoise(img)
        result = img.copy()
        img[0:img.shape[0], img.shape[1] - 100:img.shape[1]] = (255, 255, 255)
        img[0:img.shape[0], 0:100] = (255, 255, 255)
        img = self.__linesExtract(img)
        horizontalLineCoordinates = Tools.detectHorizontalShortLines(img, 50, 1)
        horizontalLineYCoordinates = list(chain.from_iterable(np.hsplit(np.array(horizontalLineCoordinates), 2)[1]))
        horizontalLineYCoordinates.sort()
        coordinateGroupDict = dict(enumerate(Tools.grouper(horizontalLineYCoordinates, 1), 0))
        # ----------------------
        linesExtracted = self.__linesExtract(img)
        verticalLineCoordinates = Tools.detectVerticalShortLines(linesExtracted)
        verticalXCoordinates = list(chain.from_iterable(np.hsplit(np.array(verticalLineCoordinates), 2)[0]))
        verticalXCoordinates.sort()
        xcoordinateGroupDict = dict(enumerate(Tools.grouper(verticalXCoordinates, 3), 0))
        # ----------------------
        firstVerticalLine = xcoordinateGroupDict[list(xcoordinateGroupDict.keys())[0]]
        lastVerticalLine = xcoordinateGroupDict[list(xcoordinateGroupDict.keys())[-1]]
        xcoordBotLeftPoint = int(statistics.median(firstVerticalLine))
        xcoordBotRightPoint = int(statistics.median(lastVerticalLine))
        max_ycoord = max(coordinateGroupDict.get(0))
        min_ycoord = min(coordinateGroupDict.get(0))
        max_coord = None
        min_coord = None
        if (max_ycoord - min_ycoord) > 10:
            for i in horizontalLineCoordinates:
                if i[1] == max_ycoord:
                    max_coord = i.copy()
                elif i[1] == min_ycoord:
                    min_coord = i.copy()
            ang = Tools.calculateAngle(xcoordBotLeftPoint, min_coord[1], xcoordBotRightPoint, max_coord[1])
            if max_coord[0] > min_coord[0]:
                return Tools.rotate(result, angle=ang)
            elif max_coord[0] < min_coord[0]:
                return Tools.rotate(result, angle=-ang)
        return result

