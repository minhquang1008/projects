from data import *
import re
from bs4 import BeautifulSoup
from win32com.client import Dispatch
import numpy as np
from job import ExcelWriter


def __CheckAbnormal__(func):

    """
    This function send an emailn when there is any abnormal row in the report
    """

    def wrapper(*args, **kwargs):

        fullTable = func(*args, **kwargs)
        abnormalTable = fullTable[0]

        if not abnormalTable.empty:
            abnormalTable = abnormalTable.rename({
                'MarketPrice': 'Market price',
                'ReferencePrice': 'Reference Price',
                'MaxPrice': 'Max Price',
                'GeneralRoom': 'General Room',
                'UsedSystemRoom': 'Used System Room',
                'SpecialRoom': 'Special Room',
                'UsedSpecialRoom': 'Used Special Room',
                'KiemTraGiamSan': 'Kiem Tra Giam San',
                '% MP/MarketPrice': '% MP/ Market Price'
            }, axis=1)

            abnormalTable[['% MP/ Market Price','% Used GR/ Approved GR','Ratio']] = abnormalTable[['% MP/ Market Price','% Used GR/ Approved GR','Ratio']]*100
            abnormalTable['Ratio'] = abnormalTable['Ratio'].astype('int64')

            def build_formatters(df, format):
                return {
                    column: format
                    for column, dtype in df.dtypes.items()
                    if dtype in [np.dtype('int64')]
                }

            num_format = lambda x: '{0:,.0f}'.format(x)
            formatters = build_formatters(abnormalTable, num_format)
            abnormalHTML = abnormalTable.to_html(formatters=formatters, index=False,header=True,float_format=lambda x: '{0:,.2f}'.format(x)).replace("\\n","<br>")
            abnormalHTML = re.sub('<th>Kiem Tra Giam San</th>', '', abnormalHTML)
            # abnormalHTML = re.sub('<th>Market price</th>', '', abnormalHTML)
            # abnormalHTML = re.sub('<th>Reference Price</th>', '', abnormalHTML)
            # abnormalHTML = re.sub('<th>% MP/ Market Price</th>', '', abnormalHTML)
            # abnormalHTML = re.sub('<th>3M Avg. Volume</th>', '', abnormalHTML)
            abnormalHTML = re.sub('<th>', '<th style="color: White;border: 1px solid Black;background-color:#548235"; border-color: Black;>', abnormalHTML)
            abnormalHTML = re.sub('<table border="1" class="dataframe">', '<table border="1" bgcolor="HoneyDew" style="border: 1px solid Black;border-collapse:collapse;" class="dataframe">', abnormalHTML)
            abnormalHTML = re.sub('<td>', '<td style="text-align: center;border: 1px solid Black;">', abnormalHTML)
            soup = BeautifulSoup(abnormalHTML, 'html.parser')
            for i in soup.find_all('tr')[1:]:
                if int(float(re.search('\d', i.find_all('td')[-3].string).group())) == 1:
                    i.find_all('td')[0].string.wrap(soup.new_tag('td bgcolor = HoneyDew font color=Yellow style="font-weight:bold; color: Red; text-align: center;border: 1px solid Black;"'))
                    i.find_all('td')[1].string.wrap(soup.new_tag('td bgcolor = HoneyDew font color=Yellow style="font-weight:bold; color: Red; text-align: center;border: 1px solid Black;"'))
                if int(float(re.search('-?\d+.\d\d', i.find_all('td')[-6].string).group())) <= 5:
                    i.find_all('td')[-6].string.wrap(soup.new_tag('td bgcolor = Yellow font color=Yellow style="font-weight:bold; color: Red; text-align: center;border: 1px solid Black;"'))
                    i.find_all('td')[3].string.wrap(soup.new_tag('td bgcolor = Yellow font color=Yellow style="font-weight:bold; color: Red; text-align: center;border: 1px solid Black;"'))
                if int(float(re.search('\d+.\d\d', i.find_all('td')[-5].string).group())) >= 85:
                    i.find_all('td')[-5].string.wrap(soup.new_tag(
                        'td bgcolor = Yellow font color=Yellow style="font-weight:bold; color: Red; text-align: center;border: 1px solid Black;"'))
                if int(float(re.search('(\d+,?)+', i.find_all('td')[-4].string).group().replace(',', ''))) < 1.5e9:
                    i.find_all('td')[-4].string.wrap(soup.new_tag('td bgcolor = HoneyDew font color=Yellow style="font-weight:bold; color: Red; text-align: center;border: 1px solid Black;"'))
                i.find_all('td')[-3].replaceWith('')
                # i.find_all('td')[-2].replaceWith('')
                # i.find_all('td')[1].replaceWith('')
                # i.find_all('td')[2].replaceWith('')
                # i.find_all('td')[-6].replaceWith('')
            abnormalHTML = soup.prettify()
            abnormalHTML = re.sub('''<td style="text-align: center;border: 1px solid Black;">
    <td bgcolor''', '<td bgcolor', abnormalHTML)
            abnormalHTML = re.sub('</td bgcolor = Yellow font color=Yellow style="color: Red; text-align: center;border: 1px solid Black;">',
                                  '', abnormalHTML)
            html_str = f"""
            <html>
                <head></head>
                <body>
                    {abnormalHTML}
                    <p style="font-family:Times New Roman; font-size:90%"><i>
                        -- Generated by Reporting System
                    </i></p>
                </body>
            </html>
            """
            outlook = Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.To = 'quangpham@phs.vn'
            # mail.To = 'anhnguyenthu@phs.vn;anhhoang@phs.vn;huyhuynh@phs.vn;phuhuynh@phs.vn'
            # mail.CC = 'namtran@phs.vn;quangpham@phs.vn'
            # mail.To = 'anhhoang@phs.vn'
            mail.Subject = f"Cảnh báo ngày {dt.datetime.now().strftime('%d.%m.%Y')}"
            mail.HTMLBody = html_str
            attachment = fullTable[1]
            mail.Attachments.Add(attachment)
            mail.Send()
    return wrapper


@__CheckAbnormal__
def run():
    dataFromDB = WarningMonitorStock().result
    dataFromWarningRMDEOD = Liquidity3M().result

    finalTable = pd.merge(
        left=dataFromDB,
        right=dataFromWarningRMDEOD[['Stock', '3M Avg. Volume']],
        how='left',
        on='Stock'
    )
    check_list = pd.read_excel('Fixed MP List.xlsx')['Fix list'].to_list()
    finalTable['Note'] = ['Fixed' if k in check_list else '' for k in [i for i in finalTable['Stock']]]
    writeExcel = ExcelWriter()
    writeExcel.inputData = finalTable
    writeExcel.writeToExcel()

    return finalTable, writeExcel.pathToAttachFile


# vpr = pd.read_sql('''
#     SELECT * FROM [vpr0109]
#     WHERE [date] = CAST(GETDATE() AS Date)
# ''', connect_DWH_CoSo)
# vpr.to_excel('C:\\Users\\quangpham\\Desktop\\vpr_file.xlsx')
#
# vpr = pd.read_sql('''
#     SELECT * FROM [230007]
#     WHERE [date] = CAST(GETDATE() AS Date)
# ''', connect_DWH_CoSo)
# vpr.to_excel('C:\\Users\\quangpham\\Desktop\\230007_file.xlsx')


# itr = ['01','02','03','04','05','06','07','08','09','10','11','12']
# for i in itr:
#     data = pd.read_sql(f'''
#     select * from [relationship]
#     where YEAR([date]) = '2018' and MONTH([date]) = '{i}'
#     ''',connect_DWH_CoSo)
#     data.to_pickle(f'C:\\Users\\quangpham\\Desktop\\relationship\\{i}-2018.pickle')


run()
