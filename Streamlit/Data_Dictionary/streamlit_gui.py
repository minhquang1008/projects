import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import pickle
from searcher import Data, get_updated
import datetime as dt
sheet_list = ['Dim - Branch', 'Dim - Broker', 'Dim - Company', 'Dim - Customer', 'Dim - Territory', 'Dim - Vendor', 'Fact - Outstanding', 'Fact - Room', 'Fact - Margin Detail', 'Fact - Trading', 'Fact - Price Board',]
information_table = ['Dim - Branch', 'Dim - Broker', 'Dim - Company', 'Dim - Customer', 'Dim - Territory', 'Dim - Vendor']
margin_table = ['Fact - Outstanding', 'Fact - Room', 'Fact - Margin Detail']
trading_table = ['Fact - Trading', 'Fact - Price Board']

# st-emotion-cache

with open('returning_dictionary.pkl', 'rb') as file:
    returning_dictionary = pickle.load(file)
with open('last_update.pkl', 'rb') as file:
    last_update = pickle.load(file)
with open('last_search.pkl', 'rb') as file:
    last_search = pickle.load(file)

st.title('DATA DICTIONARY')
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
[class="block-container st-emotion-cache-1y4p8pa ea3mdgi4"] {
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
df_search = pd.DataFrame(list(returning_dictionary.items()), columns=['index', 'path'])
text_search = st.selectbox("Search column's name", df_search['path'])
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
        sac.TreeItem('Information', tooltip='item1 tooltip', children=[
            sac.TreeItem(i.split('-')[-1].strip(), icon='table', children=[sac.TreeItem(f'{k}', icon='arrow-return-right') for k in
                                     [q.split('/')[-1] for q in returning_dictionary.values()
                                      if len(q.split('/')) == 3 and q.split('/')[1] == i]])
            for i in information_table
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
    if st.button("Update"):
        with st.spinner('Wait for it...'):
            returning_dictionary = get_updated(sheet_list, information_table, margin_table, trading_table)
            with open('returning_dictionary.pkl', 'wb') as file:
                pickle.dump(returning_dictionary, file)
            last_update = dt.datetime.now()
            with open('last_update.pkl', 'wb') as file:
                pickle.dump(last_update, file)

# ----------------------------------------------------------------------------
data = Data()
if clicked and text_search and t1 > t2:
    the_path = returning_dictionary.get(clicked[0])
else:
    the_path = text_search
st.text(the_path.title())
if len(the_path.split('/')) == 3:
    data.table = the_path.split('/')[1].title()
    df = data.getData(the_path.split('/')[-1])
    st.write(f'''## {the_path.split('/')[-1].title()}''')
    st.write('article - ' + str(df['article'].iloc[0].strftime("%d/%m/%Y")))
    if str(df['Description'].iloc[0]) != 'nan':
        st.write(str(df['Description'].iloc[0]))
    st.write('### Managed by')
    st.write(str(df['Managed by'].iloc[0]))
    st.write('### Data source')
    st.write(df[['Source', 'Table', 'Field']].style.hide(axis="index").to_html(), unsafe_allow_html=True)
    if str(df['Formula'].iloc[0]) != 'nan':
        st.write('### Formula')
        st.write(str(df['Formula'].iloc[0]))
st.divider()
st.success(f'last update: {last_update.strftime("%m/%d/%Y, %H:%M:%S")}')


