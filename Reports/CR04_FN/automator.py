from automation.flex_gui.base import Flex
import pyperclip
import cv2
import numpy as np
import time
from pywinauto.application import Application


class VRM6630(Flex):

    def __init__(self, username, password):
        super().__init__()
        self.start(existing=False)
        self.login(username, password)
        self.insertFuncCode('VRM6630')
        self.funcWindow = self.app.window(auto_id='frmSearch')
        self.insertWindow = self.app.window(auto_id='frmTransact')

    def __insertFromKeyboard(self, textBox, textString: str):
        Flex.setFocus(self.mainWindow)
        textBox.click_input()
        textBox.type_keys('^a{DELETE}')
        textBox.type_keys(textString, with_spaces=True)

    def __insertFromClipboard(self, textBox, textString: str):
        Flex.setFocus(self.mainWindow)
        textBox.click_input()
        pyperclip.copy(textString)
        textBox.type_keys('^a{DELETE}')
        textBox.type_keys('^v')

    def __takeFlexScreenshot(self, window):
        Flex.setFocus(self.mainWindow)
        return cv2.cvtColor(np.array(window.capture_as_image()), cv2.COLOR_RGB2BGR)

    @staticmethod
    def __linesExtract(img):
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.erode(img, kernel, iterations=3)
        thresh, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
        img_bin = 255 - img_bin
        kernel_len = np.array(img).shape[1] // 100
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
        image = cv2.erode(img_bin, hor_kernel, iterations=3)
        horizontal_lines = cv2.dilate(image, hor_kernel, iterations=3)
        gray_image = cv2.cvtColor(horizontal_lines, cv2.COLOR_BGR2GRAY)
        thresh, img_vh = cv2.threshold(gray_image, 250, 255, cv2.THRESH_BINARY)
        return img_vh

    @staticmethod
    def __checkIfAnyRows(binaryRecordImage):
        flag = 0
        sumIntensity = binaryRecordImage.sum(axis=1).nonzero()
        minLocArray = np.asarray(sumIntensity)[0][1:-1]
        if len(minLocArray) > 0:
            flag = 1
        return flag

    @staticmethod
    def __findFirstLineCoords(containingImage):
        templateImage = cv2.imread(fr"findit.png")
        containingImage = np.array(containingImage)
        templateImage = np.array(templateImage)
        matchResult = cv2.matchTemplate(containingImage, templateImage, cv2.TM_CCOEFF)
        _, _, _, topLeft = cv2.minMaxLoc(matchResult)
        midPoint = (topLeft[0], topLeft[1] + templateImage.shape[0] + 8)
        return midPoint

    def __clickThucHien(self):
        Flex.setFocus(self.funcWindow)
        while True:  # đợi maximize window xong
            if self.funcWindow.rectangle() == self.mainWindow.rectangle():
                break
            time.sleep(0.5)
        actionWindow = self.funcWindow.child_window(title='SMS')
        actionImage = self.__takeFlexScreenshot(actionWindow)
        actionImage = actionImage[:, :-10, :]
        unique, count = np.unique(actionImage, return_counts=True, axis=1)
        mostFrequentColumn = unique[:, np.argmax(count), :]
        columnMask = ~(actionImage == mostFrequentColumn[:, np.newaxis, :]).all(axis=(0, 2))
        lastColumn = np.argwhere(columnMask).max()
        croppedImage = actionImage[:, :lastColumn, :]
        midPoint = croppedImage.shape[1] // 2, croppedImage.shape[0] // 2
        actionWindow.click_input(coords=midPoint, absolute=False)
        self.insertWindow.wait('exists', timeout=30)

    def __clickSuccess(self):
        successWindow = self.app.window(title='Nhập giao dịch', class_name="#32770")
        successWindow.wait('exists', timeout=45)
        okButton = successWindow.child_window(title='OK', class_name="Button")
        okButton.click_input()

    def run(self):
        Flex.setFocus(self.funcWindow)
        dateBox = self.funcWindow.child_window(auto_id='txtValue')
        self.__insertFromKeyboard(dateBox, '2023')
        dateBox.type_keys('^a{LEFT}')
        dateBox.type_keys('06', with_spaces=True)
        dateBox.type_keys('^a{LEFT}')
        dateBox.type_keys('28', with_spaces=True)
        addButton = self.funcWindow.child_window(auto_id='btnAdd')
        searchButton = self.funcWindow.child_window(auto_id='btnSearch')
        searchResult = self.funcWindow.child_window(auto_id='grbSearchResult')
        removeButton = self.funcWindow.child_window(auto_id='btnRemoveAll')
        removeButton.click_input()
        addButton.click_input()
        while True:
            searchButton.click_input()
            picture = self.__takeFlexScreenshot(searchResult)
            screenPicture = self.__takeFlexScreenshot(self.funcWindow)
            lineExtration = self.__linesExtract(picture)
            midPoint = self.__findFirstLineCoords(screenPicture)
            if self.__checkIfAnyRows(lineExtration) == 1:
                self.funcWindow.click_input(coords=midPoint, absolute=False)
                self.__clickThucHien()
                trangThaiDuyet = self.insertWindow.child_window(auto_id='mskData32')
                self.__insertFromClipboard(trangThaiDuyet, 'Duyệt')
                self.insertWindow.child_window(auto_id='btnOK').click_input()
                time.sleep(1)
                self.__clickSuccess()
                time.sleep(1)
                self.insertWindow.child_window(auto_id='btnOK').click_input()
            else:
                time.sleep(4)
            time.sleep(1)


if __name__ == "__main__":
    obj = VRM6630('admin', '123456')
    obj.run()

