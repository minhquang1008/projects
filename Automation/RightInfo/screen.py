import time
from abc import ABC, abstractmethod

import numpy as np
import cv2 as cv
from pywinauto.application import WindowSpecification

from automation.flex_gui.base import Flex
from automation.flex_gui.RightInfo import utils
from automation.flex_gui.RightInfo import right
from automation.flex_gui.RightInfo.type import Fraction, Percentage


class RightScreen(ABC):

    def __init__(
        self,
        rightWindow: WindowSpecification,
        rightObject: right.Right,
    ):
        self.rightWindow = rightWindow
        self.rightObject = rightObject

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertChungKhoan(self):
        textBox = self.rightWindow.child_window(auto_id='mskDataCODEID')
        Flex.sendTextByClipboard(textBox, self.rightObject.maChungKhoan)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertLoaiQuyen(self):
        textBox = self.rightWindow.child_window(auto_id='mskDataCATYPE')
        mapper = {
            'ThamDuDaiHoiCoDong': 'Tham dự đại hội cổ đông',
            'ChiaCoTucBangTien': 'Chia cổ tức bằng tiền',
            'ChiaCoTucBangCoPhieu': 'Chia cổ tức bằng cổ phiếu',
            'CoPhieuThuong': 'Cổ phiếu thưởng',
            'QuyenMua': 'Quyền mua',
            'TraLaiTraiPhieu': 'Trả lãi trái phiếu',
            'TraGocVaLaiTraiPhieu': 'Trả gốc và lãi trái phiếu',
            'ChuyenDoiTraiPhieuThanhCoPhieu': 'Chuyển đổi trái phiếu thành cổ phiếu',
            'ChuyenDoiCoPhieuThanhCoPhieu': 'Chuyển đổi cổ phiếu thành cổ phiếu',
            'TraLoiTucBangChungQuyen': 'Chi trả lợi tức chứng quyền',
        }
        Flex.sendTextByClipboard(textBox, mapper[self.rightObject.tenQuyen])
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertMaISIN(self):
        textBox = self.rightWindow.child_window(auto_id='mskDataISINCODE')
        Flex.sendTextByClipboard(textBox, self.rightObject.maISIN)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertNgayDangKyCuoiCung(self):
        textBox = self.rightWindow.child_window(auto_id='mskDataREPORTDATE')
        Flex.sendTextByClipboard(textBox, self.rightObject.ngayDangKyCuoiCung.strftime('%d/%m/%Y'))
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertNgayThucHienDuKien(self):
        textBox = self.rightWindow.child_window(auto_id='mskDataACTIONDATE')
        try:
            Flex.sendTextByClipboard(textBox, self.rightObject.ngayThucHienDuKien.strftime('%d/%m/%Y'))
            return 200
        except (Exception,):
            Flex.sendTextByClipboard(textBox, self.rightObject._sauNgayDangKyCuoiCung(months=1).strftime('%d/%m/%Y'))     
            return 204
            
    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertPhuongThucThuThueTien(self):
        textBox = self.rightWindow.child_window(auto_id='mskDataPITRATEMETHOD')
        Flex.sendTextByClipboard(textBox, self.rightObject.phuongThucThuThueTien)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertThueSuatThueTNCNChoTien(self):
        textBox = self.rightWindow.child_window(auto_id='mskDataPITRATE')
        Flex.sendTextByClipboard(textBox, self.rightObject.thueSuatThueTNCNChoTien)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertThueSuatThueTNCNChoCoPhieu(self):
        textBox = self.rightWindow.child_window(auto_id='mskDataPITRATESE')
        Flex.sendTextByClipboard(textBox, self.rightObject.thueSuatThueTNCNChoCoPhieu)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _sendKeyTab(self, times: int):
        self.rightWindow.type_keys('{TAB}'*times)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _clickAccept(self):
        # Click chấp nhận
        acceptButton = self.rightWindow.child_window(auto_id='btnOK')
        acceptButton.click_input()
        # Chờ ghi nhận dữ liệu xong -> click OK
        popUpWindow = self.rightWindow.app.window(title='FlexCustodian')
        for _ in range(2): # có thể xuất hiện 1 hoặc 2 pop up window
            if self.rightWindow.exists(timeout=5):  # nếu click đủ số lần cần thiết thì rightWindow sẽ tự tắt
                popUpWindow.child_window(title='OK').click_input()
        return 200


    @abstractmethod
    def _insertTyLeThucHien(self):
        pass

    def __repr__(self):
        return __class__.__qualname__

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def create(self):
        self._insertChungKhoan()
        self._insertLoaiQuyen()
        self.edit(emitExitCode=False)
        return 200

    @abstractmethod
    def edit(self, emitExitCode: bool=True):
        pass


class ThamDuDaiHoiCoDong(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData005DEVIDENTSHARES')
        try:
            Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204


class ChiaCoTucBangTien(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        # luôn chọn chia theo tỷ lệ
        valueBox = self.rightWindow.child_window(auto_id='mskData010TYPERATE')
        Flex.sendTextByClipboard(valueBox, "Chia theo tỷ lệ")
        valueBox = self.rightWindow.child_window(auto_id='mskData010DEVIDENTRATE')
        try:
            # nhập tỷ lệ thực hiện
            Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204


class ChiaCoTucBangCoPhieu(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertGiaQuyDoiChoCoPhieuLoLe()
        self._insertQuyDinhLamTron()
        self._insertSoChuSoThapPhanCKLeQuyDoi()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        # luôn chọn chia theo tỷ lệ trước
        typeTextBox = self.rightWindow.child_window(auto_id='mskData011RATIOTYPE')
        Flex.sendTextByClipboard(typeTextBox, "Chia theo tỷ lệ")
        valueBox = self.rightWindow.child_window(auto_id='mskData011DEVIDENTRATE')
        if isinstance(self.rightObject.tyLeThucHien, Percentage):
            try:
                Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
                return 200
            except (Exception,):
                valueBox.type_keys('{TAB}')
                return 204
        elif isinstance(self.rightObject.tyLeThucHien, Fraction):  # chia theo giá trị
            # nhập 0 vào box chia theo tỷ lệ
            Flex.sendTextByKeyboard(valueBox, Percentage('0'))
            # nhập giá trị vào box chia theo giá trị
            Flex.sendTextByClipboard(typeTextBox, "Chia theo giá trị/(CP,CW)")
            valueBox = self.rightWindow.child_window(auto_id='mskData011DEVIDENTSHARES')
            try:
                Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
                return 200
            except (Exception,):
                valueBox.type_keys('{TAB}')
                return 204
        else:
            raise ValueError(f'TyLeThucHien must be either Percentage or Fraction, get {self.rightObject.tyLeThucHien}')

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertGiaQuyDoiChoCoPhieuLoLe(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData011EXPRICE')
        Flex.sendTextByClipboard(valueBox, self.rightObject.giaQuyDoiChoCoPhieuLoLe)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertQuyDinhLamTron(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData011ROUNDTYPE')
        Flex.sendTextByClipboard(valueBox, self.rightObject.quyDinhLamTron)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertSoChuSoThapPhanCKLeQuyDoi(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData011CIROUNDTYPE')
        Flex.sendTextByClipboard(valueBox, self.rightObject.soChuSoThapPhanChungKhoanLeQuyDoi)
        return 200


class CoPhieuThuong(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertGiaQuyDoiChoCoPhieuLoLe()
        self._insertQuyDinhLamTron()
        self._insertSoChuSoThapPhanCKLeQuyDoi()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        # luôn chọn chia theo tỷ lệ trước
        typeTextBox = self.rightWindow.child_window(auto_id='mskData021RATIOTYPE')
        Flex.sendTextByClipboard(typeTextBox, "Chia theo tỷ lệ")
        valueBox = self.rightWindow.child_window(auto_id='mskData021DEVIDENTRATE')
        if isinstance(self.rightObject.tyLeThucHien, Percentage):
            try:
                Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
                return 200
            except (Exception,):
                valueBox.type_keys('{TAB}')
                return 204
        elif isinstance(self.rightObject.tyLeThucHien, Fraction):  # chia theo giá trị
            # nhập 0 vào box chia theo tỷ lệ
            Flex.sendTextByKeyboard(valueBox, Percentage('0'))
            # nhập giá trị vào box chia theo giá trị
            Flex.sendTextByClipboard(typeTextBox, "Chia theo giá trị/(CP,CW)")
            valueBox = self.rightWindow.child_window(auto_id='mskData021EXRATE')
            try:
                Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
                return 200
            except (Exception,):
                valueBox.type_keys('{TAB}')
                return 204
        else:
            raise ValueError(f'TyLeThucHien must be either Percentage or Fraction, get {self.rightObject.tyLeThucHien}')

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertGiaQuyDoiChoCoPhieuLoLe(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData021EXPRICE')
        Flex.sendTextByClipboard(valueBox, self.rightObject.giaQuyDoiChoCoPhieuLoLe)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertQuyDinhLamTron(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData021ROUNDTYPE')
        Flex.sendTextByClipboard(valueBox, self.rightObject.quyDinhLamTron)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertSoChuSoThapPhanCKLeQuyDoi(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData021CIROUNDTYPE')
        Flex.sendTextByClipboard(valueBox, self.rightObject.soChuSoThapPhanChungKhoanLeQuyDoi)
        return 200


class QuyenMua(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertGiaPhatHanh()
        self._insertNgayBatDauVaKetThucChuyenNhuong()
        self._insertNgayBatDauVaKetThucDangKyQuyenMua()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData014RIGHTOFFRATE')
        try:
            Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeCoPhieuSoHuuQuyen(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData014EXRATE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeCoPhieuSoHuuQuyen)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertGiaPhatHanh(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData014EXPRICE')
        try:
            Flex.sendTextByClipboard(valueBox, self.rightObject.giaPhatHanh)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertNgayBatDauVaKetThucChuyenNhuong(self):
        startDateBox = self.rightWindow.child_window(auto_id='mskData014FRDATETRANSFER')
        endDateBox = self.rightWindow.child_window(auto_id='mskData014TODATETRANSFER')
        try:
            startDate, endDate = self.rightObject.ngayBatDauVaKetThucChuyenNhuong.strftime('%d/%m/%Y')
            Flex.sendTextByClipboard(startDateBox, startDate)
            Flex.sendTextByClipboard(endDateBox, endDate)
            return 200
        except (Exception,):
            startDateBox.type_keys('{TAB}')
            endDateBox.type_keys('{TAB}')
            return 204


    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertNgayBatDauVaKetThucDangKyQuyenMua(self):
        startDateBox = self.rightWindow.child_window(auto_id='mskData014BEGINDATE')
        endDateBox = self.rightWindow.child_window(auto_id='mskData014DUEDATE')
        try:
            startDate, endDate = self.rightObject.ngayBatDauVaKetThucDangKyQuyenMua.strftime('%d/%m/%Y')
            Flex.sendTextByClipboard(startDateBox, startDate)
            Flex.sendTextByClipboard(endDateBox, endDate)
            return 200
        except (Exception,):
            startDateBox.type_keys('{TAB}')
            endDateBox.type_keys('{TAB}')
            return 204


class TraLaiTraiPhieu(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData015INTERESTRATE')
        try:
            Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204


class TraGocVaLaiTraiPhieu(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData016INTERESTRATE')
        try:
            Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204


class ChuyenDoiTraiPhieuThanhCoPhieu(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertGiaQuyDoiChoPhanLe()
        self._insertQuyDinhLamTron()
        self._insertSoChuSoThapPhanChungKhoanLeQuyDoi()
        self._insertCoPhieuVeLaChoGiaoDich()
        self._insertMaCoPhieuChuyenDoi()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData017EXRATE')
        try:
            Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertMaCoPhieuChuyenDoi(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData017TOCODEID')
        try:
            Flex.sendTextByKeyboard(valueBox, self.rightObject.maCoPhieuChuyenDoi)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertGiaQuyDoiChoPhanLe(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData017EXPRICE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.giaQuyDoiChoPhanLe)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertQuyDinhLamTron(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData017ROUNDTYPE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.quyDinhLamTron)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertSoChuSoThapPhanChungKhoanLeQuyDoi(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData017CIROUNDTYPE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.soChuSoThapPhanChungKhoanLeQuyDoi)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertCoPhieuVeLaChoGiaoDich(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData017ISWFT')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.coPhieuVeLaChoGiaoDich)
        return 200


class ChuyenDoiCoPhieuThanhCoPhieu(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertNgayDuKienHuyCoPhieuCu()
        self._insertNgayDuKienHuyCoPhieuMoi()
        self._insertTyLeThucHien()
        self._insertGiaQuyDoiChoPhanLe()
        self._insertQuyDinhLamTron()
        self._insertSoChuSoThapPhanChungKhoanLeQuyDoi()
        self._insertCoPhieuVeLaChoGiaoDich()
        self._insertMaCoPhieuChuyenDoi()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData020DEVIDENTSHARES')
        try:
            Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertNgayDuKienHuyCoPhieuCu(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData020CANCELDATE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.ngayDuKienHuyCoPhieuCu.strftime('%d/%m/%Y'))
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertNgayDuKienHuyCoPhieuMoi(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData020RECEIVEDATE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.ngayDuKienNhanCoPhieuMoi.strftime('%d/%m/%Y'))
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertMaCoPhieuChuyenDoi(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData020TOCODEID')
        try:
            Flex.sendTextByKeyboard(valueBox, self.rightObject.maCoPhieuChuyenDoi)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertGiaQuyDoiChoPhanLe(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData020EXPRICE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.giaQuyDoiChoPhanLe)
        return 200
    
    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertQuyDinhLamTron(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData020ROUNDTYPE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.quyDinhLamTron)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertSoChuSoThapPhanChungKhoanLeQuyDoi(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData020CIROUNDTYPE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.soChuSoThapPhanChungKhoanLeQuyDoi)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertCoPhieuVeLaChoGiaoDich(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData020ISWFT')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.coPhieuVeLaChoGiaoDich)
        return 200


class TraLoiTucBangChungQuyen(RightScreen):

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def edit(self, emitExitCode: bool=True):
        self._insertMaISIN()
        self._insertNgayDangKyCuoiCung()
        self._insertNgayThucHienDuKien()
        self._insertTyLeThucHien()
        self._insertSoTienChiTra()
        self._insertQuyDinhLamTron()
        self._insertPhuongThucThuThueTien()
        self._insertThueSuatThueTNCNChoTien()
        self._insertThueSuatThueTNCNChoCoPhieu()
        self._sendKeyTab(times=50)
        self._clickAccept()
        if emitExitCode:
            return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertTyLeThucHien(self):
        typeTextBox = self.rightWindow.child_window(auto_id='mskData028TYPERATE')
        Flex.sendTextByClipboard(typeTextBox, "Chia theo tỷ lệ")
        valueBox = self.rightWindow.child_window(auto_id='mskData028DEVIDENTRATE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.tyLeThucHien)
        return 200

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertSoTienChiTra(self):
        typeTextBox = self.rightWindow.child_window(auto_id='mskData028TYPERATE')
        Flex.sendTextByClipboard(typeTextBox, "Chia theo giá trị/(CP,CW)")
        valueBox = self.rightWindow.child_window(auto_id='mskData028DEVIDENTVALUE')
        try:
            Flex.sendTextByClipboard(valueBox, self.rightObject.soTienChiTra)
            return 200
        except (Exception,):
            valueBox.type_keys('{TAB}')
            return 204

    @utils.Decorator.logRightWindowFunctions(logger=utils.Logging.logger)
    def _insertQuyDinhLamTron(self):
        valueBox = self.rightWindow.child_window(auto_id='mskData028ROUNDTYPE')
        Flex.sendTextByKeyboard(valueBox, self.rightObject.quyDinhLamTron)
        return 200


class MainScreen(Flex):

    def __init__(
        self,
        username,
        password
    ):
        super().__init__()
        self.start(existing=False) # Tạo Flex instance mới
        self.login(username,password)
        self.insertFuncCode('220001')
        self.funcWindow = self.app.window(auto_id='frmSearch')
        self.rightWindow = self.app.window(auto_id='frmMaster')
        self.funcWindow.wait('exists',timeout=10)
        self.funcWindow.maximize()

    @utils.Decorator.logMaintWindowFunctions(logger=utils.Logging.logger)
    def clearAllCriteria(self):
        Flex.setFocus(self.funcWindow)
        self.funcWindow.child_window(auto_id='btnRemoveAll').click_input()

    @utils.Decorator.logMaintWindowFunctions(logger=utils.Logging.logger)
    def selectMaThucHienQuyen(self, value: str):
        # set focus
        Flex.setFocus(self.funcWindow)
        # chọn tiêu chí "Mã thực hiện quyền"
        self.funcWindow.child_window(auto_id='cboField').select('Mã thực hiện quyền')
        # chọn phép toán LIKE
        self.funcWindow.child_window(auto_id='cboOperator').select('LIKE')
        # nhập giá trị Mã thực hiện quyền
        textBox = self.funcWindow.child_window(auto_id='txtValue')
        Flex.sendTextByKeyboard(textBox, value)
        # click add điều kiện vừa chọn
        self.funcWindow.child_window(auto_id='btnAdd').click_input()
        # click search (còn lại duy nhất 1 record)
        self.funcWindow.child_window(auto_id='btnSearch').click_input()
        # chờ hệ thống load kết quả xong
        time.sleep(1)

    @utils.Decorator.logMaintWindowFunctions(logger=utils.Logging.logger)
    def clickAction(self, action: str):
        # screenshot màn hình
        Flex.setFocus(self.funcWindow)
        actionWindow = self.funcWindow.child_window(title='SMS')
        actionImage = cv.cvtColor(
            src = np.array(actionWindow.capture_as_image()), 
            code = cv.COLOR_RGB2BGR,
        )
        # crop 10 cột cuối vì layer không được phủ hết
        actionImage = actionImage[:,:-20,:]
        # tìm cột có occurence cao nhất (cột nền)
        unique, count = np.unique(actionImage, return_counts=True, axis=1)
        mostFrequentColumn = unique[:,np.argmax(count),:]
        # crop đến cột cuối cùng không phải là cột nền
        columnMask = ~(actionImage==mostFrequentColumn[:,np.newaxis,:]).all(axis=(0,2))
        lastColumn = np.argwhere(columnMask).max()
        croppedImage = actionImage[:,:lastColumn,:]
        # tính tọa độ nút bấm
        if action == 'edit': 
            n = 12
        elif action == 'create': 
            n = 2
        else: 
            raise ValueError(f'action expects either "edit" or "create", get "{action}"')
        midPoint = croppedImage.shape[1]//25*n, croppedImage.shape[0]//2
        # click trên tọa độ được tính (đến khi cửa sổ quyền mở ra thì ngừng)
        while not self.rightWindow.exists(timeout=1):
            actionWindow.click_input(coords=midPoint, double=True)

    def __repr__(self):
        return self.__class__.__qualname__

    def __del__(self):
        self.mainWindow.close()