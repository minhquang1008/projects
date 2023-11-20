import warnings; warnings.filterwarnings('ignore')
import datetime as dt
import pandas as pd
import unidecode
from abc import ABC, abstractmethod
from request import connect_DWH_ThiTruong, connect_DWH_CoSo
from datawarehouse import BDATE, SYNC


class Query(ABC):
    
    def __init__(self):
        self._result = None

    @property
    @abstractmethod
    def result(self) -> pd.DataFrame:
        pass


class DanhSachQuyenVSD(Query):

    def __init__(self, atDate: dt.datetime):
        super().__init__()
        self.atDate = atDate

    @property
    def result(self) -> pd.DataFrame:
        
        atDateString = self.atDate.strftime(r'%Y-%m-%d')
        statement = f"""
            SELECT 
                [ThoiGian] [VSD.ThoiGian],
                [URL] [VSD.URL],
                [NgayDangKyCuoiCung] [VSD.NgayDangKyCuoiCung],
                [MaChungKhoan] [VSD.MaChungKhoan],
                [MaISIN] [VSD.MaISIN],
                [TieuDe] [VSD.TieuDe],
                [NoiDungHTML] [VSD.NoiDungHTML]
            FROM [TinThucHienQuyenVSD]
            WHERE [ThoiGian] <= '{atDateString} 23:59:59'
            ORDER BY [ThoiGian] DESC, [MaChungKhoan] ASC
            """
        
        self._result = pd.read_sql(
            sql = statement, 
            con = connect_DWH_ThiTruong, 
            parse_dates = ['VSD.ThoiGian','VSD.NgayDangKyCuoiCung']
        )

        return self._result


class F220001(Query):

    @property
    def result(self) -> pd.DataFrame:

        today = dt.date.today().strftime(r'%Y-%m-%d')
        # SYNC(connect_DWH_CoSo,'sp220001_UAT',today,today)
        SYNC(connect_DWH_CoSo,'sp220001',today,today)

        statement = f"""
            SELECT
                [NgayDangKyCuoiCung] [F220001.NgayDangKyCuoiCung],
                [ChungKhoanChot] [F220001.MaChungKhoan],
                [LoaiThucHienQuyen] [F220001.LoaiQuyen],
                [MaThucHienQuyen] [F220001.MaThucHienQuyen],
                [TyLeChiaCoTucBangTien] [F220001.TyLeChiaCoTucBangTien]
            -- FROM [220001_UAT]
            FROM [220001]
            WHERE [TrangThai] IN (N'Chờ duyệt',N'Duyệt')
            ORDER BY [NgayDangKyCuoiCung] DESC, [ChungKhoanChot] ASC
        """

        table = pd.read_sql(
            sql = statement, 
            con = connect_DWH_CoSo, 
            parse_dates = ['F220001.NgayDangKyCuoiCung']
        )
        table['F220001.LoaiQuyen'] = table['F220001.LoaiQuyen'].str.replace(r'\W','')
        table['F220001.LoaiQuyen'] = table['F220001.LoaiQuyen'].apply(lambda x: unidecode.unidecode(x).lower())

        mapper = {
            'thamdudaihoicodong': 'ThamDuDaiHoiCoDong',
            'quyenmua': 'QuyenMua',
            'chiacotucbangtien': 'ChiaCoTucBangTien',
            'tralaitraiphieu': 'TraLaiTraiPhieu',
            'chuyendoicophieuthanhcophieu': 'ChuyenDoiCoPhieuThanhCoPhieu',
            'chuyendoitraiphieuchonnhancphoactien': 'ChuyenDoiTraiPhieuThanhCoPhieu',
            'cophieuthuong': 'CoPhieuThuong',
            'chiacotucbangcophieu': 'ChiaCoTucBangCoPhieu',
            'tragocvalaitraiphieu': 'TraGocVaLaiTraiPhieu',
            'chitraloitucchungquyen': 'TraLoiTucBangChungQuyen',
        }
        table['F220001.LoaiQuyen'] = table['F220001.LoaiQuyen'].apply(lambda x: mapper.get(x))
        self._result = table

        return self._result


class ChungKhoanRSE0008(Query):

    def __init__(self, atDate: dt.datetime):
        super().__init__()
        self.atDate = atDate

    @property
    def result(self) -> pd.DataFrame:

        atDateString = self.atDate.strftime(r'%Y-%m-%d')
        SYNC(connect_DWH_CoSo,'spRSE0008',atDateString,atDateString)
        # SYNC(connect_DWH_CoSo,'spRSE0008_UAT',atDateString,atDateString)

        statement = f"""
            SELECT DISTINCT [MaCK] [RSE0008.MaChungKhoan]
            FROM [RSE0008] 
            -- FROM [RSE0008_UAT] 
            WHERE [GiaoDich] + [BanChoGiao] > 0
                AND [Ngay] = '{atDateString}'
        """

        self._result = pd.read_sql(statement, connect_DWH_CoSo)
        return self._result



class TinChungQuyenHOSE(Query):


    def __init__(self):
        super().__init__()
        self._ticker = None
        self.lastRegisteredDate = dt.date.today()  # mặc định hôm nay, client set ngày sau


    @property
    def lastRegisteredDate(self):
        return self._lastRegisteredDate


    @lastRegisteredDate.setter  # chủ yếu để backtest, production không cần setter
    def lastRegisteredDate(self, dateValue: dt.datetime):
        dateString = dateValue.strftime('%Y-%m-%d')
        self._lastRegisteredDate = dateString
        self._prevDate = BDATE(dateString,-1)
        self._nextDate = BDATE(dateString,+1)


    @property
    def ticker(self):
        return self._ticker
    

    @ticker.setter
    def ticker(self, ticker: str):
        self._ticker = ticker


    @property
    def result(self) -> pd.DataFrame:

        statement = f"""
            SELECT TOP 1
                [ThoiGian] [HOSE.ThoiGian],
                [URL] [HOSE.URL],
                [TieuDe] [HOSE.TieuDe],
                [NoiDung] [HOSE.NoiDung]
            FROM [TinChungQuyenHOSE]
            WHERE [TieuDe] LIKE N'%giá thanh toán vào ngày đáo hạn%{self.ticker}%'
                AND [ThoiGian] BETWEEN '{self._prevDate} 00:00:00' AND '{self._nextDate} 23:59:59'
            ORDER BY [ThoiGian] DESC
        """

        self._result = pd.read_sql(statement, connect_DWH_ThiTruong)
        return self._result



class LogTable(Query):

    @property
    def result(self) -> pd.DataFrame:

        today = dt.date.today().strftime(r'%Y-%m-%d')
        statement = f"""
            WITH
            [LastRecord] AS (
                SELECT [RunTime], [URL], [Function], [Status]
                FROM (
                    SELECT
                        [RUNTIME] [RunTime],
                        MAX([RUNTIME]) OVER (
                            PARTITION BY JSON_VALUE([MESSAGE], '$.message.URL'), JSON_VALUE([MESSAGE], '$.function')
                        ) [MaxTime],
                        JSON_VALUE([MESSAGE], '$.message.URL') [URL],
                        LAST_VALUE([LEVELNAME]) OVER (
                            PARTITION BY JSON_VALUE([MESSAGE], '$.message.URL'), JSON_VALUE([MESSAGE], '$.function')
                            ORDER BY [RUNTIME]
                        ) [Status],
                        JSON_VALUE([MESSAGE], '$.function') [Function]
                    FROM [DWH-AppLog].[dbo].[SS.RIGHTINFO]
                    WHERE [RUNTIME] >= '{today} 00:00:00'
                        AND JSON_VALUE([MESSAGE], '$.function') NOT LIKE 'MainScreen.%'
                        AND JSON_VALUE([MESSAGE], '$.function') NOT LIKE 'Worker.%'
                ) [z]
                WHERE [RUNTIME] = [MaxTime]
            )
            , [RawStep] AS (
                SELECT
                    [RunTime],
                    [URL],
                    SUBSTRING([Function], CHARINDEX('._insert', [Function]) + LEN('._insert'), LEN([Function])) [WarningAttribute]
                FROM [LastRecord]
                WHERE [RunTime] >= '{today} 00:00:00'
                    AND [Status] = 'WARNING'
                    AND [Function] LIKE '%._insert%'
            )
            , [Step] AS (
                SELECT 
                    [RunTime],
                    [URL],
                    'WARNING' [Status],
                    STRING_AGG([WarningAttribute],', ') [Attribute]
                FROM [RawStep]
                GROUP BY [RunTime], [URL]
            )
            , [Record] AS (
            SELECT 
                [RunTime],
                [URL],
                CASE [Status] WHEN 'INFO' THEN 'SUCCESS' ELSE 'ERROR' END [Status]
            FROM [LastRecord]
            WHERE [URL] != 'null'
                AND [Status] IN ('INFO','CRITICAL')
                AND ([Function] LIKE '%.create%' OR [Function] LIKE '%.edit%')
                AND [RUNTIME] >= '{today} 00:00:00'
            )
            SELECT
                [Record].[RunTime] [Log.RunTime],
                [Record].[URL] [Log.URL],
                CASE WHEN [Record].[Status] = 'ERROR' THEN 'ERROR'
                    ELSE COALESCE([Step].[Status], [Record].[Status])
                END [Log.Status],
                CASE
                    WHEN [Record].[Status] = 'ERROR' THEN N'Chưa nhập Flex'
                    WHEN [Step].[Attribute] IS NOT NULL THEN N'Nhập Flex thành công, cần kiểm tra lại dữ liệu: ' + [Step].[Attribute] 
                    WHEN [Record].[Status] = 'SUCCESS' THEN N'Nhập Flex thành công'
                END [Log.Message]
            FROM [Record]
                LEFT JOIN [Step] ON [Record].[URL] = [Step].[URL] AND [Record].[RunTime] >= [Step].[RunTime]
            ORDER BY [Record].[RunTime] DESC
            """

        self._result = pd.read_sql(statement, connect_DWH_CoSo)
        return self._result
