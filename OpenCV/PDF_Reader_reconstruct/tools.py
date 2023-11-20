import numpy as np
import cv2
import math
import pandas as pd
from datawarehouse import BATCHINSERT
from request import connect_DWH_AppData


class Tools:

    # insert dữ liệu đọc được vào data warehouse
    @staticmethod
    def insertToDatabase(df):
        existing = pd.read_sql('SELECT * FROM [SS.PhieuThuPhi]', connect_DWH_AppData)
        df['Code'] = df['Code'].astype(np.int64)
        df_merged = df[['Code', 'SoTaiKhoan']].merge(
            existing[['Code', 'SoTaiKhoan', 'ID']],
            on=['Code', 'SoTaiKhoan'],
            how='left',
            indicator=True
        )

        tookRows = df_merged[df_merged['_merge'] == 'left_only'].index.tolist()
        if len(tookRows) != 0:
            BATCHINSERT(
                conn=connect_DWH_AppData,
                df=df.iloc[tookRows],
                table='SS.PhieuThuPhi'
            )
        else:
            pass
        return len(tookRows)

    # tìm ra trong file pdf trang nào là trang cần đọc
    @staticmethod
    def detectPage(data):
        indexList = []
        for i in range(0, len(data)):
            horizonLineCoordinates = Tools.detectHorizontalShortLines(np.array(data[i]))
            indexList.append(len(horizonLineCoordinates))
        return indexList.index(max(indexList)), max(indexList)

    # group 1 sorted number list thành nhiều nhóm
    @staticmethod
    def grouper(iterable: list, length):
        prev = None
        group = []
        for item in iterable:
            if prev is None or item - prev <= 30:
                group.append(item)
            else:
                if len(group) > length:
                    yield group
                group = [item]
            prev = item
        if len(group) > length:
            yield group

    # tính góc tạo ra bởi 3 điểm
    @staticmethod
    def calculateAngle(x1, y1, x2, y2):
        a = np.array([x2, y2])
        b = np.array([x1, y1])
        c = np.array([x2, y1])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    # xoay hình
    @staticmethod
    def rotate(image, angle, center=None, scale=1.0):
        (h, w) = image.shape[:2]
        if center is None:
            center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, scale)
        rotated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_CONSTANT,
                                 borderValue=(255, 255, 255))
        return rotated

    # xác định đường houghlines dọc
    @staticmethod
    def detectVerticalShortLines(img_arr, minLineLength=25, maxLineGap=1):
        gray = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        lines = cv2.HoughLinesP(edges, 1, math.pi / 2, 1, None, minLineLength, maxLineGap)
        verticalLineCoordinates = []
        for line in lines:
            for i in line:
                pt1 = (i[0], i[1])
                pt2 = (i[2], i[3])
                if abs(i[0] - i[2]) <= 3:
                    verticalLineCoordinates.append([i[2], i[3]])
                    # cv2.line(img_arr, pt1, pt2, (0, 255, 0), 3)
        # cv2.imwrite("houghlines_vertical.jpg", img_arr)
        return verticalLineCoordinates

    # xác định đường houglines ngang
    @staticmethod
    def detectHorizontalShortLines(img_arr, minLineLength=25, maxLineGap=1):
        gray = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        lines = cv2.HoughLinesP(edges, 1, math.pi / 2, 1, None, minLineLength, maxLineGap)
        horizonLineCoordinates = []
        if lines is not None:
            for line in lines:
                for i in line:
                    pt1 = (i[0], i[1])
                    pt2 = (i[2], i[3])
                    if abs(i[1] - i[3]) <= 20:
                        horizonLineCoordinates.append([i[2], i[3]])
                        cv2.line(img_arr, pt1, pt2, (0, 255, 0), 3)
            # cv2.imwrite("houghlines_horizon.jpg", img_arr)
        return horizonLineCoordinates
