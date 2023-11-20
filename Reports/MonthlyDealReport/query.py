import pandas as pd
from request import connect_DWH_CoSo, connect_DWH_ThiTruong
import datetime as dt
import os
import re
from dateutil.parser import parse
from datawarehouse import BDATE
from xlsx_writer import ExcelWriter
from warning.warning_RMD_EOD import run


class SummaryInformation:
    def __init__(self):
        self._startDate = None
        self._endDate = None

    @property
    def start_date(self):
        return self._startDate

    @property
    def end_date(self):
        return self._endDate

    @start_date.setter
    def start_date(self, start: str):
        self._startDate = dt.datetime.strptime(start, '%d/%m/%Y').strftime('%Y-%m-%d')

    @end_date.setter
    def end_date(self, end: str):
        self._endDate = dt.datetime.strptime(end, '%d/%m/%Y').strftime('%Y-%m-%d')

    '''
    Hàm này để tìm ra file nào là file ngày gần nhất trong shared folder của Risk
    Trong shared folder để lấy file gốc chứa nhiều file có dạng Report RMR0035 dd.mm.yyyy.xlsx
    '''
    @staticmethod
    def find_the_lastest(input_file_list):
        results = []
        for i in input_file_list:
            result = re.search('\d*\.\d*\.\d{4}', i)
            if result:
                results.append(result.group())
        the_max_date = max([parse(x) for x in results]).strftime("%d.%m.%Y")
        return the_max_date

    def getData(self):
        # đọc file
        now = dt.datetime.now()
        month = '{:02d}'.format(now.month)
        # directory = f"\\\\192.168.10.101\phs-storge-2018\RiskManagementDept\RMD_Data\Luu tru van ban\Daily Report\\04. High Risk & Liquidity\High Risk\\{now.year}\\{month}.{now.year}\\"
        directory = fr"C:\Users\quangpham\Desktop\CR06\\"
        dir_list = os.listdir(directory)
        the_lastest_date = self.find_the_lastest(dir_list)
        # risk_root_table = pd.read_excel(directory + f'Report RMR0035 {the_lastest_date}.xlsx', sheet_name='Special room_Gốc')[['MãRoom', 'Account', 'MãCK']]
        risk_root_table = pd.read_excel(directory + f'Report RMR0035 30.06.2023.xlsx', sheet_name='Special room_Gốc')[['MãRoom', 'Account', 'MãCK']]
        # phần data lấy ra từ db và merge với bảng gốc bằng account_code
        df_account_related = pd.read_sql(f'''
            WITH [sub_account] AS (
                SELECT [TieuKhoan] [sub_account], [branch_name] [location], [relationship].[account_code]
                FROM [VMR0004] LEFT JOIN [relationship] 
                    ON [VMR0004].[Ngay] = [relationship].[date] 
                    AND [VMR0004].[TieuKhoan] = [relationship].[sub_account] 
                    LEFT JOIN [branch] ON [relationship].[branch_id] = [branch].[branch_id]
                    LEFT JOIN [vcf0051] ON [relationship].[sub_account] = [vcf0051].[sub_account]
                    AND [relationship].[date] = [vcf0051].[date]
                WHERE [vcf0051].[contract_type] LIKE '%MR%'
                AND [Ngay] = '{self.end_date}'
            ),
            [cash] AS (
                SELECT [account_code],[cash]
                FROM [RMR0062]
                WHERE [date] = '{self.end_date}'
                AND [margin_value] != 0
            ),
            [value_for_all] AS (
                SELECT [sub_account], SUM([market_value]) [market_value]
                FROM [rmr0015]
                WHERE [date] = '{self.end_date}'
                GROUP BY [sub_account]
            ),
            [outstanding] AS(
                SELECT [account_code], [principal_outstanding], [interest_outstanding], ([principal_outstanding]+[interest_outstanding])[total_outstanding]
                FROM [margin_outstanding]
                WHERE [date] = '{self.end_date}'
                AND [type] IN ('Margin','Trả chậm','Bảo lãnh')
            ),
            [account_trading_value] AS (
                SELECT [vcf0051].[sub_account], SUM([value])[trading_value_of_account], SUM([fee])[trading_fee_of_account]
                FROM [trading_record] LEFT JOIN [vcf0051] ON [trading_record].[sub_account] = [vcf0051].[sub_account]
                AND [trading_record].[date] = [vcf0051].[date]
                WHERE [trading_record].[date] BETWEEN '{self.start_date}' AND '{self.end_date}'
                AND [vcf0051].[contract_type] LIKE 'MR%'
                GROUP BY [vcf0051].[sub_account]
            )
            SELECT [sub_account].[account_code],[sub_account].[sub_account], [sub_account].[location], [cash][total_cash],
            [value_for_all].[market_value][market_value_for_all_stocks], [principal_outstanding], [interest_outstanding], [total_outstanding], [trading_value_of_account],
            [trading_fee_of_account]
            FROM [sub_account] 
            LEFT JOIN [cash] ON [sub_account].[account_code] = [cash].[account_code]
            LEFT JOIN [outstanding] ON [sub_account].[account_code] = [outstanding].[account_code]
            LEFT JOIN [value_for_all] ON [sub_account].[sub_account] = [value_for_all].[sub_account]
            LEFT JOIN [account_trading_value] ON [sub_account].[sub_account] = [account_trading_value].[sub_account]
        ''', connect_DWH_CoSo)
        risk_root_table = risk_root_table.merge(df_account_related, left_on=['Account'], right_on=['account_code'], how='left')

        # phần data lấy từ db merge với bảng gốc thông qua ticker
        df_ticker_related = pd.read_sql(f'''
            WITH [value_for_one] AS(
                SELECT [sub_account], [ticker], SUM([market_value])[market_value]
                FROM [rmr0015]
                WHERE [date] = '{self.end_date}'
                GROUP BY [sub_account], [ticker]
            ),
            [quantity] AS (
                SELECT (SUM([trading_volume])+ SUM([receiving_volume]))[quantity], [sub_account], [ticker]
                FROM [VMR9004]
                WHERE [date] = '{self.end_date}'
                GROUP BY [sub_account], [ticker]
            ),
            [stock_trading_value] AS (
                SELECT [trading_record].[ticker], SUM([value])[trading_value_of_stock]
                FROM [trading_record] LEFT JOIN [vcf0051] ON [trading_record].[sub_account] = [vcf0051].[sub_account]
                AND [trading_record].[date] = [vcf0051].[date]
                WHERE [trading_record].[date] BETWEEN '{self.start_date}' AND '{self.end_date}'
                AND [vcf0051].[contract_type] LIKE 'MR%'
                GROUP BY [trading_record].[ticker]
            )
            SELECT [value_for_one].[market_value][market_value_of_this_stock], [trading_value_of_stock], [value_for_one].[ticker], [value_for_one].[sub_account], [quantity].[quantity]
            FROM [value_for_one] LEFT JOIN [stock_trading_value] ON [value_for_one].[ticker] = [stock_trading_value].[ticker]
            LEFT JOIN [quantity] ON [quantity].[ticker] = [value_for_one].[ticker] AND [quantity].[sub_account] = [value_for_one].[sub_account]
        ''', connect_DWH_CoSo)
        risk_root_table = risk_root_table.merge(df_ticker_related, left_on=['MãCK', 'sub_account'], right_on=['ticker', 'sub_account'], how='left')

        # phần data từ dữ liệu giao dịch ngày trong DWH thị trường
        df_closed_price = pd.read_sql(f'''
            SELECT [Ticker], [Close]*1000 [Close]
            FROM [DuLieuGiaoDichNgay]
            WHERE [Date] = '{BDATE(self.end_date, -1)}'
        ''', connect_DWH_ThiTruong)
        risk_root_table = risk_root_table.merge(df_closed_price, left_on=['MãCK'], right_on=['Ticker'], how='left')

        # xóa cột thừa do hàm merge
        risk_root_table = risk_root_table.drop(['account_code', 'ticker', 'Ticker'], axis=1)

        # đổi tên location thành tiếng anh
        mapping = {
            'Hải Phòng': 'Hai Phong',
            'Tân Bình': 'Tan Binh',
            'Hà Nội': 'Ha Noi',
            'Quận 1': 'District 1',
            'Phú Mỹ Hưng': 'Phu My Hung',
            'Quận 3': 'District 3',
            'Thanh Xuân': 'Thanh Xuan',
            'Quận 7': 'District 7',
            'Phòng Giao Dịch trực tuyến': 'Internet Broker',
            'Phòng Quản lý tài khoản - 01': 'AMD01',
            'Phòng Quản lý tài khoản - 05': 'AMD05',
            'Phòng Khách hàng tổ chức - 01': 'Institutional Business 01',
            'Phòng Khách hàng tổ chức - 02': 'Institutional Business 02'
        }
        risk_root_table['location'] = [mapping.get(i) if mapping.get(i) is not None else i for i in risk_root_table['location']]
        risk_root_table['MãRoom'] = pd.to_numeric(risk_root_table['MãRoom'])
        risk_root_table.sort_values(by=['MãRoom', 'MãCK'], inplace=True)
        return risk_root_table


class MonthlyDealReport:

    def __init__(self, df_summary_information):
        self._endDate = None
        # bảng này lấy từ phần 1
        self.summaryInformation = df_summary_information[['MãCK', 'MãRoom', 'Close', 'location', 'quantity', 'Account',
        'total_outstanding', 'total_cash', 'market_value_for_all_stocks', 'market_value_of_this_stock',
        'trading_value_of_account', 'trading_value_of_stock']]

    @property
    def end_date(self):
        return self._endDate

    @end_date.setter
    def end_date(self, end: str):
        self._endDate = dt.datetime.strptime(end, '%d/%m/%Y').strftime('%Y-%m-%d')

    # cột lấy từ bảng warning
    @staticmethod
    def getDataFromWarning():
        return run()[['Stock', '3M Avg. Volume']]

    def getData(self):
        # phần data lấy từ db coso
        risk_root_table = pd.read_sql(fr'''
        WITH [root] AS (
            SELECT [room_code], [ticker], [total_volume], [used_volume]
            FROM [VPR0108]
            LEFT JOIN [DataHop] ON [VPR0108].[ticker] = [DataHop].[MaChungKhoan]
            WHERE [total_volume] != 0
            AND [date] = '{self.end_date}'
        ),
        [cl01_basket] AS (
            SELECT [ticker_code], [margin_ratio][mr_ratio], [margin_max_price]
            FROM VPR0109
            WHERE [date] = '{self.end_date}'
            AND [room_code] = 'CL01_PHS'
        ),
        [tc01_basket] AS (
            SELECT [ticker_code], [margin_ratio][dp_ratio]
            FROM VPR0109
            WHERE [date] = '{self.end_date}'
            AND [room_code] = 'TC01_PHS'
        )
        SELECT [room_code], [ticker], [total_volume], [used_volume], [mr_ratio], [dp_ratio], [margin_max_price], [Nganh][sector]
        FROM [root]
        LEFT JOIN [cl01_basket] ON [root].[ticker] = [cl01_basket].[ticker_code]
        LEFT JOIN [tc01_basket] ON [root].[ticker] = [tc01_basket].[ticker_code]
        LEFT JOIN [DataHop] ON [root].[ticker] = [DataHop].[MaChungKhoan]
            ''', connect_DWH_CoSo)
        risk_root_table['room_code'] = pd.to_numeric(risk_root_table['room_code'])
        # merge vào bảng phần 1
        risk_root_table = risk_root_table.merge(self.summaryInformation, left_on=['ticker','room_code'], right_on=['MãCK', 'MãRoom'], how='left')
        # merge vào bảng warning
        risk_root_table = risk_root_table.merge(self.getDataFromWarning(), left_on=['ticker'], right_on=['Stock'], how='left')
        # tính 2 cột break even price min max
        sub_table = risk_root_table[['total_outstanding','total_cash','market_value_of_this_stock','market_value_for_all_stocks','quantity','MãRoom']].copy()
        sub_table['market_value_of_other_stocks'] = sub_table['market_value_for_all_stocks'] - sub_table['market_value_of_this_stock']
        sub_table['break_even_price'] = (sub_table['total_outstanding'] - sub_table['total_cash'] - sub_table['market_value_of_other_stocks'])/sub_table['quantity']
        df_max = sub_table[['break_even_price', 'MãRoom']].groupby('MãRoom', group_keys=False).max().reset_index()
        df_max.rename(columns={'break_even_price': 'break_even_price_max'}, inplace=True)
        df_max['break_even_price_max'][df_max['break_even_price_max'] < 0] = 0
        df_min = sub_table[['break_even_price', 'MãRoom']].groupby('MãRoom', group_keys=False).min().reset_index()
        df_min.rename(columns={'break_even_price': 'break_even_price_min'}, inplace=True)
        df_min['break_even_price_min'][df_min['break_even_price_min'] < 0] = 0
        risk_root_table = risk_root_table.merge(df_max, left_on=['MãRoom'], right_on=['MãRoom'], how='left')
        risk_root_table = risk_root_table.merge(df_min, left_on=['MãRoom'], right_on=['MãRoom'], how='left')
        # tính cột p.outs net cash
        sub_table['p.outs_net_cash'] = sub_table['total_outstanding'] - sub_table['total_cash']
        df_p_outs = sub_table[['p.outs_net_cash', 'MãRoom']].groupby('MãRoom', group_keys=False).sum().reset_index()
        risk_root_table = risk_root_table.merge(df_p_outs, left_on=['MãRoom'], right_on=['MãRoom'], how='left')
        # tính cột p.outs MATV
        risk_root_table['MATV'] = risk_root_table['trading_value_of_account']/risk_root_table['p.outs_net_cash']
        # risk_root_table = risk_root_table.groupby(by=["Account", "ticker"], as_index=False).first()
        risk_root_table.sort_values(by=['room_code', 'ticker'], inplace=True)
        risk_root_table['No'] = [i for i in range(1, len(risk_root_table) + 1)]
        return risk_root_table


if __name__ == '__main__':
    smrInfor = SummaryInformation()
    df = smrInfor.getData()
    writer = ExcelWriter()
    writer.data1 = df
    mthReport = MonthlyDealReport(df)
    df2 = mthReport.getData()
    writer.data2 = df2
    writer.data1.fillna("", inplace=True)
    writer.data2.fillna("", inplace=True)
    writer.writeFullReport()

