import datetime as dt
import pandas as pd
import os

from info import CompanyName, CompanyAddress, CompanyPhoneNumber
from request import connect_DWH_ThiTruong
# from automation.trading_service.giaodichluuky.ThanhVienGiaoDich import crawler

class Report:

    def __init__(self) -> None:
        
        self.atTime = dt.datetime.now()  # chỉ ghi nhận gần đúng
        self.__data = None
        # self.HOSECrawler = crawler.HOSECrawler()
        # self.HNXCrawler = crawler.HNXCrawler()

    @property
    def data(self):
        if self.__data is not None:  # cache
            return self.__data
        # Crawl HNX
        # self.HNXCrawler.crawl()
        # Crawl HOSE
        # self.HOSECrawler.crawl()
        # Crawl xong -> query từ database lên
        self.__data = pd.read_sql(
            sql=f"""
            WITH [HNX] AS (
                SELECT             
                    [MaThanhVien] [MaThanhVienHNX],
                    [TenDayDu] [TenThanhVienHNX],
                    [TenVietTat] [TenVietTatHNX],
                    CONCAT('=HYPERLINK("', [URL], '","Link")') [LinkHNX]
                FROM [DanhSachThanhVienSGD]
                -- WHERE [Ngay] = '{dt.date.today().strftime('%Y-%m-%d')}'
                WHERE [Ngay] = '2023-01-31' AND [SanGiaoDich] LIKE 'HNX'
            ),
            [HOSE] AS (
                SELECT                 
                    [MaThanhVien] [MaThanhVienHOSE],
                    [TenDayDu] [TenThanhVienHOSE],
                    [TenVietTat] [TenVietTatHOSE],
                    CONCAT('=HYPERLINK("', [URL], '","Link")') [LinkHOSE]
                FROM [DanhSachThanhVienSGD]
                -- WHERE [Ngay] = '{dt.date.today().strftime('%Y-%m-%d')}'
                WHERE [Ngay] = '2023-01-31' AND [SanGiaoDich] LIKE 'HOSE'
            )
                        
            SELECT 
                ROW_NUMBER() OVER(ORDER BY [MaThanhVienHNX]) AS [STT],
                CASE
                    WHEN [MaThanhVienHNX] IS NULL
                        THEN ISNULL([MaThanhVienHNX], [MaThanhVienHOSE])
                    WHEN [MaThanhVienHOSE] IS NULL
                        THEN ISNULL([MaThanhVienHOSE], [MaThanhVienHNX])
                    ELSE [MaThanhVienHNX]
                END [MaThanhVien],
                [TenThanhVienHNX],
                [TenVietTatHNX],
                [LinkHNX],
                [TenThanhVienHOSE],
                [TenVietTatHOSE],
                [LinkHOSE]
            
            FROM [HNX] 
            FULL OUTER JOIN [HOSE] 
                ON [HNX].[MaThanhVienHNX] = [HOSE].[MaThanhVienHOSE]
            ORDER BY 1
            """,
            con=connect_DWH_ThiTruong,
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
        filePath = f'./temp/DanhSachThanhVienGiaoDich_{self.atTime.strftime("%d.%m.%Y %H.%M.%S")}.xlsx'

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
            'bold':True, 'align':'left', 'valign':'vcenter', 'font_size':12,
            'font_name':'Times New Roman', 'text_wrap':True
        })
        companyInfoFormat = workbook.add_format({
            'align':'left', 'valign':'vcenter', 'font_size':12,
            'font_name':'Times New Roman', 'text_wrap':True
        })
        emptyRowFormat = workbook.add_format({
            'bottom':1, 'valign':'vcenter', 'font_size':12,
            'font_name':'Times New Roman',
        })
        sheetTitleFormat = workbook.add_format({
            'bold':True, 'align':'center', 'valign':'vcenter', 'font_size':14, 
            'font_name':'Times New Roman', 'text_wrap':True
        })
        subTitleTimeFormat = workbook.add_format({
            'italic':True, 'align':'center', 'valign':'vcenter', 'font_size':12,
            'font_name':'Times New Roman', 'text_wrap':True
        })
        headersFormat = workbook.add_format({
            'border':1, 'bold':True, 'align':'center', 'valign':'vcenter',
            'font_size':12, 'font_name':'Times New Roman', 'text_wrap':True
        })    
        textCenterFormat = workbook.add_format({
            'border':1, 'align':'center', 'valign':'vcenter', 'font_size':12,
            'font_name':'Times New Roman'
        })
        textLeftFormat = workbook.add_format({
            'border':1, 'align':'left', 'valign':'top', 'font_size':12,
            'font_name':'Times New Roman',
        })
        headers = [
            'STT', # A
            'Mã thành viên', # B
            'Tên thành viên HNX', # C
            'Tên viết tắt HNX', # D
            'Link thành viên HNX', # E
            'Tên thành viên HOSE',  # F
            'Tên viết tắt HOSE',  # G
            'Link thành viên HOSE',  # H
        ]
        titleName = 'DANH SÁCH THÀNH VIÊN GIAO DỊCH'
        subTitleName = f'Cập nhật lúc: {self.atTime.strftime("%d.%m.%Y %H:%M:%S")}'
        worksheet = workbook.add_worksheet(f'DanhSachThanhVienGiaoDich')
        worksheet.hide_gridlines(option=2)
        worksheet.insert_image('A1','phs_logo.png',{'x_scale':0.66,'y_scale':0.71})
        worksheet.set_column('A:A', 6)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 50)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 50)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 15)
        worksheet.merge_range('C1:F1', CompanyName, companyNameFormat)
        worksheet.merge_range('C2:F2', CompanyAddress, companyInfoFormat)
        worksheet.merge_range('C3:F3', CompanyPhoneNumber, companyInfoFormat)
        worksheet.merge_range('A7:F7', titleName, sheetTitleFormat)
        worksheet.merge_range('A8:F8', subTitleName, subTitleTimeFormat)
        worksheet.write_row('A4', ['']*len(headers), emptyRowFormat)
        worksheet.write_row('A10', headers, headersFormat)
        worksheet.write_column('A11',self.data['STT'],textLeftFormat)
        worksheet.write_column('B11',self.data['MaThanhVien'],textCenterFormat)
        worksheet.write_column('C11',self.data['TenThanhVienHNX'],textLeftFormat)
        worksheet.write_column('D11',self.data['TenVietTatHNX'],textCenterFormat)
        worksheet.write_column('E11',self.data['LinkHNX'],textCenterFormat)
        worksheet.write_column('F11',self.data['TenThanhVienHOSE'],textLeftFormat)
        worksheet.write_column('G11',self.data['TenVietTatHOSE'],textCenterFormat)
        worksheet.write_column('H11',self.data['LinkHOSE'],textCenterFormat)


if __name__ == '__main__':
    # os.chdir(r'C:\Users\hiepdang\PycharmProjects\DataAnalytics\automation\trading_service\giaodichluuky\ThanhVienGiaoDich')
    report = Report()
    report.show()