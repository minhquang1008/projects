import pandas as pd
import datetime as dt
import os

from os.path import join, dirname, realpath


class ExcelWriter:

    def __init__(self):
        self.__today = dt.datetime.now()
        self.__data = None
        self.__destinationDir = fr"C:\Users\quangpham\Shared Folder\Risk Management\Monitor Stock"

        self.__yearString = str(self.__today.year)
        if self.__today.month > 9:
            mStr = f'{self.__today.month}'
        else:
            mStr = f'0{self.__today.month}'
        self.__monthString = f'T{mStr}'
        self.__dateString = dt.datetime.now().strftime('%d.%m.%Y')

        # create 'year' folder
        if not os.path.isdir(join(self.__destinationDir, self.__yearString)):
            os.mkdir((join(self.__destinationDir, self.__yearString)))
        # create 'month' folder
        if not os.path.isdir(join(self.__destinationDir, self.__yearString, self.__monthString)):
            os.mkdir((join(self.__destinationDir, self.__yearString, self.__monthString)))
        # create 'date' folder in date folder
        if not os.path.isdir(join(self.__destinationDir, self.__yearString, self.__monthString, self.__dateString)):
            os.mkdir((join(self.__destinationDir, self.__yearString, self.__monthString, self.__dateString)))

        self.__filePath = None

    # @property
    # def inputData(self):
    #     if self.__data is None:
    #         raise ValueError('No data to write!')
    #     return self.__data

    # @inputData.setter
    # def inputData(self, value: pd.DataFrame):
    #     self.__data = value

    @property
    def pathToAttachFile(self):
        return self.__filePath

    def writeToExcel(self):

        hour = self.__today.hour
        minute = self.__today.minute
        dateString = self.__today.strftime("%d.%m.%Y")
        fileName = f"Monitor Stock {dateString} - {hour}h{minute}.xlsx"
        self.__filePath = join(self.__destinationDir, self.__yearString, self.__monthString, self.__dateString, fileName)
        result = self.inputData

        writer = pd.ExcelWriter(
            self.__filePath,
            engine='xlsxwriter',
            engine_kwargs={'options': {'nan_inf_to_errors': True}}
        )

        workbook = writer.book
        worksheet = workbook.add_worksheet('Monitor Stock')
        worksheet.hide_gridlines(option=2)

        # format
        headerFormat = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 12,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#548235',
            'font_color': '#FFFFFF',
        })

        textFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        priceFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
        })

        priceSpecialFormatBgBold = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
            'bold': True,
            'bg_color': '#FFFF00',
            'font_color': '#FF0000',
        })

        priceSpecialFormatNoBgBold = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
            'bold': True,
            'font_color': '#FF0000',
        })

        priceSpecialFormatNoBgNoBold = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
            'font_color': '#FF0000',
        })

        textSpecialFormatNoBg = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_color': '#FF0000',
        })

        percentFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'num_format': '0.00%',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'
        })

        percentSpecialFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'bold': True,
            'font_size': 12,
            'num_format': '0.00%',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#FFFF00',
            'font_color': '#FF0000'
        })

        percentRatioFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'num_format': '0%',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:C', 20)
        worksheet.set_column('D:E', 15)
        worksheet.set_column('F:I', 15)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:N', 20)

        headers = [
            'Stock',
            'Market price',
            'Reference price',
            'Max price',
            'Ratio',
            'General room',
            'Used system room',
            'Special room',
            'Used special room',
            '% MP / Market price',
            '% Used GR / Approved GR',
            'Liquidity within 03 months',
            'Remaining P.Outs',
            'Note'
        ]
        # write
        worksheet.write_row('A1', headers, headerFormat)
        worksheet.write_column('A2', result['Stock'], textFormat)
        worksheet.write_column('B2', result['MarketPrice'], priceFormat)
        worksheet.write_column('C2', result['ReferencePrice'], priceFormat)
        worksheet.write_column('D2', result['MaxPrice'], priceFormat)
        worksheet.write_column('E2', result['Ratio'], percentRatioFormat)
        worksheet.write_column('F2', result['GeneralRoom'], priceFormat)
        worksheet.write_column('G2', result['UsedSystemRoom'], priceFormat)
        worksheet.write_column('H2', result['SpecialRoom'], priceFormat)
        worksheet.write_column('I2', result['UsedSpecialRoom'], priceFormat)
        worksheet.write_column('J2', result['% MP/MarketPrice'], percentFormat)
        worksheet.write_column('K2', result['% Used GR/ Approved GR'], percentFormat)
        worksheet.write_column('L2', result['3M Avg. Volume'], priceFormat)
        worksheet.write_column('M2', result['Remaining P.Outs'], priceFormat)
        worksheet.write_column('N2', result['Note'], textFormat)

        alphabet = 'ABCDEFGHIJKLM'

        for idx in result.index:
            stock = result.loc[idx, 'Stock']
            marketPrice = result.loc[idx, 'MarketPrice']
            maxPrice = result.loc[idx, 'MaxPrice']
            pctMPDivMarketPrice = result.loc[idx, '% MP/MarketPrice']
            pctUsedGRDivApprovedGR = result.loc[idx, '% Used GR/ Approved GR']
            remainingPOuts = result.loc[idx, 'Remaining P.Outs']
            checkFloor = result.loc[idx, 'KiemTraGiamSan']

            # trường hợp các mã chạm sàn
            if checkFloor == 1:
                worksheet.write(idx + 1, alphabet.index('A'), stock, textSpecialFormatNoBg)
                worksheet.write(idx + 1, alphabet.index('B'), marketPrice, priceSpecialFormatNoBgNoBold)
            # trường hợp % MP/MarketPrice <= 5%
            if pctMPDivMarketPrice <= 5/100:
                worksheet.write(idx + 1, alphabet.index('J'), pctMPDivMarketPrice, percentSpecialFormat)
                worksheet.write(idx + 1, alphabet.index('D'), maxPrice, priceSpecialFormatBgBold)
            # trường hợp % Used GR/ Approved GR >= 85%
            if pctUsedGRDivApprovedGR >= 85/100:
                worksheet.write(idx + 1, alphabet.index('K'), pctUsedGRDivApprovedGR, percentSpecialFormat)
            # trường hợp Remaining P.Outs < 1.5 tỷ
            if 0 < remainingPOuts < 1.5e9:
                worksheet.write(idx + 1, alphabet.index('M'), remainingPOuts, priceSpecialFormatNoBgBold)

        writer.close()

    def writeFullReport(self):

        hour = self.__today.hour
        minute = self.__today.minute
        dateString = self.__today.strftime("%d.%m.%Y")
        fileName = f"Final report {dateString} - {hour}h{minute}.xlsx"
        self.__filePath = join(self.__destinationDir, self.__yearString, self.__monthString, self.__dateString, fileName)
        # result = self.inputData

        writer = pd.ExcelWriter(
            self.__filePath,
            engine='xlsxwriter',
            engine_kwargs={'options': {'nan_inf_to_errors': True}}
        )

        workbook = writer.book
        worksheet = workbook.add_worksheet('MP < Market price')
        worksheet.hide_gridlines(option=2)

        # format
        headerFormat = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 12,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFFFFF',
            'font_color': '#000000',
        })

        textFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        priceFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
        })

        priceSpecialFormatBgBold = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
            'bold': True,
            'bg_color': '#FFFF00',
            'font_color': '#FF0000',
        })

        priceSpecialFormatNoBgBold = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
            'bold': True,
            'font_color': '#FF0000',
        })

        priceSpecialFormatNoBgNoBold = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
            'font_color': '#FF0000',
        })

        textSpecialFormatNoBg = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_color': '#FF0000',
        })

        percentFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'num_format': '0.00%',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'
        })

        percentSpecialFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'bold': True,
            'font_size': 12,
            'num_format': '0.00%',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#FFFF00',
            'font_color': '#FF0000'
        })

        percentRatioFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 12,
            'num_format': '0%',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:C', 15)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:G', 15)
        worksheet.set_column('H:I', 12)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:AT', 15)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 30)
        worksheet.set_row(2, 80)

        headers = [
            'Abbreviation: SR: special room; GR: general room; MP: max price; RP:Reference price; BP:Breakeven price; MC:Market Cap; AV:Average Volume',
            '','','','',
            'PRICE','','','','',
            'BREAKEVEN PRICE','','','','','','',
            'MARKET INFORMATION', '','','','','',
            'Liquidity of 3 months','','','',
            'RATIO','','','',
            'ROOM','','','','','','','',
            'Total potential outstanding','',''
        ]

        subheaders1 = [
            '', '', '', '', '', '','', '', '', '','','',
            'Based on P_value: 0.05','','Based on P_value: 0.02','','',
            '', '', '', '', '', '', '', '', '', '',
            'CURRENT', '',
            "RMD's suggestion", '',
            'General room', '','',
            'Special room', '','',
            "RMD's suggestion", '',

        ]

        subheaders2 = [
            'No',
            'Group',
            'Sector',
            'Stock code',
            'Name',
            'Market price',
            'RP',
            '130% RP',
            'Max price',
            "RMD's suggestion",
            'Current BP',
            'BP of 130% RP',
            'BP',
            'Lowest BP',
            'BP',
            'Lowest BP',
            "RMD's suggestion",
            'Vol-listed',
            'Floating shares',
            '5% of listed-shares',
            'Market Cap (million dong)',
            'Net profit(million dong)',
            'Ranking',
            'Average Volume',
            'Average Amount 3Ms (million dong)',
            'Illiquidity',
            'Approved/liquidity (time)',
            'MR loan ratio',
            'DP loan ratio',
            'MR ratio',
            'DP ratio',
            'Approved',
            'Set up',
            'Used room',
            'Approved',
            'Set up',
            'Used room',
            'General room',
            'Special room',
            'Approved',
            'Used room',
            "RMD's suggestion",
            'Fixed MP',
            'Backlist',
            'Note 1 (MC, AV)',
            'Note 2 (CBP, Var)'
        ]
        # write
        worksheet.merge_range('A1:E2', 'Merged Cells')
        worksheet.merge_range('F1:J2', 'Merged Cells')
        worksheet.merge_range('K1:Q1', 'Merged Cells')
        worksheet.merge_range('R1:W2', 'Merged Cells')
        worksheet.merge_range('X1:AA2', 'Merged Cells')
        worksheet.merge_range('AB1:AE1', 'Merged Cells')
        worksheet.merge_range('AF1:AM1', 'Merged Cells')
        worksheet.merge_range('AN1:AP2', 'Merged Cells')
        worksheet.merge_range('M2:N2', 'Merged Cells')
        worksheet.merge_range('O2:P2', 'Merged Cells')
        worksheet.merge_range('AB2:AC2', 'Merged Cells')
        worksheet.merge_range('AD2:AE2', 'Merged Cells')
        worksheet.merge_range('AF2:AH2', 'Merged Cells')
        worksheet.merge_range('AI2:AK2', 'Merged Cells')
        worksheet.merge_range('AL2:AM2', 'Merged Cells')
        worksheet.write_row('A1', headers, headerFormat)
        worksheet.write_row('A2', subheaders1, headerFormat)
        worksheet.write_row('A3', subheaders2, headerFormat)
        worksheet.autofilter('A3:AT3')
        worksheet.freeze_panes(3, 0)
        writer.close()


if __name__ == '__main__':
    a = ExcelWriter()
    a.writeFullReport()

