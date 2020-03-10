import pandas as pd

## Read in the excel with raw event logs

df=pd.read_excel("McAfee_Raw_Events_edit_003.xlsx")

## Replace the dest_ip field using regex

df=df.replace(to_replace=r'\w{4}\_\w{2}\=.\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.',
           value='dest_ip= 923.45.67.891', regex=True)

## Replace the src_ip field using regex

df=df.replace(to_replace=r'\w{3}\_\w{2}\=.\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.',
           value='src_ip= 923.45.67.891', regex=True)

## Replace the user="<number>" using regex"

df=df.replace(to_replace=r'\w{4}\=\"\d{5,7}\"',
           value='user= 8675309', regex=True)

## Replace the numerics with same count as an ID with user=<number>

df=df.replace(to_replace=r'\s*\d{5,7}',
              value='8675309', regex=True)
## Fixes multi user issue

df=df.replace(to_replace=r'\w{4}\=\"\d{5,7}\,\d{5,7}\,\d{5,7}\"',
           value='user= 8675309', regex=True)

## Saves what you did. 

df.to_excel("McAfee_Raw_Events_edit_003.xlsx", index=False, header=False)
