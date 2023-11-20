import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
from datetime import datetime
import re
import pickle

# 1. Read data
st.title("Data Science Project")
st.write("## Customer segmentation")
uploaded_file_1 = st.file_uploader("Choose file", type=['txt','csv'])
flag = 0
if uploaded_file_1 is not None:
    df = pd.read_csv(uploaded_file_1, header = None)
    flag = 1
    st.write("###### Uploaded is in use")
else:
    df = pd.read_csv('CDNOW_master.txt', header = None)
df[0] = df[0].apply(lambda x: re.sub("\s{2,}"," ", x.strip()))
df = df[0].str.split(' ', expand=True)
df.columns =['customer_id', 'date', 'quantity', 'gross_sales']
# 2. xử lý dữ liệu ra dataframe RFM
string_to_date = lambda x : datetime.strptime(x, "%Y%m%d").date()
df['date'] = df['date'].apply(string_to_date)
df['date'] = df['date'].astype('datetime64[ns]')
df['quantity'] = df['quantity'].astype('int')
df['gross_sales'] = df['gross_sales'].astype('float')
df['order_id'] = [i for i in range(1, len(df) + 1)]
df = df.dropna()
max_date = df['date'].max().date()
Recency = lambda x : (max_date - x.max().date()).days
Frequency  = lambda x: len(x.unique())
Monetary = lambda x : round(sum(x), 2)
df_RFM = df.groupby('customer_id').agg({'date': Recency,
                                        'order_id': Frequency,
                                        'gross_sales': Monetary })
df_RFM.columns=['Recency', 'Frequency', 'Monetary']
df_RFM = df_RFM.sort_values('Monetary',ascending = False)
df_now = df_RFM[['Recency','Frequency','Monetary']]
# 3. scale dữ liệu
from sklearn.preprocessing import MinMaxScaler
mmScaler = MinMaxScaler()
mmScaler.fit(df_now)
data_sub = mmScaler.transform(df_now)
# 4. chạy model
from sklearn.cluster import AgglomerativeClustering
if flag == 1:
    cluster = AgglomerativeClustering(n_clusters = 4,
    affinity='euclidean',
    linkage='ward')
    cluster.fit(data_sub)
else:
    pkl_filename = "cluster.pkl"  
    with open(pkl_filename, 'rb') as file:  
        cluster = pickle.load(file)
# 5. clustering
df_now["Cluster"] = cluster.labels_
df_now['Rank'] = ['Regular customers' if i == 0 else 'Gold customers' if i == 1 else 'Potential customers' if i == 2 else 'Silver customers' for i in df_now["Cluster"]]
df_now.groupby('Cluster').agg({
    'Recency':'mean',
    'Frequency':'mean',
    'Monetary':['mean', 'count']}).round(2)
rfm_agg2 = df_now.groupby('Cluster').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': ['mean', 'count']}).round(0)
rfm_agg2.columns = rfm_agg2.columns.droplevel()
rfm_agg2.columns = ['RecencyMean','FrequencyMean','MonetaryMean', 'Count']
rfm_agg2['Percent'] = round((rfm_agg2['Count']/rfm_agg2.Count.sum())*100, 2)
rfm_agg2 = rfm_agg2.reset_index()
rfm_agg2['Cluster'] = 'Cluster '+ rfm_agg2['Cluster'].astype('str')
rfm_agg2['Rank'] = ['Regular customers', 'Gold customers', 'Potential customers', 'Silver customers']
rfm_agg2['Cluster'] = rfm_agg2['Cluster'] + ' ' + rfm_agg2['Rank']
# 6. ploting
# tree plot
cluster_fig = plt.gcf()
ax = cluster_fig.add_subplot()
cluster_fig.set_size_inches(14, 10)
colors_dict2 = {'Regular customers':'yellow','Gold customers':'green', 'Potential customers':'cyan', 'Silver customers':'purple'}
squarify.plot(sizes=rfm_agg2['Count'],
              text_kwargs={'fontsize':12,'weight':'bold', 'fontname':"sans serif"},
              color=colors_dict2.values(),
              label=['{} \n{:.0f} days \n{:.0f} orders \n{:.0f} $ \n{:.0f} customers ({}%)'.format(*rfm_agg2.iloc[i])
                      for i in range(0, len(rfm_agg2))], alpha=0.5 )
plt.title("Customers Segments",fontsize=26,fontweight="bold")
plt.axis('off')
# scatter plot
import plotly.express as px
scatter_fig = px.scatter(rfm_agg2, x="RecencyMean", y="MonetaryMean", size="FrequencyMean", color="Cluster",
           hover_name="Cluster", size_max=100)
# 3d plot
threedee = plt.figure(figsize=(12,10))
ax = threedee.add_subplot(projection='3d')
ax.scatter(df_now['Recency'], df_now['Frequency'], df_now['Monetary'],
c=df_now["Cluster"])
ax.set_xlabel('Recency')
ax.set_ylabel('Frequency')
ax.set_zlabel('Monetary')

# GUI
menu = ["Business Objective", "Build Project", "Prediction"]
choice = st.sidebar.selectbox('Menu', menu)
if choice == 'Business Objective':    
    st.subheader("Business Objective")
    st.write("""
    ###### Customer segmentation is a unique strategy that can help to find your target audience, improve client retention, and overall improve your number of clients and sources of revenue.
    """)  
    st.write("""###### => Problem/ Requirement: Use Machine Learning algorithms in Python for customer segmentation.""")
    st.image("customer_segmentation.jpg")

elif choice == 'Build Project':
    st.subheader("Build Project")
    st.write("##### 1. Some data")
    st.dataframe(df_RFM.head(10))
    st.dataframe(df_RFM.tail(10))  
    st.write("##### 2. Visualize the distribution")
    distribution_fig = plt.figure(figsize=(8,10))
    plt.subplot(3, 1, 1)
    sns.distplot(df_RFM['Recency'], color='green')# Plot distribution of R
    plt.subplot(3, 1, 2)
    sns.distplot(df_RFM['Frequency'], color='green')# Plot distribution of F
    plt.subplot(3, 1, 3)
    sns.distplot(df_RFM['Monetary'], color='green') # Plot distribution of M
    st.pyplot(distribution_fig.figure)
    st.write("##### 3. Build Hierarchical Clustering model")
    if flag == 0:
        st.image("dendograms.png")
    st.write("##### 4. Evaluation")
    st.write("###### The four clusters:")
    st.dataframe(rfm_agg2)
    st.write("###### Tree map:")
    cluster_fig.figure
    st.write("###### Scatter plot:")
    scatter_fig
    st.write("###### 3D scatter plot:")
    ax.figure
elif choice == 'Prediction':
    st.subheader("Input ID")
    input = st.text_input('Customer ID')
    clicked = st.button("Search")
    if input and clicked:
        st.dataframe(df_now[['Rank','Recency','Frequency','Monetary']].loc[input])



    


