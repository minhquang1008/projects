import datetime as dt
import pandas as pd
from abc import ABC, abstractmethod
from request import connect_DWH_ThiTruong, connect_DWH_CoSo

class AbstractQuery(ABC):

    def __init__(self):
        self._query = None
        self._dateRun = None
        self._ticker = None

    @property
    @abstractmethod
    def query(self):
        pass

class queryLoaiChungKhoan(AbstractQuery):

    def __init__(self):
        super().__init__()

    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker (self,value):
        self._ticker=value
    @property
    def query(self):
        self._query = pd.read_sql(
            f"""
            SELECT
                [Attribute],[Value]
            FROM [SecuritiesInfoVSD] [infoVSD]
            WHERE [infoVSD].[Ticker] = '{self.ticker}'
            """,
            connect_DWH_ThiTruong
        )
        return self._query

class query154000(AbstractQuery):
    def __init__(self):
        super().__init__()

    @property
    def query(self):
        self._query = pd.read_sql(
            f"""
            SELECT
                [_154000].[MaChungKhoan]
            FROM [115400.ST9944] [_154000]
            WHERE [_154000].[TenDien] = N'Thông báo mã chứng khoán đăng ký mới'
            AND [_154000].[NgayTaoDien] = '{self._dateRun}'
            ORDER BY [MaChungKhoan]
            """,
            connect_DWH_CoSo
        )
        return self._query

class query020004(AbstractQuery):
    @property
    def query(self):
        """
        Hàm dùng để kiểm tra xem các mã mới từ điện VSD trả về đã có trong 020004 chưa
        """
        self._query = pd.read_sql(
            f"""
            SELECT
                [_154000].[MaChungKhoan]
            FROM [115400.ST9944] [_154000]
            WHERE [_154000].[NgayTaoDien] = '{self._dateRun}'
            AND [_154000].[TenDien] = N'Thông báo mã chứng khoán đăng ký mới'
            AND [_154000].[MaChungKhoan] IN (
                SELECT [TenVietTat]
                FROM [020004]
            )
            ORDER BY [MaChungKhoan]
            """,
            connect_DWH_CoSo
        )
        return self._query
