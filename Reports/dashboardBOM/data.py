import os
import datetime as dt
import pandas as pd
from typing import Literal
from request import connect_DWH_CoSo, connect_DWH_PhaiSinh


class _Data:

    def __init__(
            self,
            dataDate: dt.datetime,
            domain: Literal['CoSo', 'PhaiSinh']
    ) -> None:

        className = self.__class__.__qualname__
        self.__sqlScriptPath = f'./{domain.lower()}/sql/{className.lower()}'
        if domain == 'CoSo':
            self.connection = connect_DWH_CoSo
        else:
            self.connection = connect_DWH_PhaiSinh
        self.dataDate = dataDate
        self.__dataStore = None

    @property
    def _dataStore(self):
        # Cache
        if self.__dataStore is not None:
            return self.__dataStore
        # Danh sách các file trong folder chứa script SQL
        scriptFiles = [name for name in os.listdir(self.__sqlScriptPath) if name.endswith('.sql')]
        # Loop và query từng file
        dataStore = dict()
        for fileName in scriptFiles:
            print(f'Querying {self.__class__.__qualname__} {fileName}...')
            dataName = fileName.replace('.sql', '')
            with open(f'{self.__sqlScriptPath}/{fileName}', mode='r', encoding='utf-8-sig') as file:
                script = _Util.passDateToSqlScript(self.dataDate, file.read())
            data = pd.read_sql(sql=script, con=self.connection, parse_dates=['Date'])
            dataStore.update({dataName: data})
        # Return
        self.__dataStore = dataStore
        return self.__dataStore

    def get(self, tableName: str) -> pd.DataFrame:
        availableTables = self._dataStore.keys()
        if tableName not in availableTables:
            raise ValueError(f'Invalid table name. Only accept [{availableTables}]')
        fullTable = self._dataStore.get(tableName)
        return fullTable


class _Util:

    @staticmethod
    def passDateToSqlScript(
            date: dt.datetime,
            sql: str,
    ):
        dateString = date.strftime(r'%Y-%m-%d')
        return sql.replace('@YYYYMMDD', f"'{dateString}'")


class Daily(_Data):
    def __init__(self, dataDate: dt.datetime, domain: Literal['CoSo', 'PhaiSinh']) -> None:
        super().__init__(dataDate, domain)


class MTD(_Data):
    def __init__(self, dataDate: dt.datetime, domain: Literal['CoSo', 'PhaiSinh']) -> None:
        super().__init__(dataDate, domain)


class YTD(_Data):
    def __init__(self, dataDate: dt.datetime, domain: Literal['CoSo', 'PhaiSinh']) -> None:
        super().__init__(dataDate, domain)