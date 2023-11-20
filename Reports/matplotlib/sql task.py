from datawarehouse import connect_DWH_CoSo
from datetime import datetime
import pandas as pd
base = datetime.strptime('2019-01-01', '%Y-%m-%d')
lst = pd.date_range(base, periods=1506).to_pydatetime().tolist()
new_list=[]
for i in lst:
    if i.day == 1:
        new_list.append(i)
for i in new_list:
    df = pd.read_sql(
        f'''
        SELECT date Ngay, sub_account TieuKhoan, interest Lai 
        FROM [rln0019] 
        WHERE MONTH([date]) LIKE '{str(i.month)}' AND YEAR([date]) LIKE '{str(i.year)}'
    ''', connect_DWH_CoSo)
    df.to_excel(f'{i.strftime("%Y-%m-%d")}.xlsx')
    print(i.strftime("%Y-%m-%d"))