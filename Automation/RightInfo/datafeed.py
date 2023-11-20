# import os
# os.chdir(fr"{os.environ['PYTHONPATH']}\automation\flex_gui\RightInfo")


import datetime as dt
import pandas as pd
from automation.flex_gui.RightInfo import query, factory



class DataFeed:

    def __init__(
        self,
        queryFromVSD: query.DanhSachQuyenVSD,
        queryFromF220001: query.F220001,
        queryFromRSE0008: query.ChungKhoanRSE0008,
        queryFromLog: query.LogTable,
    ) -> None:

        self._atDate = queryFromVSD.atDate
        self._classifiableVSDTable, self._unclassifiableVSDTable = type(self).__transformVSDTable(queryFromVSD.result) # static data
        self._full220001Table = queryFromF220001.result  # static data
        self._fullRSE0008Table = queryFromRSE0008.result  # static data
        self._queryFromLog = queryFromLog  # dynamic data

        self.__jointClassifiableTable = None
        self.__jointDueTodayTable = None

        self.__tableForJob1 = None
        self.__tableForJob2 = None
        self.__tableForJob3 = None
        self.__tableForJob4 = None
        self.__tableForJob5 = None
        self.__tableForJob6 = None
        self.__tableForJob7 = None
        self.__tableForJob8 = None

    @property
    def tableForJob1(self):

        """
        Danh sách các quyền có trên VSD nhưng Flex 220001 chưa có (chỉ lấy cổ phiếu)
        ==> Dùng để gửi mail
        """

        # lấy mask các dòng
        rowMask1 = self._jointClassifiableTable['InVSD']
        rowMask2 = self._jointClassifiableTable['VSD.MaChungKhoan'].str.len() == 3 
        rowMask3 = ~ self._jointClassifiableTable['In220001']
        rowMask = rowMask1 & rowMask2 & rowMask3

        # chọn cột
        selectedColumns = [
            'VSD.ThoiGian',
            'VSD.NgayDangKyCuoiCung',
            'VSD.MaChungKhoan',
            'VSD.TieuDe',
            'VSD.LoaiQuyen',
            'VSD.URL',
        ]
        table = self._jointClassifiableTable.loc[rowMask,selectedColumns]
        self.__tableForJob1 = table.reset_index(drop=True)
        
        return self.__tableForJob1


    @property
    def tableForJob2(self):

        """
        Danh sách các quyền có trên Flex 220001 nhưng VSD chưa có (lấy toàn bộ)
        ==> Dùng để gửi mail
        """

        # lấy mask các dòng
        rowMask1 = self._jointClassifiableTable['In220001']
        rowMask2 = ~ self._jointClassifiableTable['InVSD'] 
        rowMask = rowMask1 & rowMask2

        # chọn cột
        selectedColumns = [
            'F220001.NgayDangKyCuoiCung',
            'F220001.MaChungKhoan',
            'F220001.LoaiQuyen',
            'F220001.MaThucHienQuyen',
        ]
        table = self._jointClassifiableTable.loc[rowMask, selectedColumns]
        self.__tableForJob2 = table.reset_index(drop=True)
        
        return self.__tableForJob2


    @property
    def tableForJob3(self):

        """
        Danh sách các quyền trên Flex 220001 đang bị trùng thông tin
        ==> Dùng để gửi mail
        """

        columnList1 = ['F220001.NgayDangKyCuoiCung','F220001.LoaiQuyen','F220001.MaChungKhoan']
        columnList2 = columnList1 + ['F220001.TyLeChiaCoTucBangTien']

        rowMask1 = self._full220001Table[columnList1].duplicated(keep=False)
        rowMask2 = self._full220001Table[columnList2].duplicated(keep=False)
        # trùng 4 thông tin thì không cần đánh dấu trùng 3 thông tin nữa
        rowMask1 = rowMask1 & ~rowMask2
        rowMask = rowMask1 | rowMask2

        table = self._full220001Table.loc[rowMask]
        table['F220001.Trung3ThongTin'] = rowMask1.map(lambda mask: 'x' if mask else '')
        table['F220001.Trung4ThongTin'] = rowMask2.map(lambda mask: 'x' if mask else '')
        
        self.__tableForJob3 = table.reset_index(drop=True)
        return self.__tableForJob3


    @property
    def tableForJob4(self):

        """
        Danh sách các quyền có trên Flex 220001 và VSD
        ==> Dùng để thao tác sửa trên 220001
        """

        # lấy mask các dòng
        rowMask1 = self._jointClassifiableTable['InVSD'] 
        rowMask2 = self._jointClassifiableTable['In220001']
        rowMask3 = self._jointClassifiableTable['VSD.ThoiGian'].dt.date == self._atDate.date()
        rowMask = rowMask1 & rowMask2 & rowMask3

        table = self._jointClassifiableTable.loc[rowMask]
        table = table.drop(['InVSD','In220001'], axis=1)

        self.__tableForJob4 = table.reset_index(drop=True)
        
        return self.__tableForJob4


    @property
    def tableForJob5(self):

        """
        Danh sách các quyền có trên VSD, đã đến ngày đăng ký cuối cùng 
        nhưng Flex 220001 vẫn chưa có (chỉ lấy các mã trong có trong RSE0008)
        ==> Dùng để thao tác tạo mới trên 220001
        """

        # lấy mask các dòng
        rowMask1 = self._jointDueTodayTable['InVSD']
        rowMask2 = ~ self._jointDueTodayTable['In220001']
        rowMask = rowMask1 & rowMask2

        selectedColumns = list(filter(lambda x: x.startswith('VSD.'), self._jointDueTodayTable.columns))
        table = self._jointDueTodayTable.loc[rowMask,selectedColumns]
        
        self.__tableForJob5 = table.reset_index(drop=True)
        return self.__tableForJob5


    @property
    def tableForJob6(self):

        """
        Danh sách các quyền cần phải sửa hoặc thêm mới
        ==> Dùng để gửi mail log cuối ngày
        """

        selectedColumnsOnVSD = [
            'VSD.RightObject',
            'VSD.ThoiGian',
            'VSD.MaChungKhoan',
            'VSD.TieuDe',
            'VSD.NgayDangKyCuoiCung',
            'VSD.URL',
        ]
        selectedColumnOnF220001 = ['F220001.MaThucHienQuyen']
        # tạo bảng chứa các quyền có thao tác sửa
        editedTable = self.tableForJob4[selectedColumnsOnVSD + selectedColumnOnF220001]
        editedTable['Action'] = 'Sửa'
        # tạo bảng chứa các quyền có thao tác tạo mới
        createdTable = self.tableForJob5[selectedColumnsOnVSD]
        createdTable['F220001.MaThucHienQuyen'] = ''  # tạo mới tức là không có record trên Flex
        createdTable['Action'] = 'Tạo'
        # tạo bảng tổng hợp các quyền cần thao tác
        actionTable = pd.concat([createdTable,editedTable], axis=0)
        # bỏ các quyền TraLoiTucBangChungQuyen có SoTienChiTra (tức là GiaThanhToan < GiaThucHien)
        predicate = lambda x: not (x == 'TraLoiTucBangChungQuyen' and x.soTienChiTra < 0)
        actionTable = actionTable.loc[actionTable['VSD.RightObject'].map(predicate)]
        # bỏ cột RightObject
        actionTable = actionTable.drop(['VSD.RightObject'], axis=1)

        table = pd.merge(
            left = actionTable,
            right = self._queryFromLog.result, # để lấy lại data mới
            how = 'left',
            left_on = ['VSD.URL'],
            right_on = ['Log.URL']
        )
        # vì bất kỳ lý do nào đó mà log không ghi nhận đủ
        # (ví dụ ChuyenDoiCoPhieuThanhCoPhieu có GiaThanhToan < GiaThucHien)
        # -> tức là chưa thao tác vào Flex -> báo ERROR
        table['Log.Status'] = table['Log.Status'].fillna('ERROR')
        table['Log.Message'] = table['Log.Message'].fillna('Chưa nhập Flex')
        
        self.__tableForJob6 = table.drop('Log.URL', axis=1)
        return self.__tableForJob6


    @property
    def tableForJob7(self):

        """
        Danh sách các quyền hệ thống không phân loại được
        ==> Dùng để gửi mail
        """

        selectedColumns = [
            'VSD.ThoiGian',
            'VSD.MaChungKhoan',
            'VSD.NgayDangKyCuoiCung',
            'VSD.TieuDe',
            'VSD.URL',
        ]
        self.__tableForJob7 = self._unclassifiableVSDTable[selectedColumns]
        return self.__tableForJob7


    @property
    def tableForJob8(self):

        """
        Danh sách các quyền TraLoiTucBangChungQuyen có GiaThanhToan < GiaThucHien
        ==> Dùng để gửi mail
        """

        table = pd.concat(
            [self.tableForJob4[['VSD.RightObject']], self.tableForJob5[['VSD.RightObject']]],
            axis = 0,
            ignore_index = True,
        )
        # chỉ lấy quyền TraLoiTucBangChungQuyen có SoTienChiTra < 0 (tức là GiaThanhToan < GiaThucHien)
        predicate = lambda x: x == 'TraLoiTucBangChungQuyen' and x.soTienChiTra < 0
        table = table.loc[table['VSD.RightObject'].map(predicate)]
        # chỉ quan tâm các URL của quyền
        table['VSD.URL'] = table['VSD.RightObject'].map(lambda x: x.URL)
        table['HOSE.URL'] = table['VSD.RightObject'].map(lambda x: x.HOSEURL)
        self.__tableForJob8 = table[['VSD.URL','HOSE.URL']]
        return self.__tableForJob8


    @property
    def _jointClassifiableTable(self):
        
        """
        Bảng join giữa VSD và Flex 220001, trạng thái hiện tại (chứa tất cả các ngày)
        """

        # join table
        jointTable = pd.merge(
            left = self._classifiableVSDTable,
            right = self._full220001Table,
            how = 'outer',
            left_on = ['VSD.NgayDangKyCuoiCung','VSD.MaChungKhoan','VSD.LoaiQuyen'],
            right_on = ['F220001.NgayDangKyCuoiCung','F220001.MaChungKhoan','F220001.LoaiQuyen'],
            indicator = 'VSD:220001',
        )

        # tạo 2 cột mask
        jointTable['InVSD'] = jointTable['VSD:220001'].map(lambda x: x in ('left_only','both'))
        jointTable['In220001'] = jointTable['VSD:220001'].map(lambda x: x in ('right_only','both'))

        # xóa cột indicator
        self.__jointClassifiableTable = jointTable.drop('VSD:220001', axis=1)

        return self.__jointClassifiableTable


    @property
    def _jointDueTodayTable(self):

        """
        Bảng join giữa VSD, Flex 220001
        với điều kiện Ngày Đăng Ký Cuối Cùng là hôm nay,
        và chỉ chứa mã chứng khoán có trong RSE0008 ngày hôm nay
        """

        # danh sách mã chứng khoán trong RSE0008
        tickersOfRSE0008 = tuple(self._fullRSE0008Table.squeeze(axis=1))
        
        # chỉ lấy các mã có ngày đăng ký cuối cùng là hôm nay trong bảng VSD
        mask = self._classifiableVSDTable['VSD.NgayDangKyCuoiCung'] == self._atDate
        dueTodayVSDTable = self._classifiableVSDTable.loc[mask]
        
        # chỉ lấy các mã trong RSE0008
        dueTodayVSDTable = dueTodayVSDTable.loc[dueTodayVSDTable['VSD.MaChungKhoan'].isin(tickersOfRSE0008)]

        # join table
        jointTable = pd.merge(
            left = dueTodayVSDTable,
            right = self._full220001Table,
            how = 'outer',
            left_on = ['VSD.NgayDangKyCuoiCung','VSD.MaChungKhoan','VSD.LoaiQuyen'],
            right_on = ['F220001.NgayDangKyCuoiCung','F220001.MaChungKhoan','F220001.LoaiQuyen'],
            indicator = 'VSD:220001',
        )

        # tạo 2 cột mask
        jointTable['InVSD'] = jointTable['VSD:220001'].map(lambda x: x in ('left_only','both'))
        jointTable['In220001'] = jointTable['VSD:220001'].map(lambda x: x in ('right_only','both'))

        # xóa cột indicator
        self.__jointDueTodayTable = jointTable.drop('VSD:220001', axis=1)

        return self.__jointDueTodayTable


    @staticmethod
    def __transformVSDTable(fullVSDTable: pd.DataFrame):

        """
        Xử lý data lấy từ VSD, trả ra:
            1. Bảng chứa các tin có thể phân loại quyền
            2. Bảng chưa các tin không thể phân loại quyền
        """

        # sort theo thời gian đăng tin để đảm bảo các tin mới nhất luôn nằm trên
        fullVSDTable = fullVSDTable.sort_values(
            by = ['VSD.ThoiGian'],
            ascending = False,
        )

        # tạo quyền
        fullVSDTable['VSD.RightObject'] = None
        for index in fullVSDTable.index:
            record = fullVSDTable.loc[index]
            fullVSDTable.loc[index,'VSD.RightObject'] = factory.RightFactory.createRight(record)

        # các tin không phân loại quyền (do không thể phân loại hoặc đa quyền)
        mask = fullVSDTable['VSD.RightObject'].isnull()
        unclassifiableVSDTable = fullVSDTable.loc[mask] 
        # các tin phân loại quyền được
        classifiableVSDTable = fullVSDTable.loc[~mask]
        
        # lấy tên loại quyền
        classifiableVSDTable['VSD.LoaiQuyen'] = classifiableVSDTable['VSD.RightObject'].apply(lambda x: x.tenQuyen)

        # drop các tin trùng, chỉ giữ lại tin mới nhất
        classifiableVSDTable = classifiableVSDTable.drop_duplicates(
            subset = [
                'VSD.NgayDangKyCuoiCung',
                'VSD.MaChungKhoan',
                'VSD.LoaiQuyen',
            ],
            keep = 'first',
        )

        return classifiableVSDTable, unclassifiableVSDTable



if __name__ == '__main__':

    self = DataFeed(
        query.DanhSachQuyenVSD(atDate=dt.datetime(2023,2,22)),
        query.F220001(), 
        query.ChungKhoanRSE0008(atDate=dt.datetime(2023,2,22)),
        query.LogTable()
    )






