import pandas as pd

df=pd.read_excel("McAfee_Raw_Events_edit_002.xlsx")

df.replace(to_replace=r'\w{4}\_\w{2}\=\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
           value='dest_ip= 123.45.67.891', regex=True)

