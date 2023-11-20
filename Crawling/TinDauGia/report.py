import datetime as dt
import pandas as pd
import os

from info import CompanyName, CompanyAddress, CompanyPhoneNumber
from request import connect_DWH_ThiTruong
import crawler

class Report:

    def __init__(
        self,
        fromTime: dt.datetime,
        toTime: dt.datetime,
    ) -> None:
        
        self.__fromTime = fromTime
        self.__toTime = toTime
        self.__data = None
        self.HOSECrawler = crawler.HOSE()
        self.HNXCrawler = crawler.HNX()

    @property
    def fromTime(self) -> dt.datetime:
        return self.__fromTime
    
    @fromTime.setter
    def fromTime(self, value: dt.datetime) -> None:
        self.__data = None
        self.__fromTime = value

    @property
    def toTime(self) -> dt.datetime:
        return self.__toTime
    
    @toTime.setter
    def toTime(self, value: dt.datetime) -> None:
        self.__data = None
        self.__toTime = value

    @property
    def data(self):
        if self.__data is not None:  # cache
            return self.__data
        # Crawl HNX
        self.HNXCrawler.fromTime = self.fromTime
        self.HNXCrawler.toTime = self.toTime
        self.HNXCrawler.crawl()
        # Crawl HOSE
        self.HOSECrawler.fromTime = self.fromTime
        self.HOSECrawler.toTime = self.toTime
        self.HOSECrawler.crawl()
        # Crawl xong -> query từ database lên
        self.__data = pd.read_sql(
            sql = f"""
                SELECT
                    RANK() OVER (ORDER BY [ThoiGian], [TieuDe]) [Rank]
                    , DENSE_RANK() OVER (ORDER BY [ThoiGian], [TieuDe]) [STT]
                    , [TinDauGia].[ThoiGian]
                    , [TinDauGia].[SanGiaoDich]
                    , [TinDauGia].[TieuDe]
                	, JSON_VALUE([TinDauGia].[NoiDung],'$.noidung') [NoiDung]
                    , [JsonTable].[FileDinhKem]
                FROM [TinDauGia]
                CROSS APPLY dbo.JSON2EXCELFORMULA_TinDauGia([TinDauGia].[NoiDung]) [JsonTable]
                WHERE [ThoiGian] BETWEEN '{self.fromTime}' AND '{self.toTime}'
                ORDER BY [ThoiGian], [SanGiaoDich]
                """,
            con = connect_DWH_ThiTruong,
            parse_dates = ['ThoiGian']
        )
        return self.__data

    def show(self) -> None:
        # tạo folder temp nếu chưa có
        if not os.path.isdir('./temp'):
            os.mkdir('./temp')
        # xóa toàn bộ file excel có trong temp
        for excelFile in os.listdir('./temp'):
            try:
                os.remove(f'./temp/{excelFile}')
            except (PermissionError,):  # file đang được mở
                continue
        # ghi file excel 
        filePath = f'./temp/TinDauGia_{dt.datetime.now().strftime("%d.%m.%Y %H.%M.%S")}.xlsx'
        
        with pd.ExcelWriter(
            path = filePath, 
            engine = 'xlsxwriter',
            engine_kwargs = {'options': {'nan_inf_to_errors': True}}
        ) as excelWriter:
            self.__writeExcel(excelWriter)
        # mở file excel
        os.startfile(os.path.abspath(filePath))

    def __writeExcel(self, excelWriter: pd.ExcelWriter) -> None:

        workbook = excelWriter.book
        companyNameFormat = workbook.add_format({
            'bold':True,
            'align':'left',
            'valign':'vcenter',
            'font_size':12,
            'font_name':'Times New Roman',
            'text_wrap':True
        })
        companyInfoFormat = workbook.add_format({
            'align':'left',
            'valign':'vcenter',
            'font_size':12,
            'font_name':'Times New Roman',
            'text_wrap':True
        })
        emptyRowFormat = workbook.add_format({
            'bottom':1,
            'valign':'vcenter',
            'font_size':12,
            'font_name':'Times New Roman',
        })
        sheetTitleFormat = workbook.add_format({
            'bold':True,
            'align':'center',
            'valign':'vcenter',
            'font_size':14,
            'font_name':'Times New Roman',
            'text_wrap':True
        })
        subTitleTimeFormat = workbook.add_format({
            'italic':True,
            'align':'center',
            'valign':'vcenter',
            'font_size':12,
            'font_name':'Times New Roman',
            'text_wrap':True
        })
        headersFormat = workbook.add_format({
            'border':1,
            'bold':True,
            'align':'center',
            'valign':'vcenter',
            'font_size':12,
            'font_name':'Times New Roman',
            'text_wrap':True
        })    
        textCenterFormat = workbook.add_format({
            'border':1,
            'align':'center',
            'valign':'vcenter',
            'font_size':12,
            'font_name':'Times New Roman'
        })
        textLeftFormat = workbook.add_format({
            'border':1,
            'align':'left',
            'valign':'top',
            'font_size':12,
            'font_name':'Times New Roman',
            'text_wrap': True
        })
        timeFormat = workbook.add_format({
            'border':1,
            'align':'center',
            'valign':'vcenter',
            'font_name':'Times New Roman',
            'font_size':12,
            'num_format':'dd/mm/yyyy hh:mm:ss'
        })
        headers = [
            'STT', # A
            'Thời Gian', # B
            'Sàn', # C
            'Tiêu Đề', # D
            'Nội Dung', # E
            'File Đính Kèm', # F
        ]
        titleName = 'TIN ĐẤU GIÁ'
        fromTimeString = self.fromTime.strftime("%d/%m/%Y %H:%M:%S")
        toTimeString = self.toTime.strftime("%d/%m/%Y %H:%M:%S")
        subTitleName = f'Giai đoạn: {fromTimeString} - {toTimeString}'
        worksheet = workbook.add_worksheet(f'TinDauGia')
        worksheet.hide_gridlines(option=2)
        worksheet.insert_image('A1','phs_logo.png',{'x_scale':0.66,'y_scale':0.71})
        
        worksheet.set_column('A:A', 6)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 70)
        worksheet.set_column('F:F', 40)
        worksheet.merge_range('C1:F1', CompanyName, companyNameFormat)
        worksheet.merge_range('C2:F2', CompanyAddress, companyInfoFormat)
        worksheet.merge_range('C3:F3', CompanyPhoneNumber, companyInfoFormat)
        worksheet.merge_range('A7:F7', titleName, sheetTitleFormat)
        worksheet.merge_range('A8:F8', subTitleName, subTitleTimeFormat)
        worksheet.write_row('A4', ['']*len(headers), emptyRowFormat)

        worksheet.write_row('A10', headers, headersFormat)
        for rank in self.data['Rank'].unique():
            # mỗi subTable là một article
            subTable = self.data.loc[self.data['Rank']==rank]
            # article-wise values
            stt = subTable.loc[subTable.index[0],'STT']
            thoiGian = subTable.loc[subTable.index[0],'ThoiGian']
            sanGiaoDich = subTable.loc[subTable.index[0],'SanGiaoDich']
            tieuDe = subTable.loc[subTable.index[0],'TieuDe']
            noiDung = subTable.loc[subTable.index[0],'NoiDung']
            if subTable.shape[0] == 1:
                worksheet.write(f'A{10+rank}',stt,textCenterFormat)
                worksheet.write(f'B{10+rank}',thoiGian,timeFormat)
                worksheet.write(f'C{10+rank}',sanGiaoDich,textCenterFormat)
                worksheet.write(f'D{10+rank}',tieuDe,textLeftFormat)
                worksheet.write(f'E{10+rank}',noiDung,textLeftFormat)
                # có duy nhất 1 file đính kèm
                fileDinhKem = subTable.loc[subTable.index[0],'FileDinhKem']
                worksheet.write(f'F{10+rank}',fileDinhKem,textLeftFormat)
            else:
                startMergeRow = 10 + rank
                endMergeRow = 10 + rank + subTable.shape[0] - 1
                worksheet.merge_range(f'A{startMergeRow}:A{endMergeRow}',stt,textCenterFormat)
                worksheet.merge_range(f'B{startMergeRow}:B{endMergeRow}',thoiGian,timeFormat)
                worksheet.merge_range(f'C{startMergeRow}:C{endMergeRow}',sanGiaoDich,textCenterFormat)
                worksheet.merge_range(f'D{startMergeRow}:D{endMergeRow}',tieuDe,textLeftFormat)
                worksheet.merge_range(f'E{startMergeRow}:E{endMergeRow}',noiDung,textLeftFormat)
                # mỗi file đính kèm là 1 dòng
                worksheet.write_column(f'F{startMergeRow}',subTable['FileDinhKem'],textLeftFormat)

