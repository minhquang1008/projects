from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time
import os
import pandas as pd


class VietStock:

    def __init__(self, startdate, enddate):
        f = open('password.json')
        self.__startDate = startdate
        self.__endDate = enddate
        self.__password = json.load(f)
        self.__url = 'https://finance.vietstock.vn/trading-statistic?tab=gd-td'
        self.__filePath = os.getcwd()
        self.df = pd.DataFrame()
        self.__exchange = [1, 2, 3]

    def crawl(self):
        service = Service(executable_path='chromedriver.exe')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": f"{self.__filePath}"
        })
        driver = webdriver.Chrome(service=service, options=options)
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        wait = WebDriverWait(driver, timeout=30, poll_frequency=1, ignored_exceptions=ignored_exceptions)
        driver.get(self.__url)
        driver.maximize_window()
        xpath = "//*[@title='Export Excel']"
        export = driver.find_element(By.XPATH, xpath)
        export.click()
        xpath = "//*[@id='txtEmailLogin']"
        email = driver.find_element(By.XPATH, xpath)
        email.send_keys(self.__password['id'])
        xpath = "//*[@id='txtPassword']"
        password = driver.find_element(By.XPATH, xpath)
        password.send_keys(self.__password['password'])
        xpath = "//*[@id='btnLoginAccount']"
        login = driver.find_element(By.XPATH, xpath)
        login.click()
        time.sleep(5)
        xpath = "//*[@id='txtFromDate']/input"
        fromDate = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
        fromDate.clear()
        fromDate.send_keys(self.__startDate)
        xpath = "//*[@id='txtToDate']/input"
        toDate = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
        toDate.clear()
        toDate.send_keys(self.__endDate)
        for i in self.__exchange:
            xpath = f"//*[@class='form-control']/option[@value='{i}']"
            exchange = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
            time.sleep(1)
            exchange.click()
            xpath = "//*[@title='Export Excel']"
            export = driver.find_element(By.XPATH, xpath)
            export.click()
            time.sleep(1)
            self.df = pd.concat([self.df, self.readFile()], ignore_index=True)

    def readFile(self):
        columns = ["DATE",
                   "STOCK",
                   "TOTAL_BUY_VOL",
                   "TOTAL_SELL_VOL",
                   "TOTAL_BUY_VAL",
                   "TOTAL_SELL_VAL",
                   "TOTAL_NET_VOL",
                   "TOTAL_NET_VAL",
                   "MATCHED_TRANS_BUY_VOL",
                   "MATCHED_TRANS_SELL_VOL",
                   "MATCHED_TRANS_BUY_VAL",
                   "MATCHED_TRANS_SELL_VAL",
                   "PUT_THROUGH_BUY_VOL",
                   "PUT_THROUGH_SELL_VOL",
                   "PUT_THROUGH_BUY_VAL",
                   "PUT_THROUGH_SELL_VAL"]

        files = os.listdir(self.__filePath)
        paths = [os.path.join(self.__filePath, basename) for basename in files]
        theNewest = max(paths, key=os.path.getctime)
        dataFrame = pd.read_excel(theNewest, skiprows=8, names=columns)
        dataFrame = dataFrame.reset_index().drop(['level_0', 'level_1'], axis=1)
        os.remove(theNewest)
        return dataFrame


if __name__ == "__main__":
    a = VietStock('01/11/2023', '28/11/2023')
    a.crawl()
    df = a.df

