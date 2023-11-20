import datetime as dt
from abc import ABC, abstractmethod
import time
import re
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from log import Logger
from request import connect_DWH_ThiTruong
from datawarehouse import SEQUENTIALINSERT


logger = Logger(tableName='SS.TINDAUGIA')


class _Crawler(ABC):

    @property
    @abstractmethod
    def url(self):
        pass

    @property
    @abstractmethod
    def fromTime(self) -> dt.datetime:
        pass

    @fromTime.setter
    @abstractmethod
    def fromTime(self, value: dt.datetime) -> None:
        pass

    @property
    @abstractmethod
    def toTime(self) -> dt.datetime:
        pass

    @toTime.setter
    @abstractmethod
    def toTime(self, value: dt.datetime) -> None:
        pass

    @abstractmethod
    def crawl(self) -> dt.datetime:
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__


class _PopUpHNX:

    def __init__(self, articleElement: WebElement) -> None:
        self.__articleElement = articleElement
        self.__popupElements = None
        self.__content = None

    @property
    def content(self) -> str:
        resultDict = {}
        popupElement = self._popupElements.pop()
        # Nội dung
        xpath = "//*[@class='Box-Noidung']"
        contentElement = popupElement.find_element(By.XPATH,xpath)
        resultDict.update({'noidung': contentElement.text})
        # File đính kèm
        xpath = '//p/a[@href!="" and text()!=""]'
        attachmentElements = popupElement.find_elements(By.XPATH,xpath)
        processAttachment = lambda x: {'file': x.text, 'url': x.get_attribute('href')}
        resultDict.update({'filedinhkem': list(map(processAttachment, attachmentElements))})
        self.__content = json.dumps(resultDict)
        return self.__content

    @property
    def _popupElements(self) -> list: 
        """
        __len__() either 0 or 1
        """
        xpath = "//*[@class='divPopupHeader']"
        self.__popupElements = self.__articleElement.parent.find_elements(By.XPATH, xpath)
        return self.__popupElements

    def __enter__(self) -> None:
        # click vào article đến khi hiện lên popup
        while not self._popupElements:
            self.__articleElement.click()
            time.sleep(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # click đóng popup đến khi mất popup
        while self._popupElements:
            popupElement = self._popupElements.pop()
            xpath = "//*[@class='clsBtnClosePopup']"
            closeButton = popupElement.find_element(By.XPATH, xpath)
            closeButton.click()
            time.sleep(1)


class HNX(_Crawler):

    def __init__(self) -> None:
        self.__fromTime = None
        self.__toTime = None
        self.__maxPages = None
        self.__articleElements = None
        self.__timeElements = None
        self.__url = 'https://www.hnx.vn/vi-vn/dau-gia/dau-gia-tin-cong-bo.html'
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')
        self.wait = WebDriverWait(self.driver, timeout=30, poll_frequency=1)
        self.driver.get(self.__url)
        self.driver.maximize_window()

    @property
    def url(self):
        return self.__url

    @property
    def fromTime(self) -> dt.datetime:
        if self.__fromTime:
            return self.__fromTime
        raise AttributeError('attribute fromTime not set')

    @fromTime.setter
    @logger.log
    def fromTime(self, value: dt.datetime) -> None:
        self.__maxPages = None
        self.__fromTime = value

    @property
    def toTime(self) -> dt.datetime:
        if self.__toTime:
            return self.__toTime
        raise AttributeError('attribute toTime not set')

    @toTime.setter
    @logger.log
    def toTime(self, value: dt.datetime) -> None:
        self.__maxPages = None
        self.__toTime = value
    
    @logger.log
    def crawl(self) -> None:
        # không craw lại các tin đã có trong database
        existingRecords = pd.read_sql(
            sql = f"""
                SELECT 
                    [ThoiGian], [TieuDe]
                FROM [TinDauGia]
                WHERE [SanGiaoDich] = '{type(self).__name__}'
            """,
            con = connect_DWH_ThiTruong,
            parse_dates = ['ThoiGian']
        )
        for page in range(1, self._maxPages + 1):
            # click chọn trang
            if page >= 2:
                self.__goToPage(page)
            # crawl từng tin
            for timeElement, articleElement in zip(
                self._timeElements,
                self._articleElements
            ):
                articleTime = type(self).__parseTime(timeElement.text)
                articleTitle = articleElement.text
                maskTime = existingRecords['ThoiGian'] == articleTime
                maskTitle = existingRecords['TieuDe'] == articleTitle
                # nếu tin đã có trong database -> bỏ qua
                if not existingRecords.loc[maskTime & maskTitle].empty:
                    continue
                # nếu tin chưa có trong database -> crawl
                with _PopUpHNX(articleElement) as popup:
                    data = {
                        'ThoiGian':  articleTime,
                        'SanGiaoDich': type(self).__name__,
                        'TieuDe': articleTitle,
                        'NoiDung': popup.content, 
                    }
                    SEQUENTIALINSERT(
                        connect_DWH_ThiTruong, 
                        'TinDauGia', 
                        pd.DataFrame(data, index=[0])
                    )

    @property
    def _maxPages(self) -> int:
        if isinstance(self.__maxPages, int):
            return self.__maxPages # return cached value 
        # truyền ngày
        self.__sendFromDate()
        self.__sendToDate()
        self.__clickSearch()
        maxRecordsPerPage = self.__selectMaxRecordsPerPage()
        time.sleep(3) # chờ load dữ liệu
        # lấy max page
        xpath = '//*[@id="d_total_rec"]'
        totalRecordsElement = self.wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
        totalRecordsMatch = re.search(r'\d+',totalRecordsElement.text)
        if totalRecordsMatch:
            totalRecords = int(totalRecordsMatch.group())
            self.__maxPages = (totalRecords // maxRecordsPerPage) + (totalRecords % maxRecordsPerPage > 0) 
        else:  # hiện "Không tìm thấy dữ liệu"
            self.__maxPages = 0
        return self.__maxPages
    
    @property
    def _articleElements(self) -> list:
        xpath = "//tbody/tr[*]/td/a[@class='hrefViewDetail']"
        self.__articleElements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,xpath)))
        return self.__articleElements

    @property
    def _timeElements(self) -> list:
        xpath = "//tbody/tr[*]/td[2][contains(@class,'td')]"  # column 2
        self.__timeElements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,xpath)))
        return self.__timeElements

    def __goToPage(self, pageNumber: int) -> None:
        while True:
            # kiểm tra xem có đang đứng ở page được chọn chưa    
            xpath = f"//*[contains(@class,'active1')]"
            currentPageElement = self.wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
            if currentPageElement.get_attribute('id') == str(pageNumber):
                break
            xpath = f"//*[@onclick='pageNextTinAutions({pageNumber})']"
            pageElement = self.wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
            pageElement.click()
            time.sleep(2)

    def __sendFromDate(self) -> None:
        xpath = "//*[@id='txtTuNgay']"
        fromDateElement = self.wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
        fromDateElement.clear() # xóa ngày cũ
        fromDateElement.send_keys(self.fromTime.strftime('%d/%m/%Y'))

    def __sendToDate(self) -> None:
        xpath = "//*[@id='txtDenNgay']"
        toDateElement = self.wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
        toDateElement.clear() # xóa ngày cũ
        toDateElement.send_keys(self.toTime.strftime('%d/%m/%Y'))

    def __clickSearch(self) -> None:
        xpath = "//input[@id='btn_search']"
        searchButton = self.wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
        searchButton.click()

    def __selectMaxRecordsPerPage(self) -> None:
        xpath = "//*[@id='divNumberRecordOnPageAutions']"
        selectElement = self.wait.until(EC.presence_of_element_located((By.XPATH,xpath)))
        selectObject = Select(selectElement)
        maxRecordsPerPage = selectObject.options[-1].text
        selectObject.select_by_value(maxRecordsPerPage)
        return int(maxRecordsPerPage)

    @staticmethod
    def __parseTime(timeString: str):
        return dt.datetime.strptime(timeString, '%d/%m/%Y %H:%M')

    def __del__(self):
        self.driver.quit()


class HOSE(_Crawler):

    HOME = 'https://www.hsx.vn/'

    def __init__(self) -> None:
        super().__init__()
        self.__fromTime = None
        self.__toTime = None
        # Tên đấu giá -> tin tức đấu giá
        self.__url = 'https://www.hsx.vn/Modules/CMS/Web/ArticleInCategory/96029cf2-00ed-d042-ad0f-5d2d6a31a09e' 
        self.__session = None

    @property
    def url(self):
        return self.__url

    @property
    def fromTime(self) -> dt.datetime:
        if self.__fromTime:
            return self.__fromTime
        raise AttributeError('attribute fromTime not set')

    @fromTime.setter
    @logger.log
    def fromTime(self, value: dt.datetime) -> None:
        self.__fromTime = value

    @property
    def toTime(self) -> dt.datetime:
        if self.__toTime:
            return self.__toTime
        raise AttributeError('attribute toTime not set')

    @toTime.setter
    @logger.log
    def toTime(self, value: dt.datetime) -> None:
        self.__toTime = value

    @property
    def session(self):
        if self.__session is not None:
            return self.__session
        self.__session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=10)
        self.__session.mount(type(self).HOME,adapter)
        return self.__session

    @logger.log
    def crawl(self):
        # không craw lại các tin đã có trong database
        existingRecords = pd.read_sql(
            sql = f"""
                SELECT 
                    [ThoiGian], [TieuDe]
                FROM [TinDauGia]
                WHERE [SanGiaoDich] = '{type(self).__name__}'
            """,
            con = connect_DWH_ThiTruong,
            parse_dates = ['ThoiGian']
        )
        params = {
            'exclude': '00000000-0000-0000-0000-000000000000',
            'lim': 'True',
            'pageFieldName1': 'FromDate',
            'pageFieldValue1': self.fromTime.strftime('%d.%m.%Y'),
            'pageFieldOperator1': 'eq',
            'pageFieldName2': 'ToDate',
            'pageFieldValue2' : self.toTime.strftime('%d.%m.%Y'),
            'pageFieldOperator2': 'eq',
            'pageFieldName3': 'TokenCode',
            'pageFieldValue3': '',
            'pageFieldOperator3': 'eq',
            'pageFieldName4': 'CategoryId',
            'pageFieldValue4': '96029cf2-00ed-d042-ad0f-5d2d6a31a09e',
            'pageFieldOperator4': 'eq',
            'pageCriteriaLength': '4',
            '_search': 'false',
            'nd': '1671084036237',
            'rows': '100000000',
            'page': '1',
            'sidx': 'id',
            'sord': 'desc',
        }
        response = self.session.get(
            url = self.url, 
            params = params,
            headers = {'User-Agent':'Chrome/100.0.4896.88'}, 
            timeout = 30,
        )
        jsonData = response.json() # dictionary
        for row in jsonData.get('rows'):
            # Get cell value
            jsonCell = row.get('cell')  # list
            # Get time
            articleTime = type(self).__parseTime(timeString=jsonCell[1])
            # Nếu nằm ngoài inputTime thì bỏ qua
            if not self.fromTime <= articleTime <= self.toTime:
                continue
            # Get title
            titleHTML = jsonCell[2]
            titleSoup = BeautifulSoup(titleHTML,'html5lib')
            articleTitle = titleSoup.find(attrs={'data-object-type':'1'}).text
            # Nếu đã có dưới database thì bỏ qua
            maskTime = existingRecords['ThoiGian'] == articleTime
            maskTitle = existingRecords['TieuDe'] == articleTitle
            if not existingRecords.loc[maskTime & maskTitle].empty:
                continue
            # Get content
            articleContent = self.__crawlArticle(articleID=jsonCell[0])
            data = {
                'ThoiGian':  articleTime,
                'SanGiaoDich': type(self).__name__,
                'TieuDe': articleTitle,
                'NoiDung': articleContent, 
            }
            SEQUENTIALINSERT(
                connect_DWH_ThiTruong, 
                'TinDauGia', 
                pd.DataFrame(data, index=[0])
            )

    def __crawlArticle(self, articleID):
        params = {
            'id': articleID,
            'objectType': '1',
        }
        response = self.session.get(
            url = 'https://www.hsx.vn/Modules/Cms/Web/LoadArticle', 
            params = params,
            headers = {'User-Agent':'Chrome/100.0.4896.88'}, 
            timeout = 30,
        )
        html = response.text
        popupSoup = BeautifulSoup(html, 'html5lib')
        contentSoup = popupSoup.find(class_='popup-content')
        return type(self).__parseArticle2JSON(contentSoup)

    @staticmethod
    def __parseArticle2JSON(contentSoup: BeautifulSoup) -> dict:
        resultDict = {}
        # Nội dung
        content = re.sub(r'[^\w \n,.:]','',contentSoup.text)
        content = re.sub(r'\s+',' ',content).strip()
        contentDict = {'noidung': content}
        resultDict.update(contentDict)
        # File đính kèm
        hrefSoups = contentSoup.find_all(name='a',href=True)
        attachmentDict = {'filedinhkem': [{'file': soup.text, 'url': HOSE.HOME + soup['href']} for soup in hrefSoups]}
        resultDict.update(attachmentDict)
        return json.dumps(resultDict)

    @staticmethod
    def __parseTime(timeString: str) -> dt.datetime:
        processedTimeString = timeString.replace('SA','AM').replace('CH','PM')
        return dt.datetime.strptime(processedTimeString,'%d/%m/%Y %I:%M:%S %p')

    def __del__(self):
        self.session.close()