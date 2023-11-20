import pandas as pd
from request import db_DWH_Base
import pickle
with open('returning_dictionary.pkl', 'rb') as file:
    returning_dictionary = pickle.load(file)

# df = pd.read_sql('''select top 100 * from W_BRANCH_D
# ''', db_DWH_Base)
# with open('Dim - Branch_sample.pkl', 'wb') as file:
#     pickle.dump(df, file)
#
# df = pd.read_sql('''select top 100 * from W_BROCKER_D
# ''', db_DWH_Base)
# with open('Dim - Brocker_sample.pkl', 'wb') as file:
#     pickle.dump(df, file)
#
# df = pd.read_sql('''select top 100 * from W_CUSTOMER_D
# ''', db_DWH_Base)
# with open('Dim - Customer_sample.pkl', 'wb') as file:
#     pickle.dump(df, file)
#
# df = pd.read_sql('''select top 100 * from W_CUSTOMER_D
# ''', db_DWH_Base)
# with open('Dim - Customer_sample.pkl', 'wb') as file:
#     pickle.dump(df, file)

