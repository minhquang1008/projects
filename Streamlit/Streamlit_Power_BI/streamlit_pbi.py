import streamlit as st

# st-emotion-cache
st.markdown('''
<style>
[data-testid="stAppViewContainer"] {
background-image: url('https://images4.alphacoders.com/600/600287.jpg');
background-size: cover;
background-repeat: no-repeat;
}
[data-testid='stHeader'] {
background-color: #FFFFFF;
opacity: 0.0;
background-repeat: no-repeat;
}
[class="block-container css-1y4p8pa ea3mdgi4"] {
margin-top: -50px;
margin-left: -750px;
background-repeat: no-repeat;
}
</style>
''', unsafe_allow_html=True)
st.markdown('''
<iframe title="DataMart_SS" width="1450" height="650" src="https://app.powerbi.com/reportEmbed?reportId=94422eb9-fb54-463d-b130-c234a15765ab&autoAuth=true&ctid=2d55064c-02ee-48f7-9f5f-f2b7915015b0" frameborder="0" allowFullScreen="true"></iframe>
''',  unsafe_allow_html=True)
