import pandas as pd
import datetime
import argparse

'''
NROWS Daycounter
v0.1, 27 January 2024
All rights belong to the U.S. Government.
POC: Github mbalexander19

Written in Python v3.12.1 with pandas v2.2.0. There is no guarantee of compatibility for prior or future versions.

Note: This code requires knowledge of command line inputs. 
'''
def date_range(df, start, end):
    # for calculation, set start date to be later of actual start or specified window start
    df['Start Date'] = df['Start Date'].apply(lambda x : max(start, x))
    # and set end date to be earlier of actual end or specified window end
    df['End Date'] = df['End Date'].apply(lambda x : min(end, x))

    # remove all rows outside of date bounds
    df = df.drop(df[(df['Start Date'] > df['End Date'])].index)
    
    df['Total Days'] = (df['End Date'] - df['Start Date']).dt.days + 1
    return df

def coarse_orders(df, start, end):
    order_map = {'AT' : 'AT', 'AD' : 'ADT', 'ID' : 'IDTT'}
    df['Order Type'] = df['Order Type'].str.slice(stop = 2).map(order_map)
    df = date_range(df, start, end)
    counts = df.groupby(df['Order Type'])['Total Days'].sum()
    return counts

def daycount(orders_tsv, output_path = 'daycount.csv', start_date = None, end_date = None, type = 'order_coarse'):
    '''
    Input
    orders_tsv :
        a str, file path to NROWS orders data in tab-separated value format
            format matches NROWS output table with some cleaning (provided in nrows_parse.py)
    start_date :
        a str, the start date of the orders window in the format "YYYYMMDD" (no slashes or dashes).
        If not given, set to 01 Jan 1970.
    end_data :
        a str, the end date of the orders window in the format "YYYYMMDD" (no slashes or dashes). 
        If not given, defaults to today.
    type :
        a str, defines how to aggregate data
            -'order_coarse' aggregates by high-level order type (AT, ADT, IDTT)
            -'order_fine' aggregates by detailed order type (AT-AT, AT-SC, ADT-SCRE, ADT-REIM, etc.)
            -'sailor' aggregates by individual sailor
            -'all' provides the sum of person-days on orders
            -'none' (or any other input) simply returns the input tsv with dates transformed to a 
                pandas datetime object
    
    Output :
        A csv with orders count aggregation using the chosen method.
    '''
    
    if start_date is not None:
        start_dt = pd.to_datetime(start_date, format = "%Y%m%d")
    else:
        start_dt = pd.to_datetime('19700101', format = "%Y%m%d")
    
    if end_date is not None:
        end_dt = pd.to_datetime(end_date, format = "%Y%m%d")
    else:
        end_dt = pd.to_datetime('today')
    
    orders = pd.read_csv(orders_tsv, sep = '\t', header = 0, index_col = False)
    orders['Start Date'] = pd.to_datetime(orders['Start Date'], format = "%Y/%m/%d")
    orders['End Date'] = pd.to_datetime(orders['End Date'], format = "%Y/%m/%d")
    
    if type not in ['order_coarse', 'order_fine', 'sailor', 'all']:
        return orders
    elif type == 'order_coarse':
        out_df = coarse_orders(orders, start_dt, end_dt)
    
    #print(orders['Start Date'] < start_dt)

if __name__ == '__main__':
    daycount('nrows_data.csv', start_date='20240101', end_date = '20240131')