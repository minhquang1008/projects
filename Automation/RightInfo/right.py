import re
import datetime as dt
from abc import ABC, abstractmethod
import itertools
import dateutil
import pandas as pd

from automation.flex_gui.RightInfo.utils import Preprocessor, Parser, Regex, Calculation
from automation.flex_gui.RightInfo.exception import ParsingError, NoDataFound
from automation.flex_gui.RightInfo.type import Fraction, Percentage
from automation.flex_gui.RightInfo.query import TinChungQuyenHOSE
from automation.flex_gui.RightInfo.cw import CWExtractor


class Right(ABC):

    def __init__(
        self,
        record: pd.Series
    ):
        self._record = record
        self.__menhGia = None
        self.__richTextList = None
        self.__plainTextList = None
        self.__plainBodyList = None

    @property
    def tieuDe(self):
        return self._record['VSD.TieuDe']

    @property
    def tenQuyen(self):
        return self.__class__.__name__

    @property
    def maChungKhoan(self):
        return self._record['VSD.MaChungKhoan']

    @property
    def ngayDangKyCuoiCung(self):
        return self._record['VSD.NgayDangKyCuoiCung'].to_pydatetime()

    @property
    def maISIN(self):
        return self._record['VSD.MaISIN']

    @property
    def URL(self):
        return self._record['VSD.URL']

    @property
    def menhGia(self):
        if self.__menhGia is not None:
            return self.__menhGia
        # không có mệnh giá -> mặc định = 0 (không ảnh hưởng logic chung)
        valueString = next(filter(lambda x: x.startswith('menh gia'),self._plainTextList),'0') 
        self.__menhGia = int(re.sub(r'\D','',valueString))
        return self.__menhGia

    @property
    def _noiDungHTML(self):
        return Preprocessor.processHTML(self._record['VSD.NoiDungHTML'])

    @property
    def _breakpoint(self):
        return self._richTextList.index('BREAK_POINT')

    def _sauNgayDangKyCuoiCung(self,**kwargs):
        return self.ngayDangKyCuoiCung + dateutil.relativedelta.relativedelta(**kwargs)

    @property
    def _richTextList(self):
        if self.__richTextList is not None:
            return self.__richTextList
        self.__richTextList = Parser.parseHTML2List(self._noiDungHTML)
        return self.__richTextList

    @property
    def _plainTextList(self):
        if self.__plainTextList is not None:
            return self.__plainTextList
        self.__plainTextList = list(
            map(Parser.parseRichText2PlainText, self._richTextList)
        )
        return self.__plainTextList

    @property
    def _plainBodyList(self):
        if self.__plainBodyList is not None:
            return self.__plainBodyList
        self.__plainBodyList = self._plainTextList[self._breakpoint + 1:]
        return self.__plainBodyList

    def __eq__(self, other: str):
        return self.tenQuyen == other

    @property
    @abstractmethod
    def _plainLookUpList(self):
        pass

    @property
    @abstractmethod
    def tyLeThucHien(self):
        pass

    @property
    @abstractmethod
    def ngayThucHienDuKien(self):
        pass

    @property
    @abstractmethod
    def phuongThucThuThueTien(self):
        pass

    @property
    @abstractmethod
    def thueSuatThueTNCNChoTien(self):
        pass

    @property
    @abstractmethod
    def thueSuatThueTNCNChoCoPhieu(self):
        pass


class ThamDuDaiHoiCoDong(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # lấy đến trước đoạn bắt đầu bằng chữ "Đề nghị"
        predicate = lambda x: not x.startswith('de nghi')
        self.__plainLookUpList = list(itertools.takewhile(predicate,self._plainBodyList))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        return Fraction('1:1')

    @property
    def ngayThucHienDuKien(self):
        if self.__ngayThucHienDuKien is not None:
            return self.__ngayThucHienDuKien
        for plainParagraph in self._plainLookUpList:
            pattern = Regex.pattern.get(self.tenQuyen).get('NgayThucHienDuKien')
            if re.search(pattern,plainParagraph):  # xác định đoạn chứa ngày thực hiện dự kiến
                self.__ngayThucHienDuKien = Parser.parsePlainText2Date(plainParagraph)
                return self.__ngayThucHienDuKien
        raise ParsingError(f"Can't parse NgayThucHienDuKien: {' '.join(self._plainLookUpList)}")

    @property
    def phuongThucThuThueTien(self):
        return 'Không'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 0

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 0


class ChiaCoTucBangTien(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self.__tyLeThucHien = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # lấy đến trước đoạn chứa "chưa lưu ký"
        predicate = lambda x: 'chua luu ky' not in x
        self.__plainLookUpList = list(itertools.takewhile(predicate,self._plainBodyList))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        # lấy đến trước đoạn chứa Ngày Thực Hiện Dự Kiến
        pattern = Regex.pattern.get(self.tenQuyen).get('NgayThucHienDuKien')
        predicate = lambda x: not re.search(pattern, x)
        targetList = itertools.takewhile(predicate, self._plainLookUpList)
        targetString = ' '.join(targetList) # đưa về một string lớn cho dễ xử lý pattern
        # Lấy toàn bộ tỷ lệ phần trăm / cổ phiếu (Ví dụ: 7,9%/cổ phiếu)
        pattern = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien')
        matchedText = re.findall(pattern, targetString)
        # chuyển từ text sang Percentage
        percentages = list(map(Parser.parsePlainText2Percentage, matchedText))
        if percentages:
            # tính toán tỷ lệ        
            self.__tyLeThucHien = Calculation.findSum(percentages, tolerance=1e-3)
            return self.__tyLeThucHien
        else:
            raise ParsingError(f"Can't parse TyLeThucHien: {targetString}")

    @property
    def ngayThucHienDuKien(self):
        if self.__ngayThucHienDuKien is not None:
            return self.__ngayThucHienDuKien
        for plainParagraph in self._plainLookUpList:
            pattern = Regex.pattern.get(self.tenQuyen).get('NgayThucHienDuKien')
            if re.search(pattern, plainParagraph): # xác định đoạn chứa ngày thực hiện dự kiến
                self.__ngayThucHienDuKien = Parser.parsePlainText2Date(plainParagraph)
                return self.__ngayThucHienDuKien
        raise ParsingError(f"Can't parse NgayThucHienDuKien: {' '.join(self._plainLookUpList)}")

    @property
    def phuongThucThuThueTien(self):
        return 'Tại Tổ chức phát hành'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 5

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 0


class ChiaCoTucBangCoPhieu(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self.__tyLeThucHien = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # lấy đến trước đoạn bắt đầu bằng "phương án"
        predicate = lambda x: not x.startswith('phuong an')
        droppedIter = itertools.takewhile(predicate, self._plainBodyList)
        self.__plainLookUpList = list(droppedIter)
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        # lấy đến trước đoạn chứa Ngày Thực Hiện Dự Kiến
        pattern = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get("Filter")
        predicate = lambda x: not re.search(pattern, x)
        targetList = itertools.takewhile(predicate, self._plainLookUpList)
        targetString = ' '.join(targetList)  # đưa về một string lớn cho dễ xử lý pattern
        # lấy pattern        
        percentagePattern = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get('PhanTram')  # bắt tỷ lệ (dạng %)
        fractionPattern = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get('PhanSo')  # bắt phần trăm
        # lấy tỷ lệ
        percentages = list(map(Parser.parsePlainText2Percentage, re.findall(percentagePattern, targetString)))
        fractions = list(map(Parser.parsePlainText2Fraction, re.findall(fractionPattern, targetString)))
        # ưu tiên láy percentages
        if percentages:
            self.__tyLeThucHien = Calculation.findSum(percentages, tolerance=1e-3)
        elif fractions:
            self.__tyLeThucHien = Calculation.findSum(fractions, tolerance=1e-3)
        else:
            raise ParsingError(f"Can't parse TyLeThucHien: {targetString}")
        return self.__tyLeThucHien

    @property
    def ngayThucHienDuKien(self):
        self.__ngayThucHienDuKien = self._sauNgayDangKyCuoiCung(months=3)
        return self.__ngayThucHienDuKien

    @property
    def giaQuyDoiChoCoPhieuLoLe(self):
        return 0

    @property
    def quyDinhLamTron(self):
        return 'Hàng đơn vị'
    
    @property
    def soChuSoThapPhanChungKhoanLeQuyDoi(self):
        return 0

    @property
    def phuongThucThuThueTien(self):
        return 'Tại Công ty chứng khoán'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 0

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 5


class CoPhieuThuong(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self.__tyLeThucHien = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # lấy đến trước đoạn chứa "chưa lưu ký"
        predicate1 = lambda x: 'chua luu ky' not in x
        droppedIter = itertools.takewhile(predicate1,self._plainBodyList)
        # xóa các đoạn bắt đầu bằng "phương án", "nguyên tắc", "ví dụ"
        predicate2 = lambda x: not x.startswith(('phuong an','nguyen tac','vi du'))
        self.__plainLookUpList = list(filter(predicate2,droppedIter))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        # lấy đến trước đoạn chứa Ngày Thực Hiện Dự Kiến
        pattern = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get("Filter")
        predicate = lambda x: not re.search(pattern, x)
        targetList = itertools.takewhile(predicate, self._plainLookUpList)
        targetString = ' '.join(targetList)  # đưa về một string lớn cho dễ xử lý pattern
        # lấy pattern        
        percentagePattern = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get('PhanTram')  # bắt tỷ lệ (dạng %)
        fractionPattern = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get('PhanSo')  # bắt phần trăm
        # lấy tỷ lệ
        percentages = list(map(Parser.parsePlainText2Percentage, re.findall(percentagePattern, targetString)))
        fractions = list(map(Parser.parsePlainText2Fraction, re.findall(fractionPattern, targetString)))
        # ưu tiên láy percentages
        if percentages:
            self.__tyLeThucHien = Calculation.findSum(percentages, tolerance=1e-3)
        elif fractions:
            self.__tyLeThucHien = Calculation.findSum(fractions, tolerance=1e-3)
        else:
            raise ParsingError(f"Can't parse TyLeThucHien: {targetString}")
        return self.__tyLeThucHien

    @property
    def ngayThucHienDuKien(self):
        self.__ngayThucHienDuKien = self._sauNgayDangKyCuoiCung(months=3)
        return self.__ngayThucHienDuKien

    @property
    def giaQuyDoiChoCoPhieuLoLe(self):
        return 0

    @property
    def quyDinhLamTron(self):
        return 'Hàng đơn vị'
    
    @property
    def soChuSoThapPhanChungKhoanLeQuyDoi(self):
        return 0

    @property
    def phuongThucThuThueTien(self):
        return 'Tại Công ty chứng khoán'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 0

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 5


class QuyenMua(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self.__tyLeThucHien = None
        self.__tyLeCoPhieuSoHuuQuyen = None
        self.__giaPhatHanh = None
        self.__ngayBatDauVaKetThucChuyenNhuong = None
        self.__ngayBatDauVaKetThucDangKyQuyenMua = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # lấy đến trước đoạn bắt đầu bằng "Phương án"
        predicate1 = lambda x: not x.startswith('phuong an')
        iter1 = itertools.takewhile(predicate1,self._plainBodyList)
        # lấy từ sau đoạn bắt đầu bằng "Lịch trình thực hiện"
        predicate2 = lambda x: not x.startswith('lich trinh thuc hien')
        iter2 = itertools.dropwhile(predicate2,self._plainBodyList)
        # gộp 2 đoạn lại với nhau
        self.__plainLookUpList = list(itertools.chain(iter1,iter2))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        # Chỉ lấy các đoạn bắt đầu bằng "Thực hiện" hoặc "Tỷ lệ thực hiện", ưu tiên "Thực hiện"
        targetString = next(
            itertools.chain(
                filter(lambda x: x.startswith('thuc hien'), self._plainLookUpList),
                filter(lambda x: x.startswith('ty le thuc hien'), self._plainLookUpList)
            )
        )
        pattern = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien')
        fractionString = re.search(pattern,targetString).group()
        self.__tyLeThucHien = Parser.parsePlainText2Fraction(fractionString)
        return self.__tyLeThucHien

    @property
    def ngayThucHienDuKien(self):
        self.__ngayThucHienDuKien = self._sauNgayDangKyCuoiCung(months=3)
        return self.__ngayThucHienDuKien

    @property
    def tyLeCoPhieuSoHuuQuyen(self):
        self.__tyLeCoPhieuSoHuuQuyen = Fraction('1:1')
        return self.__tyLeCoPhieuSoHuuQuyen

    @property
    def giaPhatHanh(self):
        # lấy đoạn đầu tiên bắt đầu bằng "Giá phát hành" và chứa giá
        pattern = Regex.pattern.get(self.tenQuyen).get('GiaPhatHanh').get('Filter')
        targetString = next(filter(lambda x: re.search(pattern, x), self._plainLookUpList))
        # lấy giá
        pattern = Regex.pattern.get(self.tenQuyen).get('GiaPhatHanh').get('Ngay')
        valueString = re.search(pattern, targetString).group()
        self.__giaPhatHanh = Parser.parsePlainTextValue2Float(valueString)
        return self.__giaPhatHanh
    
    @property
    def ngayBatDauVaKetThucChuyenNhuong(self):
        # lấy đoạn đầu tiên bắt đầu bằng "Thời gian chuyển nhượng quyền mua cổ phiếu" và chứa ngày
        pattern = Regex.pattern.get(self.tenQuyen).get('NgayBatDauVaKetThucChuyenNhuong').get("Filter")
        targetString = next(filter(lambda x: re.search(pattern, x), self._plainLookUpList))
        # lấy ngày
        pattern = Regex.pattern.get(self.tenQuyen).get('NgayBatDauVaKetThucChuyenNhuong').get("Ngay")
        dateStrings = re.findall(pattern, targetString)
        self.__ngayBatDauVaKetThucChuyenNhuong = sorted(map(lambda x: dt.datetime.strptime(x, r'%d/%m/%Y'), dateStrings))
        return self.__ngayBatDauVaKetThucChuyenNhuong

    @property
    def ngayBatDauVaKetThucDangKyQuyenMua(self):
        # lấy đoạn đầu tiên thỏa điều kiện
        pattern = Regex.pattern.get(self.tenQuyen).get('NgayBatDauVaKetThucDangKyQuyenMua').get("Filter")
        targetString = next(filter(lambda x: re.search(pattern, x), self._plainLookUpList))
        # lấy ngày
        pattern = Regex.pattern.get(self.tenQuyen).get('NgayBatDauVaKetThucDangKyQuyenMua').get("Ngay")
        dateStrings = re.findall(pattern, targetString)
        self.__ngayBatDauVaKetThucDangKyQuyenMua = sorted(map(lambda x: dt.datetime.strptime(x, r'%d/%m/%Y'), dateStrings))
        return self.__ngayBatDauVaKetThucDangKyQuyenMua

    @property
    def phuongThucThuThueTien(self):
        return 'Không'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 0

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 0


class TraLaiTraiPhieu(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self.__tyLeThucHien = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # lấy đến trước đoạn bắt đầu bằng "Đề nghị"
        predicate = lambda x: not x.startswith('de nghi')
        self.__plainLookUpList = list(itertools.takewhile(predicate,self._plainBodyList))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        # lấy đoạn đầu tiên thảa pattern
        pattern1 = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get("1")
        targetString = next(filter(lambda x: re.search(pattern1, x), self._plainLookUpList))
        # lấy giá trị lãi
        pattern2 = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get("2")
        matchObject = re.search(pattern2, targetString)
        if matchObject: # trong diễn giải có "tiền lãi" thì lấy tiền lãi
            amountString = matchObject.group(1)
        else: # trong diễn giải không có "tiền lãi" -> lấy số duy nhất
            amountString = re.search(pattern1, targetString).group(1)
        amount = float(re.sub('[^\d,]','',amountString).replace(',','.'))
        self.__tyLeThucHien = Percentage(f'{amount / self.menhGia * 100}')
        return self.__tyLeThucHien
        
    @property
    def ngayThucHienDuKien(self):
        # Chỉ lấy các đoạn thỏa điều kiện, ưu tiên lấy ngày thực thanh toán
        pattern1 = Regex.pattern.get(self.tenQuyen).get('NgayThucHienDuKien').get('1')
        pattern2 = Regex.pattern.get(self.tenQuyen).get('NgayThucHienDuKien').get('2')
        targetString = next(
            itertools.chain(
                filter(lambda x: re.search(pattern1, x), self._plainLookUpList),
                filter(lambda x: re.search(pattern2, x), self._plainLookUpList)
            )
        )
        self.__ngayThucHienDuKien = Parser.parsePlainText2Date(targetString)
        return self.__ngayThucHienDuKien

    @property
    def phuongThucThuThueTien(self):
        return 'Tại Tổ chức phát hành'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 5

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 0


class TraGocVaLaiTraiPhieu(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self.__tyLeThucHien = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # lấy đến trước đoạn bắt đầu bằng "Đề nghị"
        predicate = lambda x: not x.startswith('de nghi')
        self.__plainLookUpList = list(itertools.takewhile(predicate,self._plainBodyList))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        pattern1 = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get('LaiSuat')
        targetString1 = next(filter(lambda x: re.search(pattern1, x), self._plainLookUpList),'')
        pattern2 = Regex.pattern.get(self.tenQuyen).get('TyLeThucHien').get('GiaTri')
        targetString2 = next(filter(lambda x: re.search(pattern2, x), self._plainLookUpList),'')
        if targetString1: # bài đăng dưới dạng lãi suất
            percentString = re.search(pattern1, targetString1).group(1)
            self.__tyLeThucHien = Parser.parsePlainText2Percentage(percentString)
        elif targetString2: # bài đăng dưới dạng giá trị
            valueString = re.search(pattern2, targetString2).group(1)
            valueFloat = Parser.parsePlainTextValue2Float(valueString) / self.menhGia - 1
            self.__tyLeThucHien = Percentage(f'{valueFloat}')
        else:
            raise ParsingError(f"Can't parse TyLeThucHien: {targetString1 + targetString2}")
        return self.__tyLeThucHien

    @property
    def ngayThucHienDuKien(self):
        # Chỉ lấy các đoạn thỏa điều kiện, ưu tiên lấy ngày thực thanh toán
        pattern1 = Regex.pattern.get(self.tenQuyen).get('NgayThucHienDuKien').get('1')
        pattern2 = Regex.pattern.get(self.tenQuyen).get('NgayThucHienDuKien').get('2')
        targetString = next(
            itertools.chain(
                filter(lambda x: re.search(pattern1, x), self._plainLookUpList),
                filter(lambda x: re.search(pattern2, x), self._plainLookUpList)
            )
        )
        self.__ngayThucHienDuKien = Parser.parsePlainText2Date(targetString)
        return self.__ngayThucHienDuKien

    @property
    def phuongThucThuThueTien(self):
        return 'Tại Tổ chức phát hành'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 5

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 0


class ChuyenDoiTraiPhieuThanhCoPhieu(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self.__tyLeThucHien = None
        self._maCoPhieuChuyenDoi = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # chỉ lấy những đoạn bắt đầu bằng "Tỷ lệ" hoặc "Thời gian"
        predicate = lambda x: x.startswith(('ty le','thoi gian'))
        self.__plainLookUpList = list(filter(predicate,self._plainBodyList))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        # lấy đoạn đầu tiên thỏa điều kiện
        pattern = Regex.pattern.get(self.tenQuyen).get("TyLeThucHien").get("Filter")
        targetString = next(filter(lambda x: re.search(pattern, x), self._plainLookUpList))
        # lấy tỷ lệ 
        pattern = Regex.pattern.get(self.tenQuyen).get("TyLeThucHien").get("PhanSo")
        ratioString = re.search(pattern, targetString).group()
        self.__tyLeThucHien = Parser.parsePlainText2Fraction(ratioString)
        return self.__tyLeThucHien

    @property
    def ngayThucHienDuKien(self):
        # lấy đoạn đầu tiên bắt đầu bằng "Thời gian đăng ký chuyển đổi|thực hiện"
        pattern = Regex.pattern.get(self.tenQuyen).get("NgayThucHienDuKien").get("Filter")
        targetString = next(filter(lambda x: re.search(pattern, x), self._plainLookUpList))
        # lấy ngày lớn nhất
        pattern = Regex.pattern.get(self.tenQuyen).get("NgayThucHienDuKien").get("Ngay")
        dateStrings = re.findall(pattern,targetString)
        self.__ngayThucHienDuKien = max(map(lambda x: dt.datetime.strptime(x, r'%d/%m/%Y'), dateStrings))
        return self.__ngayThucHienDuKien

    @property
    def maCoPhieuChuyenDoi(self):
        # tìm tất đoạn đầu tiên thỏa điều kiện
        pattern = Regex.pattern.get(self.tenQuyen).get("MaCoPhieuChuyenDoi").get("Filter")
        targetString = next(filter(lambda x: re.search(pattern, x).group(), self._plainLookUpList))
        # tìm mã chứng khoán duy nhất trong đoạn
        # (greedy search, luôn chọn 3 ký tự đứng riêng lẻ cuối cùng)
        pattern = Regex.pattern.get(self.tenQuyen).get("MaCoPhieuChuyenDoi").get("MaChungKhoan")
        self._maCoPhieuChuyenDoi = re.search(pattern, targetString).group(2).upper()
        return self._maCoPhieuChuyenDoi

    @property
    def giaQuyDoiChoPhanLe(self):
        return 0
    
    @property
    def quyDinhLamTron(self):
        return 'Hàng đơn vị'

    @property
    def soChuSoThapPhanChungKhoanLeQuyDoi(self):
        return 0

    @property
    def coPhieuVeLaChoGiaoDich(self):
        return 'Có'

    @property
    def phuongThucThuThueTien(self):
        return 'Không'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 5

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 0


class ChuyenDoiCoPhieuThanhCoPhieu(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self._ngayDuKienHuyCoPhieuCu = None
        self._ngayDuKienNhanCoPhieuMoi = None
        self.__tyLeThucHien = None
        self._maCoPhieuChuyenDoi = None

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # chỉ lấy những đoạn bắt đầu bằng "Tỷ lệ"
        predicate = lambda x: x.startswith('ty le')
        self.__plainLookUpList = list(filter(predicate,self._plainBodyList))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        # lấy đoạn đầu tiên thỏa điều kiện
        pattern = Regex.pattern.get(self.tenQuyen).get("TyLeThucHien").get("Filter")
        targetString = next(filter(lambda x: re.search(pattern, x), self._plainLookUpList))
        # lấy tỷ lệ 
        pattern = Regex.pattern.get(self.tenQuyen).get("TyLeThucHien").get("PhanSo")
        ratioString = re.search(pattern, targetString).group()
        self.__tyLeThucHien = Parser.parsePlainText2Fraction(ratioString)
        return self.__tyLeThucHien

    @property
    def maCoPhieuChuyenDoi(self):
        # tìm tất đoạn đầu tiên thỏa điều kiện
        pattern = Regex.pattern.get(self.tenQuyen).get("MaCoPhieuChuyenDoi").get("Filter")
        targetString = next(filter(lambda x: re.search(pattern, x).group(), self._plainLookUpList))
        # tìm mã chứng khoán duy nhất trong đoạn
        # (greedy search, luôn chọn 3 ký tự đứng riêng lẻ cuối cùng)
        pattern = Regex.pattern.get(self.tenQuyen).get("MaCoPhieuChuyenDoi").get("MaChungKhoan")
        self._maCoPhieuChuyenDoi = re.search(pattern, targetString).group(2).upper()
        return self._maCoPhieuChuyenDoi

    @property
    def ngayThucHienDuKien(self):
        self.__ngayThucHienDuKien = self._sauNgayDangKyCuoiCung(months=3)
        return self.__ngayThucHienDuKien

    @property
    def ngayDuKienHuyCoPhieuCu(self):
        self._ngayDuKienHuyCoPhieuCu = self._sauNgayDangKyCuoiCung(months=3)
        return self._ngayDuKienHuyCoPhieuCu

    @property
    def ngayDuKienNhanCoPhieuMoi(self):
        self._ngayDuKienNhanCoPhieuMoi = self._sauNgayDangKyCuoiCung(months=3)
        return self._ngayDuKienNhanCoPhieuMoi

    @property
    def giaQuyDoiChoPhanLe(self):
        return 0
    
    @property
    def quyDinhLamTron(self):
        return 'Hàng đơn vị'

    @property
    def soChuSoThapPhanChungKhoanLeQuyDoi(self):
        return 0

    @property
    def coPhieuVeLaChoGiaoDich(self):
        return 'Có'

    @property
    def phuongThucThuThueTien(self):
        return 'Không'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 0

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 0


class TraLoiTucBangChungQuyen(Right):

    def __init__(self, record: pd.Series):
        super().__init__(record)
        self.__plainLookUpList = None
        self.__ngayThucHienDuKien = None
        self.__soTienChiTra = None
        self.__hoseURL = None
        # set tham số vào object query
        queryFromHOSE = TinChungQuyenHOSE()
        queryFromHOSE.lastRegisteredDate = self.ngayDangKyCuoiCung
        queryFromHOSE.ticker = self.maChungKhoan
        # query
        self.__rowTable = queryFromHOSE.result

    @property
    def _plainLookUpList(self):
        if self.__plainLookUpList is not None:
            return self.__plainLookUpList
        # lấy đến trước đoạn có chứa "chưa lưu ký"
        predicate = lambda x: 'chua luu ky' not in x
        self.__plainLookUpList = list(itertools.takewhile(predicate, self._plainBodyList))
        return self.__plainLookUpList

    @property
    def tyLeThucHien(self):
        return Percentage('0')

    @property
    def ngayThucHienDuKien(self):
        targetString = ' '.join(self._plainLookUpList)
        self.__ngayThucHienDuKien = Parser.parsePlainText2Date(targetString)
        return self.__ngayThucHienDuKien

    @property
    def soTienChiTra(self):
        if self.__rowTable.empty:
            raise NoDataFound(f'No data found in HOSE for CW {self.maChungKhoan} on {self.ngayDangKyCuoiCung}')
        # tính toán
        extractor = CWExtractor(record=self.__rowTable.squeeze(axis=0))
        numerator = extractor.giaThanhToan - extractor.giaThucHien
        denominator = extractor.tyLeChuyenDoi
        self.__soTienChiTra = int(numerator/denominator) * 1000
        return self.__soTienChiTra

    @property
    def HOSEURL(self):
        if self.__rowTable.empty:
            raise NoDataFound(f'No data found in HOSE for CW {self.maChungKhoan} on {self.ngayDangKyCuoiCung}')
        extractor = CWExtractor(record=self.__rowTable.squeeze(axis=0))
        self.__hoseURL = extractor.URL
        return self.__hoseURL

    @property
    def quyDinhLamTron(self):
        return 'Hàng đơn vị'

    @property
    def phuongThucThuThueTien(self):
        return 'Tại Công ty chứng khoán'

    @property
    def thueSuatThueTNCNChoTien(self):
        return 0.1

    @property
    def thueSuatThueTNCNChoCoPhieu(self):
        return 0


if __name__ == '__main__':
    from automation.flex_gui.RightInfo import query
    table = query.DanhSachQuyenVSD(atDate=dt.datetime(2022,12,18)).result
    
