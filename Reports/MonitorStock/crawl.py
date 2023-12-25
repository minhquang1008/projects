import pandas as pd
import datetime as dt
import time
import numpy as np

from os.path import join, dirname, realpath, isfile
from os import listdir, remove
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from request.stock import internal
from news_collector import scrape_ticker_by_exchange

from datawarehouse import BATCHINSERT, DELETE, BDATE
from request import connect_DWH_ThiTruong


class MonitorStock:

    PATH = join(dirname(dirname(dirname(realpath(__file__)))), 'dependency', 'chromedriver')

    def __init__(self):

        self.__hideWindow = True
        self.__today = dt.datetime.now().strftime('%Y-%m-%d')
        self.__yesterday = BDATE(self.__today, -1)
        self.__priceTable = None
        self.__ignored_exceptions = (
            ValueError,
            IndexError,
            NoSuchElementException,
            StaleElementReferenceException,
            TimeoutException,
            ElementNotInteractableException
        )

    @staticmethod
    def __formatPrice(inputString: str):
        if not inputString:  # x == ''
            inputString = None
        elif inputString in ('ATO', 'ATC'):
            inputString = None
        else:
            inputString = float(inputString)
        return inputString

    @staticmethod
    def __formatVolume(inputString):
        if not inputString:  # x == ''
            inputString = None
        else:
            inputString = float(inputString.replace(',', '')) * 10  # 2,30 -> 2300, 10 -> 100
        return inputString

    def priceTable(self, exchange: str):

        # Lấy tickers
        tickersFile = join(dirname(__file__), 'TempFiles', f"TickerList_{self.__today.replace('-', '.')}.pickle")
        if not isfile(tickersFile):
            allTickers = scrape_ticker_by_exchange.run().reset_index()
            allTickers.to_pickle(tickersFile)
        else:
            allTickers = pd.read_pickle(tickersFile)

        options = Options()
        if self.__hideWindow:
            options.headless = True
        driver = webdriver.Chrome(service=Service(self.PATH), options=options)
        wait = WebDriverWait(driver, 60, ignored_exceptions=self.__ignored_exceptions)
        url = r'https://priceboard.vcbs.com.vn/Priceboard/'
        driver.get(url)
        time.sleep(5)  # bắt buộc

        allTickers = allTickers.loc[allTickers['ticker'].map(len) == 3]

        if exchange == 'HOSE':
            exchangeXpath = '//*[text()="HOSE"]'
            fullTickers = allTickers.loc[allTickers['exchange'] == 'HOSE', 'ticker']
            mlist = internal.mlist(['HOSE'])
        elif exchange == 'HNX':
            exchangeXpath = '//*[text()="HNX"]'
            fullTickers = allTickers.loc[allTickers['exchange'] == 'HNX', 'ticker']
            mlist = internal.mlist(['HNX'])
        else:
            raise ValueError('Currently monitor HOSE and HNX only')

        tickerPool = set(fullTickers) & set(mlist)  # các cp phải quét
        while True:
            try:
                driver.find_element(By.XPATH, exchangeXpath).click()
                break
            except (Exception,):
                time.sleep(1)

        frames = []
        for ticker in tickerPool:
            print(f'Extract {ticker} ...')
            xpath = f'//tbody/*[@name="{ticker}"]'
            tickerElement = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            subWait = WebDriverWait(tickerElement, 60, ignored_exceptions=self.__ignored_exceptions)
            # Trần
            Ceiling = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}ceiling'))).text
            )
            # Sàn
            Floor = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}floor'))).text
            )
            # Tham chiếu
            Prior = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}priorClosePrice'))).text
            )
            # Giá khớp lệnh
            MatchPrice = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}closePrice'))).text
            )
            # Khối lượng khớp lệnh
            MatchVolume = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}closeVolume'))).text
            )
            # Giá mua
            BuyPrice1 = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best1Bid'))).text
            )
            BuyPrice2 = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best2Bid'))).text
            )
            BuyPrice3 = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best3Bid'))).text
            )
            # Khối lượng mua
            BuyVolume1 = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best1BidVolume'))).text
            )
            BuyVolume2 = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best2BidVolume'))).text
            )
            BuyVolume3 = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best3BidVolume'))).text
            )
            # Giá bán
            SellPrice1 = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best1Offer'))).text
            )
            SellPrice2 = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best2Offer'))).text
            )
            SellPrice3 = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best3Offer'))).text
            )
            # Khối lượng bán
            SellVolume1 = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best1OfferVolume'))).text
            )
            SellVolume2 = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best2OfferVolume'))).text
            )
            SellVolume3 = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}best3OfferVolume'))).text
            )
            # NN mua
            FrgBuy = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}foreignBuy'))).text
            )
            # NN Bán
            FrgSell = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}foreignSell'))).text
            )
            # NN Room
            FrgRoom = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}foreignRemain'))).text
            )
            # Tổng khối lượng
            TotalVolume = self.__formatVolume(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}totalTrading'))).text
            )
            # Giá mở cửa
            OpenPrice = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}open'))).text
            )
            # Giá cao nhất
            HighPrice = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}high'))).text
            )
            # Giá thấp nhất
            LowPrice = self.__formatPrice(
                subWait.until(EC.presence_of_element_located((By.ID, f'{ticker}low'))).text
            )
            # append to list
            frames.append((
                ticker,
                Ceiling,
                Floor,
                Prior,
                MatchPrice,
                MatchVolume,
                BuyPrice1,
                BuyVolume1,
                BuyPrice2,
                BuyVolume2,
                BuyPrice3,
                BuyVolume3,
                SellPrice1,
                SellVolume1,
                SellPrice2,
                SellVolume2,
                SellPrice3,
                SellVolume3,
                TotalVolume,
                OpenPrice,
                HighPrice,
                LowPrice,
                FrgBuy,
                FrgSell,
                FrgRoom
            ))
        table = pd.DataFrame(
            data=frames,
            columns=[
                'MaChungKhoan',
                'GiaTran',
                'GiaSan',
                'GiaThamChieu',
                'GiaKhopLenh',
                'KhoiLuongKhopLenh',
                'GiaMua1',
                'KhoiLuongMua1',
                'GiaMua2',
                'KhoiLuongMua2',
                'GiaMua3',
                'KhoiLuongMua3',
                'GiaBan1',
                'KhoiLuongBan1',
                'GiaBan2',
                'KhoiLuongBan2',
                'GiaBan3',
                'KhoiLuongBan3',
                'TongKhoiLuong',
                'GiaMoCua',
                'GiaCaoNhat',
                'GiaThapNhat',
                'NuocNgoaiMua',
                'NuocNgoaiBan',
                'NuocNgoaiRoom'
            ]
        )
        table.insert(1, 'SanChungKhoan', exchange)
        table['GiaDongCua'] = None

        return table


if __name__ == '__main__':
    m = MonitorStock()

    dfList = []
    for exchange in ['HOSE', 'HNX']:
        print(f'-------- START {exchange} --------')
        df = m.priceTable(exchange)
        dfList.append(df)

    fullTable = pd.concat(dfList, ignore_index=True)
    fullTable = fullTable.fillna(0)
    DELETE(
        conn=connect_DWH_ThiTruong,
        table='BangDienRealTime',
        where=''
    )
    BATCHINSERT(
        conn=connect_DWH_ThiTruong,
        table='BangDienRealTime',
        df=fullTable
    )
