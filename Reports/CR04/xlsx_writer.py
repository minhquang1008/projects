import pandas as pd
import datetime as dt
import os
from os.path import join


class ExcelWriter:

    def __init__(self):
        self.__today = dt.datetime.now()
        self.__dataSheet = None
        self.__destinationDir = fr"C:\Users\quangpham\Shared Folder\Risk Management\Review Creditline"
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
    def data(self):
        return self.__dataSheet

    @data.setter
    def data(self, df):
        self.__dataSheet = df

    @property
    def pathToAttachFile(self):
        return self.__filePath

    def writeReport(self):
        hour = self.__today.hour
        minute = self.__today.minute
        dateString = self.__today.strftime("%d.%m.%Y")
        fileName = f"Review creditline report {dateString} - {hour}h{minute}.xlsx"
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
        percentFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 10,
            'num_format': '0%',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'
        })

        headerFormatOrange = workbook.add_format({
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

        headerFormatYellow = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'yellow',
            'font_color': '#000000',
        })

        headerFormatWhite = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'white',
            'font_color': '#000000',
        })

        headerFormatDarkOrgange = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#ed7d31',
            'font_color': '#000000',
        })

        headerFormatLightOrange = workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#fff2cc',
            'font_color': '#000000',
        })

        headerFormatGreen= workbook.add_format({
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 10,
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#c6e0b4',
            'font_color': '#000000',
        })

        textFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        numberFormat = workbook.add_format({
            'font_name': 'Times New Roman',
            'font_size': 10,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)',
            'border': 1,
        })

        headers1 = ['No', 'Account', 'Sub Margin Account', 'Name', 'Broker', 'Branch']
        headers2 = ['Current limit', '', '']
        headers3 = ['Current P.Outs', '', '', 'Total Cash']
        headers4 = ['Max Outstanding (06 months)', '', '']
        headers5 = ['Average Outstanding (06 months)', '', '', 'Trading value (06 months)', '']
        headers6 = ['MR Highest outstanding/MR limit X(mr)', 'DP Highest outstanding/DP limit X(dp)']
        headers7 = ['% Reduced (MR)', '% Reduced (DP)']
        headers8 = ["RMD's review", '']
        headers9 = ["LM's opinions", '']
        headers10 = ["RMD's suggestion"]
        headers11 = ["RMC's Approval", '']
        sub_headers1 = ['MR limit', 'DP limit', 'Total limit']
        sub_headers2 = ['MR Outstanding', 'DP Outstanding', 'Total Outstanding']
        sub_headers3 = ['Max MR Outs', 'Max DP Outs', 'Max Total Outs', 'Av MR Outs', 'Av DP Outs', 'Av Total Outs',
            'Total trading value', 'Max trading value']
        sub_headers4 = ['MR limit', 'DP limit']
        sub_headers5 = ['MR limit', 'DP limit']
        sub_headers6 = ['MR', 'DP']
        # write
        worksheet.merge_range(f'G1:I1', 'Merged cells')
        worksheet.merge_range(f'J1:L1', 'Merged cells')
        worksheet.merge_range(f'N1:P1', 'Merged cells')
        worksheet.merge_range(f'Q1:S1', 'Merged cells')
        worksheet.merge_range(f'T1:U1', 'Merged cells')
        worksheet.merge_range(f'Z1:AA1', 'Merged cells')
        worksheet.merge_range(f'AB1:AC1', 'Merged cells')
        worksheet.merge_range(f'AE1:AF1', 'Merged cells')
        worksheet.write_row('G2', sub_headers1, headerFormatYellow)
        worksheet.write_row('J2', sub_headers2, headerFormatDarkOrgange)
        worksheet.write_row('N2', sub_headers3, headerFormatWhite)
        worksheet.write_row('Z2', sub_headers4, headerFormatLightOrange)
        worksheet.write_row('AB2', sub_headers5, headerFormatGreen)
        worksheet.write_row('AE2', sub_headers6, headerFormatWhite)
        for i in ['A', 'B', 'C', 'D', 'E', 'F', 'M', 'V', 'W', 'X', 'Y', 'AD']:
            worksheet.merge_range(f'{i}1:{i}2', 'Merged cells', headerFormatOrange)
        worksheet.write_row('A1', headers1, headerFormatOrange)
        worksheet.write_row('G1', headers2, headerFormatYellow)
        worksheet.write_row('J1', headers3, headerFormatDarkOrgange)
        worksheet.write_row('N1', headers4, headerFormatWhite)
        worksheet.write_row('Q1', headers5, headerFormatWhite)
        worksheet.write_row('V1', headers6, headerFormatLightOrange)
        worksheet.write_row('X1', headers7, headerFormatWhite)
        worksheet.write_row('Z1', headers8, headerFormatLightOrange)
        worksheet.write_row('AB1', headers9, headerFormatGreen)
        worksheet.write_row('AD1', headers10, headerFormatOrange)
        worksheet.write_row('AE1', headers11, headerFormatWhite)
        worksheet.set_column('A:A', 4)
        worksheet.set_column('B:B', 12)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:F', 18)
        worksheet.set_column('G:M', 15)
        worksheet.set_column('M:AC', 18)
        worksheet.set_column('AD:AD', 25)
        worksheet.set_column('AE:AF', 18)
        worksheet.set_row(0, 25)
        worksheet.freeze_panes(0, 9)
        worksheet.write_column('A3', self.data['No'], textFormat)
        worksheet.write_column('B3', self.data['account_code'], textFormat)
        worksheet.write_column('C3', self.data['sub_account'], textFormat)
        worksheet.write_column('D3', self.data['customer_name'], textFormat)
        worksheet.write_column('E3', self.data['broker_name'], textFormat)
        worksheet.write_column('F3', self.data['branch_name'], textFormat)
        worksheet.write_column('G3', self.data['mr_limit'], numberFormat)
        worksheet.write_column('H3', self.data['dp_limit'], numberFormat)
        worksheet.write_column('I3', self.data['total_limit'], numberFormat)
        worksheet.write_column('J3', self.data['mr_outstanding'], numberFormat)
        worksheet.write_column('K3', self.data['dp_outstanding'], numberFormat)
        worksheet.write_column('L3', self.data['total_outstanding'], numberFormat)
        worksheet.write_column('M3', self.data['cash'], numberFormat)
        worksheet.write_column('N3', self.data['max_mr_outstanding'], numberFormat)
        worksheet.write_column('O3', self.data['max_dp_outstanding'], numberFormat)
        worksheet.write_column('P3', self.data['max_total_outstanding'], numberFormat)
        worksheet.write_column('Q3', self.data['avg_mr_outstanding'], numberFormat)
        worksheet.write_column('R3', self.data['avg_dp_outstanding'], numberFormat)
        worksheet.write_column('S3', self.data['avg_total_outstanding'], numberFormat)
        worksheet.write_column('T3', self.data['total_value_6m'], numberFormat)
        worksheet.write_column('U3', self.data['max_value_6m'], numberFormat)
        worksheet.write_column('V3', self.data['mr_outstanding_over_limit'], percentFormat)
        worksheet.write_column('W3', self.data['dp_outstanding_over_limit'], percentFormat)
        worksheet.write_column('X3', self.data['mr_reduced'], percentFormat)
        worksheet.write_column('Y3', self.data['dp_reduced'], percentFormat)
        worksheet.write_column('Z3', self.data['mr_suggest'], numberFormat)
        worksheet.write_column('AA3', self.data['dp_suggest'], numberFormat)
        worksheet.write_column('AB3', ['']*self.data.shape[0], textFormat)
        worksheet.write_column('AC3', ['']*self.data.shape[0], textFormat)
        worksheet.write_column('AD3', self.data['rmd_suggestion'], textFormat)
        worksheet.write_column('AE3', ['']*self.data.shape[0], textFormat)
        worksheet.write_column('AF3', ['']*self.data.shape[0], textFormat)
        writer.close()
