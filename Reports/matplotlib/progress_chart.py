import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def findOrdinalNumber(date: str):
    # connection
    user = 'quang'
    password = ''
    driver_DWH_CoSo = '{SQL Server}'
    server_DWH_CoSo = 'SRV-RPT'
    db_DWH_CoSo = 'DWH-CoSo'
    connect_DWH_CoSo = pyodbc.connect(
        f'Driver={driver_DWH_CoSo};'
        f'Server={server_DWH_CoSo};'
        f'Database={db_DWH_CoSo};'
        f'uid={user};'
        f'pwd={password}'
    )
    test_date = datetime.strptime(date, '%Y-%m-%d')
    # query
    df = pd.read_sql(
        f'''
        SELECT * FROM [Date]
        WHERE MONTH([Date]) LIKE '{test_date.month}' AND 
        YEAR([Date]) LIKE'{test_date.year}' AND 
        [Work] = 1
        ''', connect_DWH_CoSo)
    df = df.sort_values('Date', ignore_index=True)
    test_date_list = df['Date']
    closest_dict = {
      (test_date - date).days: date
      for date in test_date_list}
    res = closest_dict[min([i for i in closest_dict.keys() if i >= 0])]
    passed_days = df['Date'][df['Date'] == res].index.item()+1
    working_days = len(df)
    return passed_days, working_days


def drawProgressChart(date: str):
    passed_days, working_days = findOrdinalNumber(date)
    remaining_days = working_days - passed_days
    df = pd.DataFrame([[passed_days, remaining_days]], columns=['passed', 'remaining'])
    passed_days = df['passed'].iloc[0]
    remaining_days = df['remaining'].iloc[0]
    color = ['#1d40cc', '#FF7700']
    plot = df.plot(
        kind='barh',
        stacked=True,
        title='days have passed',
        legend=False,
        mark_right=True,
        figsize=(12,0.75))
    plt.text(passed_days/2, 0 , passed_days,
             va='center', ha='center', color='#fcfdfe', fontsize=14)
    plt.text((passed_days*2+remaining_days)/2, 0, remaining_days,
             va='center', ha='center', color='#fcfdfe', fontsize=14)
    fig = plot.get_figure()
    plt.axis('off')
    return fig

#--------TEST----------------------------------
fig = drawProgressChart('2023-02-22')
fig.show()