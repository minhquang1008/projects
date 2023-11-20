import pandas as pd
from request import connect_DWH_CoSo


# sql_data = pd.read_sql('''
#     WITH TEMP1 AS (
#         SELECT [TieuKhoan] [sub_account], [branch_name] [location], [relationship].[account_code]
#         FROM [VMR0004] LEFT JOIN [relationship]
#             ON [VMR0004].[Ngay] = [relationship].[date]
#             AND [VMR0004].[TieuKhoan] = [relationship].[sub_account]
#             LEFT JOIN [branch]
#             ON [relationship].[branch_id] = [branch].[branch_id]
#             LEFT JOIN [vcf0051] ON [relationship].[sub_account] = [vcf0051].[sub_account]
#                 AND [relationship].[date] = [vcf0051].[date]
#         WHERE [vcf0051].[contract_type] LIKE '%MR%'
#         AND [Ngay] = CAST(GETDATE()  AS date)
#     ),
#     TEMP2 AS (
#         SELECT [vcf0051].[sub_account], SUM([value])[trading_value_of_account], SUM([fee])[trading_fee_of_account]
#         FROM [trading_record] LEFT JOIN [vcf0051] ON [trading_record].[sub_account] = [vcf0051].[sub_account]
#         AND [trading_record].[date] =  [vcf0051].[date]
#         WHERE [trading_record].[date] BETWEEN '2023-04-27' AND '2023-07-27'
#         AND [vcf0051].[contract_type] LIKE 'MR%'
#         GROUP BY [vcf0051].[sub_account]
#     )
#
#     SELECT [account_code], [trading_value_of_account], [trading_fee_of_account]
#     FROM [TEMP1] LEFT JOIN [TEMP2] ON [TEMP1].[sub_account] = [TEMP2].[sub_account]
# ''', connect_DWH_CoSo)
#
# root = pd.read_excel(r'C:\Users\quangpham\Downloads\Ac 28.07.xlsx')
# root = root.merge(sql_data, left_on=['Account'], right_on=['account_code'], how='left')
# root.to_excel(r'C:\Users\quangpham\Desktop\root.xlsx')


# data = pd.read_sql('''
# select * from [new_sub_account]
# ''', connect_DWH_CoSo)
# data.to_excel(r'C:\Users\quangpham\Desktop\rcf0001.xlsx')

import os
lst = [i.split('_')[1] for i in os.listdir(r'C:\Users\quangpham\Desktop\support Vy\CS Q7')[0:-1]]
print(lst)
df = pd.DataFrame([])
df['name'] = lst
df.to_excel(r'C:\Users\quangpham\Desktop\dffd.xlsx')
