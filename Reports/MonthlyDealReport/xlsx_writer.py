import pandas as pd
import datetime as dt
import os

from os.path import join


class ExcelWriter:

    def __init__(self):
        self.__today = dt.datetime.now()
        self.__dataSheet1 = None
        self.__dataSheet2 = None
        self.__roomCode = None
        self.__destinationDir = fr"C:\Users\quangpham\Shared Folder\Risk Management\High Risk Stock"
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

    @property
    def room_code(self):
        return self.__roomCode

    @room_code.setter
    def room_code(self, code):
        self.__roomCode = code

    @property
    def data1(self):
        return self.__dataSheet1

    @data1.setter
    def data1(self, df):
        self.__dataSheet1 = df

    @property
    def data2(self):
        return self.__dataSheet2

    @data2.setter
    def data2(self, df):
        self.__dataSheet2 = df

    @property
    def pathToAttachFile(self):
        return self.__filePath

    def writeFullReport(self):
        hour = self.__today.hour
        minute = self.__today.minute
        dateString = self.__today.strftime("%d.%m.%Y")
        fileName = f"Monthly deal report {dateString} - {hour}h{minute}.xlsx"
        self.__filePath = join(self.__destinationDir, self.__yearString, self.__monthString, self.__dateString,
                               fileName)

        writer = pd.ExcelWriter(
            self.__filePath,
            engine='xlsxwriter',
            engine_kwargs={'options': {'nan_inf_to_errors': True}}
        )

        workbook = writer.book
        worksheet = workbook.add_worksheet('Summary Information')
        worksheet.hide_gridlines(option=2)

        # format
        headerFormat = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#ffc000',
            'font_color': '#000000',
        })

        headerFormat2 = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#fde9d9',
            'font_color': '#000000',
        })

        headerFormat3 = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#92d050',
            'font_color': '#000000',
        })

        textFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        mergeFormat = workbook.add_format(
            {
                'font_name': 'Times New Roman',
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'text_wrap': True
            }
        )

        numberFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 10,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
        })

        headers = [
            'Room code', 'Account', 'Stock', 'Sub Account', 'Location', 'Quantity', 'Closed price', 'Total Cash',
        ]
        headers2 = [
            'Market value of this stock', 'Total market value of all stocks', 'Principal Outstanding',
            'Interest Outstanding', 'Total Outstanding',
        ]
        headers3 = [
            'Trading value of account', 'Trading value of stock', 'Trading fee of account'
        ]

        # write
        if len(self.room_code) != 0:
            self.data1 = self.data1[self.data1['MãRoom'] == int(self.room_code)]
        worksheet.write_row('A1', headers, headerFormat)
        worksheet.write_row('I1', headers2, headerFormat2)
        worksheet.write_row('N1', headers3, headerFormat3)
        worksheet.set_column('A:A', 7)
        worksheet.set_column('B:B', 12)
        worksheet.set_column('C:C', 7)
        worksheet.set_column('D:G', 12)
        worksheet.set_column('H:M', 14)
        worksheet.set_column('M:P', 18)
        worksheet.set_row(0, 30)
        worksheet.freeze_panes(1, 0)
        worksheet.write_column('A2', self.data1['MãRoom'], textFormat)
        worksheet.write_column('B2', self.data1['Account'], textFormat)
        worksheet.write_column('C2', self.data1['MãCK'], textFormat)
        worksheet.write_column('D2', self.data1['sub_account'], textFormat)
        worksheet.write_column('E2', self.data1['location'], textFormat)
        worksheet.write_column('F2', self.data1['quantity'], numberFormat)
        worksheet.write_column('G2', self.data1['Close'], numberFormat)
        worksheet.write_column('H2', self.data1['total_cash'], numberFormat)
        worksheet.write_column('I2', self.data1['market_value_of_this_stock'], numberFormat)
        worksheet.write_column('J2', self.data1['market_value_for_all_stocks'], numberFormat)
        worksheet.write_column('K2', self.data1['principal_outstanding'], numberFormat)
        worksheet.write_column('L2', self.data1['interest_outstanding'], numberFormat)
        worksheet.write_column('M2', self.data1['total_outstanding'], numberFormat)
        worksheet.write_column('N2', self.data1['trading_value_of_account'], numberFormat)
        worksheet.write_column('O2', self.data1['trading_value_of_stock'], numberFormat)
        worksheet.write_column('P2', self.data1['trading_fee_of_account'], numberFormat)
        worksheet.autofilter('A1:P1')

        worksheet = workbook.add_worksheet('Monthly deal report')
        worksheet.hide_gridlines(option=2)
        headers = [
            'No', 'Room Code', 'Setup date', 'Approved Date (MM)', 'Stock', 'Sector', 'Location', 'Account',
            'Approved Quantity', 'Set up', 'MR  Ratio (%)', 'DP  Ratio (%)', 'Max Price', 'Approved P.Outs',
            'Average Volume 03 months', 'Closed price', 'Breakeven Price Min', 'Breakeven Price Max',
            'Used quantity (Shares)', 'P.Outs net Cash (Unit: Mil VND)', 'Trading Value of Account (Unit: Mil VND)',
            'Trading Value of Stock (Unit: Mil VND)', 'Quantity (shares)',
            'MAVT (Monthly average trading value at least)', 'Commitment Fix Type Others special',
            "RMD's Suggestion", "DGD's opinions"
        ]
        if len(self.room_code) != 0:
            self.data2 = self.data2[self.data2['room_code'] == int(self.room_code)]
        for i in range(-1, -len(self.data2)-1, -1):
            if i != -1 and self.data2['room_code'].iloc[i] == self.data2['room_code'].iloc[i+1]:
                self.data2['Account'].iloc[i] = self.data2['Account'].iloc[i] + ', ' + self.data2['Account'].iloc[i+1]
        worksheet.write_row('A1', headers, headerFormat)
        worksheet.set_column('A:A', 7)
        worksheet.set_column('B:C', 12)
        worksheet.set_column('D:G', 14)
        worksheet.set_column('H:M', 14)
        worksheet.set_column('M:AA', 18)
        worksheet.set_row(0, 30)
        worksheet.freeze_panes(0, 2)
        worksheet.write_column('A2', self.data2['No'], textFormat)
        worksheet.write_column('B2', self.data2['room_code'], textFormat)
        worksheet.write_column('C2', ['' for i in range(0, len(self.data2))], textFormat)
        worksheet.write_column('D2', ['' for i in range(0, len(self.data2))], textFormat)
        worksheet.write_column('E2', self.data2['ticker'], textFormat)
        worksheet.write_column('F2', self.data2['sector'], textFormat)
        worksheet.write_column('G2', self.data2['location'], textFormat)
        worksheet.write_column('H2', self.data2['Account'], textFormat)
        worksheet.write_column('T2', self.data2['p.outs_net_cash'], numberFormat)
        worksheet.write_column('U2', self.data2['trading_value_of_account'], numberFormat)
        worksheet.write_column('X2', self.data2['MATV'], numberFormat)
        empty_list = []
        for i in range(0, len(self.data2)):
            if i != 0 and self.data2['room_code'].iloc[i] == self.data2['room_code'].iloc[i-1]:
                empty_list.append(int(i))
            elif i == 0:
                empty_list.append(int(i))
            else:
                worksheet.merge_range(f'H{min(empty_list)+2}:H{max(empty_list)+2}', self.data2['Account'].iloc[min(empty_list)], mergeFormat)
                worksheet.merge_range(f'T{min(empty_list) + 2}:T{max(empty_list) + 2}', self.data2['p.outs_net_cash'].iloc[min(empty_list)], numberFormat)
                worksheet.merge_range(f'U{min(empty_list) + 2}:U{max(empty_list) + 2}', self.data2['trading_value_of_account'].iloc[min(empty_list)], numberFormat)
                worksheet.merge_range(f'X{min(empty_list) + 2}:X{max(empty_list) + 2}', self.data2['MATV'].iloc[min(empty_list)], numberFormat)
                worksheet.merge_range(f'F{min(empty_list) + 2}:F{max(empty_list) + 2}',self.data2['sector'].iloc[min(empty_list)], mergeFormat)
                empty_list = [i]
        worksheet.merge_range(f'H{min(empty_list) + 2}:H{max(empty_list) + 2}',
                              self.data2['Account'].iloc[min(empty_list)], mergeFormat)
        worksheet.merge_range(f'T{min(empty_list) + 2}:T{max(empty_list) + 2}',
                              self.data2['p.outs_net_cash'].iloc[min(empty_list)], numberFormat)
        worksheet.merge_range(f'U{min(empty_list) + 2}:U{max(empty_list) + 2}',
                              self.data2['trading_value_of_account'].iloc[min(empty_list)], numberFormat)
        worksheet.merge_range(f'X{min(empty_list) + 2}:X{max(empty_list) + 2}',
                              self.data2['MATV'].iloc[min(empty_list)], numberFormat)
        worksheet.merge_range(f'F{min(empty_list) + 2}:F{max(empty_list) + 2}',
                              self.data2['sector'].iloc[min(empty_list)], mergeFormat)
        worksheet.write_column('I2', ['' for i in range(0, len(self.data2))], textFormat)
        worksheet.write_column('J2', self.data2['total_volume'], numberFormat)
        worksheet.write_column('K2', self.data2['mr_ratio'], numberFormat)
        worksheet.write_column('L2', self.data2['dp_ratio'], numberFormat)
        worksheet.write_column('M2', self.data2['margin_max_price'], numberFormat)
        worksheet.write_column('N2', ['' for i in range(0, len(self.data2))], numberFormat)
        worksheet.write_column('O2', self.data2['3M Avg. Volume'], numberFormat)
        worksheet.write_column('P2', self.data2['Close'], numberFormat)
        worksheet.write_column('Q2', self.data2['break_even_price_min'], numberFormat)
        worksheet.write_column('R2', self.data2['break_even_price_max'], numberFormat)
        worksheet.write_column('S2', self.data2['used_volume'], numberFormat)
        worksheet.write_column('V2', self.data2['trading_value_of_stock'], numberFormat)
        worksheet.write_column('W2', self.data2['quantity'], numberFormat)
        worksheet.write_column('Y2', ['' for i in range(0, len(self.data2))], textFormat)
        worksheet.write_column('Z2', ['' for i in range(0, len(self.data2))], textFormat)
        worksheet.write_column('AA2', ['' for i in range(0, len(self.data2))], textFormat)
        worksheet.autofilter('A1:AA1')
        writer.close()
        return self.__filePath




