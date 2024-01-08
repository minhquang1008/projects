import pickle
import pandas as pd


# sheet_list = pd.ExcelFile(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx').sheet_names
def get_updated(table, company_table, margin_table, trading_table, customer_table):
    sheet_id = '1f97mxqZXFH1I9kE6Y4f0vB5oMf1lhBtmDX3lOvEXzeo'
    column_list = []
    for i in table:
        df = pd.read_excel(
            f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx',
            sheet_name=i,
            header=1
        )
        with open(f'{i}.pkl', 'wb') as file:
            pickle.dump(df, file)
        lst = df['COLUMN.3'].dropna().unique().tolist()
        if i in company_table:
            lst = [f'Company Information/{i}/' + k for k in lst]
        elif i in margin_table:
            lst = [f'Margin/{i}/' + k for k in lst]
        elif i in trading_table:
            lst = [f'Trading/{i}/' + k for k in lst]
        elif i in customer_table:
            lst = [f'Customer Information/{i}/' + k for k in lst]
        [column_list.append(k) for k in lst]
    for i in column_list:
        if column_list.index(i) == 0:
            column_list.insert(0, i.split('/')[0])
            column_list.insert(1, i.split('/')[0]+'/'+i.split('/')[1])
        elif column_list.index(i) != 0 and i.split('/')[1] != anchor_1 and i.split('/')[0] == anchor_0:
            column_list.insert(column_list.index(i), i.split('/')[0] + '/' + i.split('/')[1])
        elif column_list.index(i) != 0 and i.split('/')[0] != anchor_0 and i.split('/')[1] != anchor_1:
            column_list.insert(column_list.index(i), i.split('/')[0])
            column_list.insert(column_list.index(i), i.split('/')[0]+'/'+i.split('/')[1])
        anchor_0 = i.split('/')[0]
        anchor_1 = i.split('/')[1]
    return dict(zip(range(len(column_list)), column_list))


class Data:
    def __init__(self):
        self.__table = None

    @property
    def table(self):
        return self.__table

    @table.setter
    def table(self, value):
        self.__table = value

    def getData(self, column_name):
        with open(f'{self.__table}.pkl', 'rb') as file:
            df = pickle.load(file)
        df.dropna(axis=0, how='all', inplace=True)
        return df[df['COLUMN.3'] == column_name]

        

