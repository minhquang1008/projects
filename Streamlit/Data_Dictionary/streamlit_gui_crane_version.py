import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import pickle
from searcher import Data
import datetime as dt
import time

returning_dictionary = {0: 'information',
                     1: 'information/dim - branch',
                     2: 'information/dim - branch/row_id',
                     3: 'information/dim - branch/integration_id',
                     4: 'information/dim - branch/datasource_id',
                     5: 'information/dim - branch/branch_code',
                     6: 'information/dim - branch/branch_name',
                     7: 'information/dim - branch/region_id',
                     8: 'information/dim - branch/status',
                     9: 'information/dim - broker',
                     10: 'information/dim - broker/row_id',
                     11: 'information/dim - broker/integration_id',
                     12: 'information/dim - broker/datasource_id',
                     13: 'information/dim - broker/broker_code',
                     14: 'information/dim - broker/broker_name',
                     15: 'information/dim - broker/gender',
                     16: 'information/dim - broker/birthday',
                     17: 'information/dim - broker/region_id',
                     18: 'information/dim - broker/nationality',
                     19: 'information/dim - broker/create_date',
                     20: 'information/dim - broker/modify_date',
                     21: 'information/dim - company',
                     22: 'information/dim - company/row_id',
                     23: 'information/dim - company/integration_id',
                     24: 'information/dim - company/datasource_id',
                     25: 'information/dim - company/company_code',
                     26: 'information/dim - company/company_name',
                     27: 'information/dim - customer',
                     28: 'information/dim - customer/row_id',
                     29: 'information/dim - customer/integration_id',
                     30: 'information/dim - customer/datasource_id',
                     31: 'information/dim - customer/customer_subcode',
                     32: 'information/dim - customer/customer_code',
                     33: 'information/dim - customer/customer_name',
                     34: 'information/dim - customer/birthday',
                     35: 'information/dim - customer/gender',
                     36: 'information/dim - customer/nationality',
                     37: 'information/dim - customer/region_id',
                     38: 'information/dim - customer/contract_number_normal',
                     39: 'information/dim - customer/contract_number_margin',
                     40: 'information/dim - customer/create_date',
                     41: 'information/dim - customer/modify_date',
                     42: 'information/dim - territory',
                     43: 'information/dim - territory/row_id',
                     44: 'information/dim - territory/integration_id',
                     45: 'information/dim - territory/flex_province',
                     46: 'information/dim - territory/bravo_province',
                     47: 'information/dim - territory/district_code',
                     48: 'information/dim - territory/district_name',
                     49: 'information/dim - territory/district_en',
                     50: 'information/dim - territory/province_code',
                     51: 'information/dim - territory/province_name',
                     52: 'information/dim - territory/province_en',
                     53: 'information/dim - vendor',
                     54: 'information/dim - vendor/row_id',
                     55: 'information/dim - vendor/integration_id',
                     56: 'information/dim - vendor/customer_subcode',
                     57: 'information/dim - vendor/customer_code',
                     58: 'information/dim - vendor/customer_name',
                     59: 'information/dim - vendor/birthday',
                     60: 'information/dim - vendor/gender',
                     61: 'information/dim - vendor/nationality',
                     62: 'information/dim - vendor/province',
                     63: 'information/dim - vendor/contract_number_normal',
                     64: 'information/dim - vendor/contract_number_margin',
                     }
#
# with open('returning_dictionary.pkl', 'wb') as file:
#     pickle.dump(returning_dictionary, file)

with open('returning_dictionary.pkl', 'rb') as file:
    returning_dictionary = pickle.load(file)
# https://i.pinimg.com/originals/60/a5/85/60a58511e5c70a418ac743f7df8134fa.gif
# https://wallpapercave.com/uwp/uwp2493549.gif
# https://i.ibb.co/DCb3nvR/crane.jpg
st.title('DATA DICTIONARY')
with st.spinner('Wait for it...'):
    time.sleep(2)
st.markdown('''
<style>
[data-testid="stAppViewContainer"] {
background-image: url('https://images4.alphacoders.com/104/1047187.jpg');
background-size: cover;
background-repeat: no-repeat;
}
[data-testid="stSidebar"] {
background-image: url('https://i.ibb.co/DCb3nvR/crane.jpg');
background-size: cover;
margin-top: 0px;
margin-left: 40px;
opacity: 0.9;
background-repeat: no-repeat;
border-style: double;
border-color: #17384D;
border-radius: 30px;
width: 450px !important;
}
[class="block-container st-emotion-cache-1y4p8pa ea3mdgi4"] {
background-color: #EEEADD;
margin-top: 70px;
opacity: 0.9;
background-repeat: no-repeat;
border-style: double;
border-color: #17384D;
border-radius: 20px;
}
[data-testid='stHeader'] {
background-color: #EEEADD;
opacity: 0.0;
background-repeat: no-repeat;
}
[class='css-zq5wmm ezrtsby0'] {
background-color: #e8e1e0;
opacity: 0.9;
background-repeat: no-repeat;
}
</style>
''', unsafe_allow_html=True)


with open('last_search.pkl', 'rb') as file:
    last_search = pickle.load(file)
df_search = pd.DataFrame(list(returning_dictionary.items()), columns=['index', 'path'])
text_search = st.selectbox("Search column's name", df_search['path'])
if text_search != last_search:
    t2 = dt.datetime.now()
    with open('last_search.pkl', 'wb') as file:
        pickle.dump(text_search, file)
else:
    t2 = dt.datetime(1993, 4, 16)
sac.divider(icon='yin-yang', align='center', direction='horizontal', dashed=False, bold=False)
with st.sidebar:

    st.image("logo.png", width=200)
    with open('last_clicked.pkl', 'rb') as file:
        last_clicked = pickle.load(file)
    clicked = sac.tree(items=[
        sac.TreeItem('Information', tooltip='item1 tooltip', children=[
            sac.TreeItem('Branch', icon='table', children=[sac.TreeItem(f'{i}', icon='arrow-return-right') for i in
                                        [returning_dictionary.get(k).split('/')[-1] for k in range(2, 9, 1)]]),
            sac.TreeItem('Broker', icon='table', children=[sac.TreeItem(f'{i}', icon='arrow-return-right') for i in
                                        [returning_dictionary.get(k).split('/')[-1] for k in range(10, 21, 1)]]),
            sac.TreeItem('Company', icon='table', children=[sac.TreeItem(f'{i}', icon='arrow-return-right') for i in
                                        [returning_dictionary.get(k).split('/')[-1] for k in range(22, 27, 1)]]),
            sac.TreeItem('Customer', icon='table', children=[sac.TreeItem(f'{i}', icon='arrow-return-right') for i in
                                        [returning_dictionary.get(k).split('/')[-1] for k in range(28, 42, 1)]]),
            sac.TreeItem('Territory', icon='table', children=[sac.TreeItem(f'{i}', icon='arrow-return-right') for i in
                                        [returning_dictionary.get(k).split('/')[-1] for k in range(43, 53, 1)]]),
            sac.TreeItem('Vendor', icon='table', children=[sac.TreeItem(f'{i}', icon='arrow-return-right') for i in
                                        [returning_dictionary.get(k).split('/')[-1] for k in range(54, 65, 1)]])
        ]),
        sac.TreeItem('Trading', tooltip='item2 tooltip', disabled=True, children=[
            sac.TreeItem('Trading', disabled=True, icon='table'),
            sac.TreeItem('Price Board',  disabled=True, icon='table')
        ]),
        sac.TreeItem('Margin', tooltip='item3 tooltip', disabled=True, children=[
            sac.TreeItem('Room', disabled=True, icon='table'),
            sac.TreeItem('Margin Detail',  disabled=True, icon='table')
        ]),
    ],  label='Table',
        index=0,
        format_func='title',
        icon='folder-fill',
        height=None,
        open_index=None,
        open_all=False,
        checkbox=False,
        show_line=True,
        checkbox_strict=False,
        return_index=True)
    if clicked != last_clicked:
        t1 = dt.datetime.now()
        with open('last_clicked.pkl', 'wb') as file:
            pickle.dump(clicked, file)
    else:
        t1 = dt.datetime(1993, 4, 16)
# ----------------------------------------------------------------------------
data = Data()

if clicked and text_search and t1 > t2:
    the_path = returning_dictionary.get(clicked[0])
else:
    the_path = text_search
st.text(the_path.title())
if len(the_path.split('/')) == 3:
    st.write(f'''## {the_path.split('/')[-1].title()}''')
    st.write('### Data Source')
    data.table = the_path.split('/')[1].title()
    df = data.getData(the_path.split('/')[-1])
    st.dataframe(df.style.hide(axis="index"))
