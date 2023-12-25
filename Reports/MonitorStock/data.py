import pandas as pd
import datetime as dt
import warnings

from abc import ABC, abstractmethod
from request import connect_DWH_CoSo, connect_DWH_AppData

from datawarehouse import BDATE, SYNC

# import module code sẵn
from warning import warning_RMD_EOD

warnings.filterwarnings('ignore')


class Query(ABC):

    @property
    @abstractmethod
    def result(self):
        pass

    @property
    @abstractmethod
    def runDate(self):
        pass


class WarningMonitorStock(Query):

    def __init__(self):
        self.__result = None
        self.__runDate = None

    @property
    def result(self) -> pd.DataFrame:

        # Ngày chạy
        self.__runDate = dt.datetime.now()
        dateString = self.__runDate.strftime('%Y-%m-%d')

        # đồng bộ dữ liệu bảng điện, vpr0109 và 230007
        print("Waiting to SYNC data 2 table vpr0109 and 230007 ...")
        # SYNC(connect_DWH_CoSo, 'spvpr0109', FrDate=dateString, ToDate=dateString)
        # SYNC(connect_DWH_CoSo, 'sp230007', FrDate=dateString, ToDate=dateString)

        statement = f'''
            DECLARE @NullTime AS DATETIME 
            SET @NullTime = '1900-01-01';
            
            WITH [MarginList] AS (
                SELECT
                    [ticker_code]
                    , MAX(CASE
                        WHEN [room_code] LIKE 'CL01%' THEN [margin_max_price]
                        ELSE NULL
                    END) [MaxPrice]
                    , MAX(CASE
                        WHEN [room_code] LIKE 'CL01%' THEN [margin_ratio] / 100  -- chia để dữ liệu có sự tương đồng
                        ELSE NULL
                    END) [Ratio]
                FROM [DWH-CoSo].[dbo].[vpr0109]
                WHERE [date] = '{dateString}'
                    AND [room_code] NOT LIKE 'BL%'
                    AND [ticker_code] NOT LIKE '%_WFT'
                GROUP BY [ticker_code]
            )
                    
            , [BangDienFull] AS (
               SELECT
                    ISNULL([ThoiGianKhopLenh], @NullTime) [ThoiGianKhopLenh]
                    , [MaChungKhoan]
                    , [GiaSan] * 1000 [GiaSan]
                    , CASE
                        WHEN [GiaKhopLenh] IS NULL THEN [GiaThamChieu] * 1000
                        ELSE [GiaKhopLenh] * 1000
                    END [GiaKhopLenh]
                    , [GiaThamChieu] * 1000 [GiaThamChieu]
                    , ISNULL([KhoiLuongKhopLenh], 0) [KhoiLuongKhopLenh]
                    , MAX(ISNULL([KhoiLuongKhopLenh], 0)) OVER (PARTITION BY [MaChungKhoan], [ThoiGianKhopLenh]) [MaxKhoiLuongKhopLenh]
                    , MAX(ISNULL([ThoiGianKhopLenh], @NullTime)) OVER (PARTITION BY [MaChungKhoan]) [MaxTime]
                    , MAX(ISNULL([GiaKhopLenh], 0) * 1000) OVER (PARTITION BY [MaChungKhoan], [ThoiGianKhopLenh]) [MaxGiaKhopLenh]
                FROM [DWH-ThiTruong].[dbo].[BangDienRealTime]
                WHERE LEN([MaChungKhoan]) = 3
            )
            
            , [BangDienRealTime] AS (
                SELECT DISTINCT
                    [MaChungKhoan]
                    , [GiaSan]
                    , [GiaKhopLenh]
                    , [GiaThamChieu]
                FROM [BangDienFull]
                WHERE [MaxTime] = [ThoiGianKhopLenh]
                    AND [KhoiLuongKhopLenh] = [MaxKhoiLuongKhopLenh]
                    AND [GiaKhopLenh] = [MaxGiaKhopLenh]
            )
                    
            , [230007.Flex] AS (
                SELECT
                    [ticker]
                    , [system_total_room] [GeneralRoom]
                    , [system_used_room] [UsedSystemRoom]
                    , [total_special_room] [SpecialRoom]
                    , [used_special_room] [UsedSpecialRoom]
                FROM [DWH-CoSo].[dbo].[230007]
                WHERE [date] = '{dateString}'
            )
                    
            , [Result] AS (
                SELECT
                    [MarginList].[ticker_code] [Stock]
                    , CAST(ISNULL([BangDienRealTime].[GiaKhopLenh], 0) AS BIGINT) [MarketPrice]
                    , CAST(ISNULL([BangDienRealTime].[GiaThamChieu], 0) AS BIGINT) [ReferencePrice]
                    , CAST(ISNULL([MarginList].[MaxPrice], 0) AS BIGINT) [MaxPrice]
                    , ISNULL([MarginList].[Ratio], 0) [Ratio]
                    , CAST(ISNULL([230007.Flex].[GeneralRoom], 0) AS BIGINT) [GeneralRoom]
                    , CAST(ISNULL([230007.Flex].[UsedSystemRoom], 0) AS BIGINT) [UsedSystemRoom]
                    , CAST(ISNULL([230007.Flex].[SpecialRoom], 0) AS BIGINT) [SpecialRoom]
                    , CAST(ISNULL([230007.Flex].[UsedSpecialRoom], 0) AS BIGINT) [UsedSpecialRoom]
                    , ISNULL(([MarginList].[MaxPrice] / NULLIF([BangDienRealTime].[GiaKhopLenh], 0)) - 1, 0) [% MP/MarketPrice]
                    , ISNULL([230007.Flex].[UsedSystemRoom] / NULLIF([230007.Flex].[GeneralRoom], 0), 0) [% Used GR/ Approved GR]
                    , CAST(ISNULL(([230007.Flex].[GeneralRoom] - [UsedSystemRoom]) * [MarginList].[MaxPrice] * [MarginList].[Ratio], 0) AS BIGINT) [Remaining P.Outs]
                    , CASE
                        WHEN [GiaSan] = [GiaKhopLenh] THEN 1
                        ELSE 0
                    END [KiemTraGiamSan]
                FROM [MarginList]
                LEFT JOIN [BangDienRealTime]
                    ON [BangDienRealTime].[MaChungKhoan] = [MarginList].[ticker_code]
                LEFT JOIN [230007.Flex]
                    ON [230007.Flex].[ticker] = [MarginList].[ticker_code]
            )
                    
            SELECT *
            FROM [Result]
            WHERE 
                [% MP/MarketPrice] <= 0.05
                OR (
                    [% Used GR/ Approved GR] >= 0.85
                    AND [Remaining P.Outs] < 1.5e9
                )
            ORDER BY [Stock]
        '''
        self.__result = pd.read_sql(
            sql=statement,
            con=connect_DWH_CoSo
        )
        print(len(self.__result))

        return self.__result

    @property
    def runDate(self):
        return self.__runDate


class Liquidity3M(Query):

    def __init__(self):
        self.__result = None
        self.__runDate = None

    @property
    def result(self) -> pd.DataFrame:
        # Ngày chạy
        self.__runDate = dt.datetime(2023,6,16)
        dateString = self.__runDate.strftime('%Y-%m-%d')
        # lùi 1 ngày làm việc
        previousWorkDateString = BDATE(dateString, -1)
        previousWorkDate = dt.datetime.strptime(previousWorkDateString, '%Y-%m-%d')
        # chạy module warning_RMD_EOD
        self.__result = warning_RMD_EOD.run(run_time=previousWorkDate)
        return self.__result

    @property
    def runDate(self):
        return self.__runDate

