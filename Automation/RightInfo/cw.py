import re
import string
import datetime as dt
import pandas as pd
from automation.flex_gui.RightInfo.utils import Parser, Regex

class CWExtractor:


    def __init__(self,record: pd.Series):
        self.record = record
        self.__richTextContent = self.record['HOSE.NoiDung']
        
        plainTextContent = Parser.parseRichText2PlainText(self.__richTextContent)
        # "hoan doi", "chuyen doi", "thuc hien" -> "thanh toan"
        pattern = r'(hoan doi|chuyen doi|thuc hien)'
        self.__plainTextContent = re.sub(pattern,'thanh toan',plainTextContent)


    @property
    def __className(self):
        return self.__class__.__name__


    @property
    def URL(self):
        return self.record['HOSE.URL']


    @property
    def tenToChucPhatHanh(self):
        pattern = Regex.pattern[self.__className].get('TenToChucPhatHanh')
        matchString = re.search(pattern, self.__richTextContent, re.IGNORECASE).group()
        return matchString.strip(string.whitespace + string.punctuation)


    @property
    def maChungQuyen(self):
        pattern = Regex.pattern[self.__className].get('MaChungQuyen')
        matchString = re.search(pattern, self.__plainTextContent).group()
        return matchString.strip(string.whitespace + string.punctuation).upper()


    @property
    def tyLeChuyenDoi(self):
        pattern = Regex.pattern[self.__className].get('TyLeChuyenDoi')
        matchString = re.search(pattern, self.__plainTextContent).group()
        valueString = matchString.strip(string.whitespace + string.punctuation)
        firstNum, secondNum = list(map(Parser.parsePlainTextValue2Float, valueString.split(':')))
        return firstNum / secondNum


    @property
    def giaThucHien(self):
        pattern = Regex.pattern[self.__className].get('GiaThucHien')
        matchString = re.search(pattern, self.__plainTextContent).group()
        valueString = matchString.strip(string.whitespace + string.punctuation)
        return int(Parser.parsePlainTextValue2Float(valueString))


    @property
    def ngayGiaoDichCuoiCung(self):
        pattern = Regex.pattern[self.__className].get('NgayGiaoDichCuoiCung')
        matchString = re.search(pattern,self.__plainTextContent).group()
        valueString = matchString.strip(string.whitespace + string.punctuation)
        return dt.datetime.strptime(valueString,r'%d/%m/%Y')


    @property
    def ngayDaoHan(self):
        pattern = Regex.pattern[self.__className].get('NgayDaoHan')
        matchString = re.search(pattern,self.__plainTextContent).group()
        valueString = matchString.strip(string.whitespace + string.punctuation)
        return dt.datetime.strptime(valueString,r'%d/%m/%Y')


    @property
    def giaThanhToan(self):
        pattern = Regex.pattern[self.__className].get('GiaThanhToan')
        matchString = re.search(pattern,self.__plainTextContent).group()
        valueString = matchString.strip(string.whitespace + string.punctuation)
        return int(Parser.parsePlainTextValue2Float(valueString))


