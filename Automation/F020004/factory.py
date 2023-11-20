import re
import pandas as pd
from request import connect_DWH_ThiTruong, connect_DWH_CoSo
from query import queryLoaiChungKhoan
import unidecode
from datawarehouse.__init__ import BDATE
from datetime import datetime


def findTypeStock(ticker):
    def typeObject():
        pass
    query=queryLoaiChungKhoan()
    query.ticker=ticker
    result=query.query
    if result.empty:
        return 'Chưa có thông tin trên VSD hoặc chưa crawl data',typeObject()
    else:
        try:
            value = result.loc[result['Attribute']=='Loại chứng khoán','Value'].item().lower()
            value = unidecode.unidecode(value)
            if re.search(r'co (phieu|phan)', value):
                loaiCK = 'Cổ phiếu thường'
                typeObject = CommonShares
            elif re.search(r'chung chi quy', value):
                loaiCK = 'Chứng chỉ quỹ'
                typeObject = FundCertificates
            elif re.search(r'trai phieu', value):
                loaiCK = 'Trái phiếu'
                typeObject = Bonds
            else:
                raise NoType('Không nằm trong 4 loại cơ bản')

            return loaiCK, typeObject()
        except ValueError:
            return 'Chứng quyền', CoverWarrant()

class NoType(Exception):
    pass

class Base:
    def __init__(self):
        self.__ticker = None
        self.__query = None

    @property
    def ticker(self):
        return self.__ticker

    @ticker.setter
    def ticker(self, value):
        self.__ticker = value
        self.__query = None

    @property
    def query(self):
        if self.__query is not None:
            return self.__query
        self.__query = pd.read_sql(
            f"""
                SELECT
                    [Attribute],
                    [Value]
                FROM [SecuritiesInfoVSD] [infoVSD]
                WHERE [infoVSD].[Ticker] = '{self.__ticker}'
            """,
            connect_DWH_ThiTruong
        )
        return self.__query

    def getTenVietTat(self):
        return self.query.loc[self.query['Attribute'] == 'Mã chứng khoán', 'Value'].item()

    def getTCPH(self):
        return self.query.loc[self.query['Attribute'] == 'Tên chứng khoán', 'Value'].item()

    def getTenGD(self):
        return self.query.loc[self.query['Attribute'] == 'Tên chứng khoán', 'Value'].item()

    def getTenGDTA(self):
        return self.query.loc[self.query['Attribute'] == 'Securities name', 'Value'].item()

    def getTenTA(self):
        return self.query.loc[self.query['Attribute'] == 'Securities name', 'Value'].item()

    def getNoiQuanLyVSD(self):
        value = self.query.loc[self.query['Attribute'] == 'Nơi quản lý tại VSD', 'Value'].item()
        if value == 'Trụ sở chính':
            noiQuanLyVSD = 'Trung tâm lưu ký chứng khoán Việt Nam'
        else:
            noiQuanLyVSD = 'Trung tâm lưu ký chứng khoán Việt Nam - Chi nhánh TP Hồ Chí Minh'
        return noiQuanLyVSD

    def getMaISIN(self):
        return self.query.loc[self.query['Attribute'] == 'Mã ISIN', 'Value'].item()

    def getMaCK(self):
        return self.ticker

    def getNoiGD(self):
        return self.query.loc[self.query['Attribute'] == 'Sàn giao dịch', 'Value'].item()

    def getMenhGia(self):
        return re.sub("đồng", "", self.query.loc[self.query['Attribute'] == 'Mệnh giá', 'Value'].item()).strip()

    def getLoaiTraiPhieu(self):
        return 'Không phải trái phiếu'

    def getLoaiCK(self):
        return self.query.loc[self.query['Attribute'] == 'Loại chứng khoán', 'Value'].item()

class CommonShares(Base):
    @Base.ticker.setter
    def ticker(self, value):
        Base.ticker.fset(self, value)
        if findTypeStock(value)[0] != 'Cổ phiếu thường':
            raise Exception('Mã chứng khoán này không phải là cổ phiếu')

    # overwrite
    def getTCPH(self):
        return self.query.loc[self.query['Attribute'] == 'Tên TCPH', 'Value'].item()

    # overwrite
    def getTenTA(self):
        return self.query.loc[self.query['Attribute'] == 'Issuers name', 'Value'].item()


class FundCertificates(Base):
    @Base.ticker.setter
    def ticker(self, value):
        Base.ticker.fset(self, value)
        if findTypeStock(value)[0] != 'Chứng chỉ quỹ':
            raise Exception('Mã chứng khoán này không phải là chứng chỉ quỹ')

class Bonds(Base):
    @Base.ticker.setter
    def ticker(self, value):
        Base.ticker.fset(self, value)
        if 'Trái phiếu' not in findTypeStock(value)[0]:
            raise Exception('Mã chứng khoán này không phải là trái phiếu')

    def getLoaiTraiPhieu(self):
        if re.match('(?=.*chính phủ.*).*',self.query.loc[self.query['Attribute'] == 'Loại chứng khoán', 'Value'].item(),re.IGNORECASE):
            loaiTraiPhieu = 'Trái phiếu chính phủ'
        elif re.match('(?=.*chính quyền.*).*',self.query.loc[self.query['Attribute'] == 'Loại chứng khoán', 'Value'].item(),re.IGNORECASE):
            loaiTraiPhieu = 'Trái phiếu chính quyền'
        elif re.match('(?=.*doanh nghiệp.*).*',self.query.loc[self.query['Attribute'] == 'Loại chứng khoán', 'Value'].item(),re.IGNORECASE):
            loaiTraiPhieu = 'Trái phiếu doanh nghiệp'
        else:
            loaiTraiPhieu = 'Trái phiếu bảo lãnh'
        return loaiTraiPhieu

    def getLoaiKyHan(self):
        if re.match('(?=.*năm.*).*',self.query.loc[self.query['Attribute'] == 'Kỳ hạn', 'Value'].item()):
            return 'Năm'
        elif re.match('(?=.*tháng.*).*', self.query.loc[self.query['Attribute'] == 'Kỳ hạn', 'Value'].item()):
            return 'Tháng'
        else:
            return 'Tuấn'

    def getKyHan(self):
        return re.search('\d+',self.query.loc[self.query['Attribute'] == 'Kỳ hạn', 'Value'].item()).group()

class CoverWarrant(Base):
    @Base.ticker.setter
    def ticker(self, value):
        Base.ticker.fset(self, value)
        if findTypeStock(value)[0] != 'Chứng quyền':
            raise Exception('Mã chứng khoán này không phải là chứng quyền')

    def getTenVietTat(self):
        return self.query.loc[self.query['Attribute'] == 'Mã chứng quyền', 'Value'].item()

    def getTCPH(self):
        return self.query.loc[self.query['Attribute'] == 'Tên chứng quyền', 'Value'].item()

    def getTenGD(self):
        return self.query.loc[self.query['Attribute'] == 'Tên chứng quyền', 'Value'].item()

    def getTenGDTA(self):
        return self.query.loc[self.query['Attribute'] == 'Name of warrant', 'Value'].item()

    def getTenTA(self):
        return self.query.loc[self.query['Attribute'] == 'Name of warrant', 'Value'].item()

    def getMaCKCS(self):
        return self.query.loc[self.query['Attribute'] == 'Mã chứng khoán cơ sở', 'Value'].item()

    def getToChucPhatHanhMaCKCS(self):
        return self.query.loc[self.query['Attribute'] == 'Tổ chức phát hành mã chứng khoán cơ sở', 'Value'].item()

    def getLoaiChungQuyen(self):
        return self.query.loc[self.query['Attribute'] == 'Loại chứng quyền', 'Value'].item()

    def getPhuongThucThanhToan(self):
        if re.match('(?=.*bằng tiền.*).*',self.query.loc[self.query['Attribute'] == 'Phương thức thực hiện chứng quyền', 'Value'].item(),re.IGNORECASE):
            return 'Thanh toán bằng tiền'
        else:
            return 'Chuyển giao chứng khoán'

    def getGiaThucHien(self):
        return re.sub("đồng", "", self.query.loc[self.query['Attribute'] == 'Giá thực hiện', 'Value'].item()).strip()

    def getTyLeChuyenDoi(self):
        return self.query.loc[self.query['Attribute'] == 'Tỷ lệ chuyển đổi', 'Value'].item()

    def getThoiHan(self):
        return re.search('\d+', self.query.loc[self.query['Attribute'] == 'Thời hạn', 'Value'].item()).group()

    def getNgayDaoHan(self):
        return datetime.strptime(self.query.loc[self.query['Attribute'] == 'Ngày đáo hạn', 'Value'].item(), "%d%m%Y").strftime("%d/%m/%Y")

    def getGiaoDichCuoiCung(self):
        return datetime.strptime(BDATE(datetime.strptime(self.query.loc[self.query['Attribute'] == 'Ngày đáo hạn', 'Value'].item(), "%d%m%Y"), -2), '%Y-%m-%d').strftime("%d/%m/%Y")
