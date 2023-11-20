import re
import json
import logging
import traceback
import functools
import datetime as dt
import calendar
import unidecode
import string
from typing import Union

from bs4 import BeautifulSoup

from automation.flex_gui.RightInfo.exception import ParsingError
from automation.flex_gui.RightInfo.type import Fraction, Percentage
from automation.flex_gui.base import LoggingDBHandler



class Preprocessor:

    @staticmethod
    def processHTML(markup: str):
        # bỏ toàn bộ \n khỏi HTML (do Beautifulsoup parse sai)
        processedMarkup = re.sub('\n','',markup)
        # Bỏ style <strong>, <em> và <span> khỏi HTML
        soup = BeautifulSoup(processedMarkup, 'html5lib')
        for element in soup.findAll(name=['strong','em','span']):
            element.unwrap()
        # Bỏ các tag <span> </span>
        return str(soup)
    
    @staticmethod
    def processString(text: str):
        # xóa "+", "-", "\xa0" khỏi toàn bộ văn bản 
        for char in ('-','+',u'\xa0'):
            text = text.replace(char,'')
        # strip toàn bộ ký tự lạ ở đầu đoạn
        text = text.lstrip(string.punctuation + string.whitespace)
        # strip toàn bộ ký tự lạ ở cuối đoạn trừ dấu %
        text = text.rstrip(string.punctuation.replace('%','') + string.whitespace)
        # strip các đề mục ở đầu đoạn: 1. 2) 3/ a> b] c} iii/ iv.
        text = re.sub(r'^\w{1,3}[.)/>\]}]{1,2}\s*','',text)
        return text

    @staticmethod
    def processQuarter(quarter: str, year: str) -> dt.datetime:
        if quarter in ('i','1'): # Quý 1
            return dt.datetime(int(year),3,31)
        elif quarter in ('ii','2'): # Quý 2
            return dt.datetime(int(year),6,30)
        elif quarter in ('iii','3'): # Quý 3
            return dt.datetime(int(year),9,30)
        elif quarter in ('iv','4'): # Quý 4
            return dt.datetime(int(year),12,31)
        else:
            raise ParsingError(f"Can't convert quarter {quarter}")


class Parser:

    @staticmethod
    def parseHTML2List(markup: str) -> list:
        soup = BeautifulSoup(Preprocessor.processHTML(markup), 'html5lib')
        soup = soup.find(class_='col-md-12')
        # parse table
        divTableTags = soup.findAll(name='div',class_='row')
        tableList = [' '.join(tag.stripped_strings) for tag in divTableTags]
        # parse body 
        # lấy các tag thỏa điều kiện
        mask = lambda tag: tag.get('style') or tag.name == 'p' or tag.class_ == "divPadingLeft" or tag.get('text')
        divBodyTags1 = soup.findAll(mask, recursive=False)
        bodyList = []
        for divBodyTag in divBodyTags1:
            bodyList.extend([Preprocessor.processString(string) for string in divBodyTag.stripped_strings])
        # lấy các text không nằm trong element nào cả
        outerTexts = soup.findAll(string=True, recursive=False)
        for outerText in outerTexts:
            bodyList.append(Preprocessor.processString(outerText))
        return list(filter(bool, tableList + ['BREAK_POINT'] + bodyList))

    @staticmethod
    def parseRichText2PlainText(richText: str):
        text = richText.lower() # đưa hết về lower case
        text = text.replace('tỉ lệ','tỷ lệ') # xử lý Tỉ lệ -> Tỷ lệ
        text = unidecode.unidecode(text) # xóa dấu
        return re.sub('\s+',' ',text) # xóa \s+

    @staticmethod
    def parsePlainText2Date(plainText: str) -> dt.datetime:
        # Preprocessing
        text = re.sub(r'qui','quy',plainText) # Quí 3 -> Quý 3
        text = re.sub(r'\s+(thu|cua)\s+',' ',text) # "Quý thứ 3 của năm 2022" -> "Quý 3 năm 2022", 
        text = re.sub(r'\s*nam\s*','/',text)  # "Năm" -> "/"
        text = re.sub(r'(q[\.uy\s]*)([iv0-4]{,3})',r'quy \2',text) # "Q.3/2022" -> "Quý 3/2022", "Q3/2022" -> "Quý 3/2022"
        if re.match(r'^(?!.*(tuan|\bthu\b))((ngay|thoi gian).*\d{1,2}\s*thang\s*\d{1,2})',text):
            # Nếu có Ngày dd Tháng mm
            text = re.sub(r'(\d{1,2})(\s*thang\s*)(\d{1,2})',r'\1/\3',text) # "Ngày dd Tháng mm" -> "Ngay dd/mm"
        detectedDates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}',text)
        detectedQuarters = re.findall(r'quy [iv0-4]{1,3}/\d{4}',text)
        detectedMonths = re.findall(r'\d{1,2}/\d{4}',text)
        if detectedDates:
            # lấy ngày lớn nhất
            return max(map(lambda x: dt.datetime.strptime(x,"%d/%m/%Y"), detectedDates))
        elif detectedQuarters:
            quarterString = detectedQuarters[0] # lấy quý đầu tiên (cũng là duy nhất)
            quarterString = re.sub(r'quy[\s0]*','',quarterString) # "Quy 04/2022" -> "4/2022"        
            return Preprocessor.processQuarter(*quarterString.split('/'))
        elif detectedMonths:
            # lấy ngày lớn nhất
            return max(map(lambda x: Calculation.findEndOfMonth(*x.split('/')), detectedMonths))
        else:
            raise ParsingError(f"Can't parse plain text to datetime: {plainText}")

    @staticmethod
    def parsePlainText2Fraction(plainText: str) -> float:
        # chỉ giữ lại các ký tự hợp lệ
        firstNum, secondNum = map(Parser.parsePlainTextValue2Float, plainText.split(':'))
        return Fraction(f'{firstNum}:{secondNum}')
        
    @staticmethod
    def parsePlainText2Percentage(plainText: str) -> float:
        # chỉ giữ lại các ký tự hợp lệ
        processedText = str(Parser.parsePlainTextValue2Float(plainText))
        return Percentage(processedText)

    @staticmethod
    def parsePlainTextValue2Float(plainText: str):
        # xóa toàn bộ các ký tự khác số và "," "."
        plainText = re.sub(r'[^\d,.]','',plainText)
        # tạo string chứa separator từ trái qua phải
        separatorString = re.sub(r'\d','',plainText)
        # tạo set chứa các separator
        separatorSet = set(separatorString)
        # có 3 trường hợp có thể xảy ra -> xử lý từng trường hợp
        # nếu không có separator
        if len(separatorSet) == 0:
            return float(plainText)
        # nếu chỉ có 1 loại separator
        elif len(separatorSet) == 1:
            separator = separatorSet.pop()
            lastNumString = plainText.split(separator)[-1]
            # nếu sau separator cuối cùng có 3 digit
            if len(lastNumString) == 3:
                # nếu separator là "," và xuất hiện đúng 1 lần 
                # -> xem "," là dấu thập phân
                if separator == ',' and len(separatorString) == 1:
                    return float(plainText.replace(',','.'))
                # tất cả trường hợp khác
                # -> xem separator là dấu phân cách hàng nghìn và bỏ đi
                else:
                    return float(plainText.replace(separator,''))
            # nếu separator xuất hiện đúng 1 lần
            # -> xem separator là dấu thập phân
            elif len(separatorString) == 1:
                return float(plainText.replace(separator,'.'))
            # tất cả trường hợp còn lại thì raise lỗi
            raise ParsingError(f"Can't parse {plainText} to number")
        # nếu có 2 loại separator
        else:
            firstSeparator = separatorString[0]
            lastSeparator = separatorString[-1]
            # nếu last separator xuất hiện nhiều hơn 1 lần
            # -> raise lỗi
            if separatorString.count(lastSeparator) > 1:
                raise ParsingError(f"Can't parse {plainText} to number")
            # nếu last separator xuất hiện đúng 1 lần
            # -> 1. first separator là phân cách hàng nghìn -> bỏ đi
            # -> 2. last separator là dấu thập phân -> replace bằng "."
            else:
                resultString = plainText.replace(firstSeparator,'')
                resultString = resultString.replace(lastSeparator,'.')
                return float(resultString)

    @staticmethod
    def parseRichText2RightName(richText: str) -> set:
        # xóa các \s thừa
        processedText = re.sub('\s+',' ',richText.lower())
        # map pattern với tên quyền
        pattern = Regex.pattern['RightFactory']
        selectors = lambda x: re.search(pattern[x],processedText)
        rightNameSet = set(filter(selectors, pattern.keys()))
        if 'LoaiTru' not in rightNameSet:
            return rightNameSet
        return set()


class Regex:

    with open(r'./regex.json',mode='r',encoding='utf-8') as __file:
        pattern = json.load(__file) # dictionary


class Calculation:

    @staticmethod
    def findSum(valueList: list, tolerance: float) -> Union[Fraction, Percentage]:
        maxValue = max(valueList)
        sumValue = functools.reduce(lambda a, b: a + b, valueList)
        if len(valueList) >= 3 and abs(sumValue - maxValue * 2).value <= tolerance:
            # có từ 3 giá trị trở lên, giá trị lớn nhất bằng sum các giá trị khác -> return maxValue
            return maxValue
        else:
            # tất cả các trường hợp khác -> return sumRatio
            return sumValue

    @staticmethod
    def findEndOfMonth(month: str, year: str) -> dt.datetime:
        _, lastDayOfMonth = calendar.monthrange(year=int(year), month=int(month))
        return dt.datetime(int(year), int(month), lastDayOfMonth)


class Logging:
    logger = logging.getLogger(__name__)
    handler = LoggingDBHandler('SS.RIGHTINFO')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


class Decorator:

    @staticmethod
    def __generateJSON(
        funcName: str,
        args: tuple,
        kwargs: dict,
        messageDict: dict,
    ):
        """
        Utility function for log
        """
        coerceValue = lambda x: str(x) if not isinstance(x,(int,float)) else x
        args = tuple(coerceValue(arg) for arg in args)
        kwargs = {param: coerceValue(arg) for param, arg in kwargs.items()}
        jsonDict = {'function': funcName}
        jsonDict.update({'args': args})
        jsonDict.update({'kwargs': kwargs})
        jsonDict.update({'message': messageDict})
        return json.dumps(jsonDict)

    @staticmethod
    def logRightWindowFunctions(
        logger: logging.Logger
    ):  
        def outer(func):
            def wrapper(*args,**kwargs): # args[0] luôn là self của RightScreen
                url = args[0].rightObject.URL
                try:
                    exitCode = func(*args,**kwargs)
                    messageDict = {'URL': url, 'status': 'OK', 'traceback': 'null'} 
                    json = Decorator.__generateJSON(func.__qualname__,args,kwargs,messageDict)
                    # bất kỳ hàm nào có exitCode khác 200 và 204 hoặc không emit ra exitCode và không lỗi đều không được ghi log
                    if exitCode == 200:  # nhập thành công và lấy được dữ liệu 
                        logger.info(json)
                    if exitCode == 204:  # nhập thành công nhưng phải nhập giá trị mặc định do không bắt được dữ liệu đúng
                        logger.warning(json)
                except (Exception,):
                    # ghi log
                    messageDict = {'URL': url, 'status': 'ERROR', 'traceback': traceback.format_exc()}
                    json = Decorator.__generateJSON(func.__qualname__,args,kwargs,messageDict)
                    logger.critical(json)
                    # tắt cửa sổ rightWindow đang mở để nhập record tiếp theo
                    # với args[0] luôn là RightScreen
                    if args[0].rightWindow.exists(timeout=1):
                        args[0].rightWindow.close()
            return wrapper
        return outer
        
    @staticmethod
    def logMaintWindowFunctions(
        logger: logging.Logger
    ):  
        def outer(func):
            def wrapper(*args,**kwargs): # args[0] luôn là self
                try:
                    func(*args,**kwargs) # MainWindow functions không cần exit code
                    messageDict = {'status': 'OK', 'traceback': 'null'} 
                    json = Decorator.__generateJSON(func.__qualname__,args,kwargs,messageDict)
                    logger.info(json)
                except (Exception,):
                    messageDict = {'status': 'ERROR', 'traceback': traceback.format_exc()}
                    json = Decorator.__generateJSON(func.__qualname__,args,kwargs,messageDict)
                    logger.critical(json)
            return wrapper
        return outer

    @staticmethod
    def logJobs(
        logger: logging.Logger
    ):  
        def outer(func):
            def wrapper(*args,**kwargs): # args[0] luôn là self
                try:
                    func(*args,**kwargs)
                    messageDict = {'status': 'OK', 'traceback': 'null'} 
                    json = Decorator.__generateJSON(func.__qualname__,args,kwargs,messageDict)
                    logger.info(json)
                except (Exception,):
                    messageDict = {'status': 'ERROR', 'traceback': traceback.format_exc()}
                    json = Decorator.__generateJSON(func.__qualname__,args,kwargs,messageDict)
                    logger.critical(json)
            return wrapper
        return outer