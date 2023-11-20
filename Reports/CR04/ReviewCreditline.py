import pandas as pd
from request import connect_DWH_CoSo
import datetime as dt
import xlsx_writer


class ReviewCreditline:
    def __init__(self):
        self._inputDate = dt.datetime(2023, 7, 25).strftime("%Y-%m-%d")

    def getData(self):
        df_query = pd.read_sql(f'''
        WITH [root] AS (
            SELECT 
                [relationship].[account_code], 
                [relationship].[sub_account], 
                [customer_name], [broker_name], 
                [branch_name], 
                [HanMucMarginDuocCap][mr_limit], 
                [HanMucTraChamDuocCap][dp_limit], 
                [HanMucMarginDuocCap]+[HanMucTraChamDuocCap][total_limit]
            FROM [VMR0004] 
                LEFT JOIN [relationship] ON [VMR0004].[TieuKhoan] = [relation'ship].[sub_account]
                AND [VMR0004].[Ngay] = [relationship].[date]
                LEFT JOIN [account] ON [relationship].[account_code] = [account].[account_code]
                LEFT JOIN [broker] ON [relationship].[broker_id] = [broker].[broker_id]
                LEFT JOIN [branch] ON [relationship].[branch_id] = [branch].[branch_id]
                LEFT JOIN [new_sub_account] ON [relationship].[sub_account] = [new_sub_account].[sub_account]
                LEFT JOIN [vcf0051] ON [relationship].[sub_account] = [vcf0051].[sub_account]
                AND [relationship].[date] = [vcf0051].[date]
            WHERE [vcf0051].[contract_type] LIKE '%MR%'
                AND [Ngay] = '{self._inputDate}'
                AND [open_date] < CAST(DATEADD(m, -6, '{self._inputDate}') as date)
        ),
        [mr_outstanding] AS (
            SELECT 
                [principal_outstanding]+[interest_outstanding]+[fee_outstanding][mr_outstanding], 
                [account_code]
            FROM [margin_outstanding]
            WHERE [date] = '{self._inputDate}'
                AND [type] LIKE 'Margin'
        ),
        [dp_outstanding] AS (
            SELECT 
                [principal_outstanding]+[interest_outstanding]+[fee_outstanding][dp_outstanding], 
                [account_code]
            FROM [margin_outstanding]
            WHERE [date] = '{self._inputDate}'
                AND [type] LIKE N'Trả chậm'
        ),
        [max_mr_outstanding] AS (
            SELECT 
                MAX([principal_outstanding]+[interest_outstanding]+[fee_outstanding])[max_mr_outstanding], 
                AVG([principal_outstanding]+[interest_outstanding]+[fee_outstanding])[avg_mr_outstanding], 
                [account_code]
            FROM [margin_outstanding]
            WHERE [date] BETWEEN  CAST(DATEADD(m, -6, '{self._inputDate}') as date) AND '{self._inputDate}'
                AND [type] LIKE 'Margin'
            GROUP BY [account_code]
        ),
        [max_dp_outstanding] AS (
            SELECT 
                MAX([principal_outstanding]+[interest_outstanding]+[fee_outstanding])[max_dp_outstanding],
                AVG([principal_outstanding]+[interest_outstanding]+[fee_outstanding])[avg_dp_outstanding], 
                [account_code]
            FROM [margin_outstanding]
            WHERE [date] BETWEEN  CAST(DATEADD(m, -6, '{self._inputDate}') as date) AND '{self._inputDate}'
                AND [type] LIKE N'Cầm cố'
            GROUP BY [account_code]
        ),
        [max_total_outstanding] AS (
            SELECT 
                MAX([principal_outstanding]+[interest_outstanding]+[fee_outstanding])[max_total_outstanding],
                AVG([principal_outstanding]+[interest_outstanding]+[fee_outstanding])[avg_total_outstanding], 
                [account_code]
            FROM [margin_outstanding]
            WHERE [date] BETWEEN  CAST(DATEADD(m, -6, '{self._inputDate}') as date) AND '{self._inputDate}'
            GROUP BY [account_code]
        ),
        [trading_value_6m] AS (
            SELECT 
                [sub_account], 
                MAX([value])[max_value_6m], 
                SUM([value])[total_value_6m]
            FROM [trading_record]
            WHERE [date] BETWEEN  CAST(DATEADD(m, -6, '{self._inputDate}') as date) AND '{self._inputDate}'
            GROUP BY [sub_account]
        ),
        [almost] AS (
            SELECT 
                [root].[account_code], 
                [root].[sub_account], 
                [customer_name], 
                [broker_name], 
                [branch_name], 
                [mr_outstanding], 
                [dp_outstanding], 
                [cash],
                ISNULL([mr_outstanding],0)+ISNULL([dp_outstanding],0)[total_outstanding], 
                [max_mr_outstanding],
                [max_dp_outstanding], 
                [max_total_outstanding],
                [avg_mr_outstanding],
                [avg_dp_outstanding], 
                [avg_total_outstanding], 
                [max_value_6m], 
                [total_value_6m],
                [max_mr_outstanding]/NULLIF([mr_limit],0) [mr_outstanding_over_limit],
                [max_dp_outstanding]/[dp_limit] [dp_outstanding_over_limit],
                [mr_limit],
                [dp_limit],
                [mr_limit]+[dp_limit][total_limit],
                CASE
                    WHEN [max_mr_outstanding]/NULLIF([mr_limit],0)*100 = 0 THEN 100
                    WHEN 0 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 10 THEN 0.9
                    WHEN 10 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 20 THEN 0.8
                    WHEN 20 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 30 THEN 0.7
                    WHEN 30 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 40 THEN 0.6
                    WHEN 40 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 50 THEN 0.50
                    ELSE 0
                END AS [mr_reduced],
                CASE
                    WHEN [max_dp_outstanding]/[dp_limit]*100 = 0 THEN 100
                    WHEN 0 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 10 THEN 0.9
                    WHEN 10 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 20 THEN 0.8
                    WHEN 20 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 30 THEN 0.7
                    WHEN 30 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 40 THEN 0.6
                    WHEN 40 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 50 THEN 0.5
                    ELSE 0
                END AS [dp_reduced],
                CASE
                    WHEN [max_mr_outstanding]/NULLIF([mr_limit],0)*100 = 0 THEN 0
                    WHEN 0 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 10 THEN [mr_limit]*(1-0.9)
                    WHEN 10 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 20 THEN [mr_limit]*(1-0.8)
                    WHEN 20 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 30 THEN [mr_limit]*(1-0.7)
                    WHEN 30 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 40 THEN [mr_limit]*(1-0.6)
                    WHEN 40 < [max_mr_outstanding]/NULLIF([mr_limit],0)*100 AND [max_mr_outstanding]/NULLIF([mr_limit],0)*100 <= 50 THEN [mr_limit]*(1-0.5)
                    ELSE [mr_limit]
                END AS [mr_suggest],
                CASE
                    WHEN [max_dp_outstanding]/[dp_limit]*100 = 0 THEN 0
                    WHEN 0 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 10 THEN [dp_limit]*(1-0.9)
                    WHEN 10 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 20 THEN [dp_limit]*(1-0.8)
                    WHEN 20 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 30 THEN [dp_limit]*(1-0.7)
                    WHEN 30 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 40 THEN [dp_limit]*(1-0.6)
                    WHEN 40 < [max_dp_outstanding]/[dp_limit]*100 AND [max_dp_outstanding]/[dp_limit]*100 <= 50 THEN [dp_limit]*(1-0.5)
                    ELSE [dp_limit]
                END AS [dp_suggest]
            FROM [root] 
                LEFT JOIN [mr_outstanding] ON [root].[account_code] = [mr_outstanding].[account_code]
                LEFT JOIN [dp_outstanding] ON [root].[account_code] = [dp_outstanding].[account_code]
                LEFT JOIN [RMR0062] ON [root].[account_code] = [RMR0062].[account_code]
                LEFT JOIN [max_mr_outstanding] ON [root].[account_code] = [max_mr_outstanding].[account_code]
                LEFT JOIN [max_dp_outstanding] ON [root].[account_code] = [max_dp_outstanding].[account_code]
                LEFT JOIN [max_total_outstanding] ON [root].[account_code] = [max_total_outstanding].[account_code]
                LEFT JOIN [trading_value_6m] ON [root].[sub_account] = [trading_value_6m].[sub_account]
            WHERE [RMR0062].[date] = '{self._inputDate}'
        )
        
        SELECT * ,
            CASE 
                WHEN [mr_suggest] = 0 AND [dp_suggest] = 0 THEN 'Cut MR&DP limit'
                WHEN [mr_suggest] NOT IN (0,[mr_limit]) AND [dp_suggest] NOT IN (0,[dp_limit]) THEN 'Reduce MR&DP limit'
                WHEN [mr_suggest] = [mr_limit] AND [dp_suggest] = [dp_limit] THEN 'Keep all like the current'
                ELSE 'Cut/reduce/keep MR and/or DP limit'
            END AS [rmd_suggestion]
        FROM [almost]
        ''', connect_DWH_CoSo)
        df_query['No'] = [i for i in range(1, len(df_query) + 1)]
        return df_query


if __name__ == '__main__':
    obj = ReviewCreditline()
    df = obj.getData()
    writer = xlsx_writer.ExcelWriter()
    writer.data = df
    writer.data.fillna("", inplace=True)
    writer.writeReport()


