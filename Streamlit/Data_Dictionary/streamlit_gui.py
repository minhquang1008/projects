import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import pickle
from searcher import Data, get_updated
import datetime as dt
from streamlit_javascript import st_javascript


def client_ip():

    url = 'https://api.ipify.org?format=json'

    script = (f'await fetch("{url}").then('
                'function(response) {'
                    'return response.json();'
                '})')

    try:
        result = st_javascript(script)

        if isinstance(result, dict) and 'ip' in result and len(result['ip']) != 0:
            return result['ip']
        else:
            client_ip()
    except(Exception,):
        pass

sheet_list = ['DIM - BRANCH', 'DIM - BROKER', 'DIM - STOCK_INFO',
              'FACT - OUTSTANDING', 'FACT - ROOM', 'FACT - LIMIT_REQUESTS',
              'FACT - TRADING', 'FACT - PRICE_BOARD', 'FACT - POSTED_TRANSACTION',
              'DIM - CUSTOMER', 'FACT - CUSTOMER_CONTRACT']
company_table = ['DIM - BRANCH', 'DIM - BROKER', 'DIM - STOCK_INFO']
margin_table = ['FACT - OUTSTANDING', 'FACT - ROOM', 'FACT - LIMIT_REQUESTS']
trading_table = ['FACT - TRADING', 'FACT - PRICE_BOARD', 'FACT - POSTED_TRANSACTION']
customer_table = ['DIM - CUSTOMER', 'FACT - CUSTOMER_CONTRACT']

# st-emotion-cache
with open('returning_dictionary.pkl', 'rb') as file:
    returning_dictionary = pickle.load(file)
with open('last_update.pkl', 'rb') as file:
    last_update = pickle.load(file)
with open('last_search.pkl', 'rb') as file:
    last_search = pickle.load(file)
st.markdown('''
<style>
[data-testid="stAppViewContainer"] {
background-image: url('https://janegee.com/cdn/shop/articles/janegee-clean-beauty-natural-blog-creating-white-space-2.jpg?v=1578514704');
background-size: cover;
background-repeat: no-repeat;
}
[data-testid="stSidebar"] {
background-image: url('https://i.pinimg.com/564x/b3/cd/06/b3cd06d39f7c85313649d605041b4c3d.jpg');
background-size: cover;
margin-top: 0px;
margin-left: 40px;
opacity: 0.9;
background-repeat: no-repeat;
border-style: double;
border-color: #34693a;
border-radius: 20px;
}
[class="block-container st-emotion-cache-1y4p8pa ea3mdgi2"] {
background-color: #FFFFFF;
padding-top: 5px;
margin-top: 0px;
opacity: 0.9;
background-repeat: no-repeat;
border-style: double;
border-color: #34693a;
border-radius: 20px;
line-height: 1.2;
}
[data-testid='stHeader'] {
background-color: #FFFFFF;
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
IP = client_ip()
if IP == '116.118.113.140' or IP == '115.78.11.116':
    df_search = pd.DataFrame(list(returning_dictionary.items()), columns=['index', 'path'])
    text_search = st.selectbox("Search column's name", df_search['path'])
    st.title('DATA DICTIONARY')
    if text_search != last_search:
        t2 = dt.datetime.now()
        with open('last_search.pkl', 'wb') as file:
            pickle.dump(text_search, file)
    else:
        t2 = dt.datetime(1993, 4, 16)
    with st.sidebar:
        st.image("logo.png", width=200)
        with open('last_clicked.pkl', 'rb') as file:
            last_clicked = pickle.load(file)
        clicked = sac.tree(items=[
            sac.TreeItem('Company Information', tooltip='item1 tooltip', children=[
                sac.TreeItem(i.split('-')[-1].strip(), icon='table', children=[sac.TreeItem(f'{k}', icon='arrow-return-right') for k in
                                         [q.split('/')[-1] for q in returning_dictionary.values()
                                          if len(q.split('/')) == 3 and q.split('/')[1] == i]])
                for i in company_table
            ]),
            sac.TreeItem('Margin', tooltip='item3 tooltip',  children=[
                sac.TreeItem(i.split('-')[-1].strip(), icon='table',
                             children=[sac.TreeItem(f'{k}', icon='arrow-return-right') for k in
                                       [q.split('/')[-1] for q in returning_dictionary.values()
                                        if len(q.split('/')) == 3 and q.split('/')[1] == i]])
                for i in margin_table
            ]),
            sac.TreeItem('Trading', tooltip='item2 tooltip', children=[
                sac.TreeItem(i.split('-')[-1].strip(), icon='table',
                             children=[sac.TreeItem(f'{k}', icon='arrow-return-right') for k in
                                       [q.split('/')[-1] for q in returning_dictionary.values()
                                        if len(q.split('/')) == 3 and q.split('/')[1] == i]])
                for i in trading_table
            ]),
            sac.TreeItem('Customer Information', tooltip='item4 tooltip', children=[
                sac.TreeItem(i.split('-')[-1].strip(), icon='table',
                             children=[sac.TreeItem(f'{k}', icon='arrow-return-right') for k in
                                       [q.split('/')[-1] for q in returning_dictionary.values()
                                        if len(q.split('/')) == 3 and q.split('/')[1] == i]])
                for i in customer_table
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
        st.write(f"The client ip is {IP}")
        if st.button("Update"):
            with st.spinner('Wait for it...'):
                returning_dictionary = get_updated(sheet_list, company_table, margin_table, trading_table, customer_table)
                with open('returning_dictionary.pkl', 'wb') as file:
                    pickle.dump(returning_dictionary, file)
                last_update = dt.datetime.now()
                with open('last_update.pkl', 'wb') as file:
                    pickle.dump(last_update, file)

    # ----------------------------------------------------------------------------
    data = Data()
    if clicked and text_search and t1 > t2:
        the_path = returning_dictionary.get(clicked)
    else:
        the_path = text_search
    st.text(the_path.upper())
    if len(the_path.split('/')) == 3:
        data.table = the_path.split('/')[1].upper()
        df = data.getData(the_path.split('/')[-1])
        st.write(f'''## {the_path.split('/')[-1].upper()}''')
        st.write('ARTICLE - ' + str(df['ARTICLE'].iloc[0].strftime("%d/%m/%Y")))
        if str(df['DESCRIPTION'].iloc[0]) != 'nan':
            st.write(str(df['DESCRIPTION'].iloc[0]))
        st.write('### Managed By')
        st.write(str(df['MANAGED BY'].iloc[0]))
        st.write('### Data source')
        st.write(df[['SOURCE', 'TABLE', 'COLUMN.1']].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        if str(df['FORMULA'].iloc[0]) != 'nan':
            st.write('### Formula')
            st.write(str(df['FORMULA'].iloc[0]))
    st.divider()
    st.success(f'last update: {last_update.strftime("%m/%d/%Y, %H:%M:%S")}')
elif IP is None:
    st.write("### Wait for it")
else:
    st.write("### Access Denied! You are not allowed to access this page")




