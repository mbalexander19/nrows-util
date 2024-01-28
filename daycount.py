import pandas as pd
import argparse

'''
NROWS Orders Analysis Tool
v0.1, January 2024
All rights belong to the U.S. Government.
POC: Github mbalexander19 (contact for official email)

Written in Python v3.12.1 with pandas v2.2.0. There is no guarantee of compatibility 
for prior or future versions.

Note: This code requires understaning of command line inputs to run. There is no GUI. 
'''


def date_range(df : pd.DataFrame, start : pd.Timestamp, end : pd.Timestamp) -> pd.DataFrame:
    '''
    Helper function. Truncates dates to given ranges and removes
    orders outside of given range.
    
    Inputs :
        df : 
            a pandas.DataFrame with (at minimum) 'Start Date' and 'End Date' columns
            formatted as pandas.Timestamp objects. nrows_parse.py includes this conversion.
        start :
            a pandas.Timestamp, the start date (date only, exact time is not used)
        end :
            a pandas.Timestamp, the end date (date only, exact time is not used)
    
    Output :
        a pandas.DataFrame with date ranges truncated to given start and end dates, orders
        outside of this window removed, and day counts calculated for each set of orders
        within the window
    '''
    # for calculation, set start date to be later of actual start or specified window start
    df['Start Date'] = df['Start Date'].apply(lambda x : max(start, x))
    # and set end date to be earlier of actual end or specified window end
    df['End Date'] = df['End Date'].apply(lambda x : min(end, x))

    # remove all rows outside of date bounds
    df = df.drop(df[(df['Start Date'] > df['End Date'])].index)
    
    df['Total Days'] = (df['End Date'] - df['Start Date']).dt.days + 1
    return df

'''
The below functions are all helpers for the aggregation method chosen. Most are simple
one-liners but are broken out separately for ease of updating and re-use in other code.
'''

def coarse_orders(df : pd.DataFrame) -> pd.DataFrame:
    order_map = {'AT' : 'AT', 'AD' : 'ADT', 'ID' : 'IDTT'}
    df['Order Type'] = df['Order Type'].str.slice(stop = 2).map(order_map)
    return df.groupby(['Order Type'])['Total Days'].sum()


def fine_orders(df : pd.DataFrame) -> pd.DataFrame:
    return df.groupby(['Order Type'])['Total Days'].sum()


def sailor_orders(df : pd.DataFrame) -> pd.DataFrame:
    return df.groupby(['Name', 'Order Type'])['Total Days'].sum()


def sailor_all(df : pd.DataFrame) -> pd.DataFrame:
    return df.groupby(['Name'])['Total Days'].sum()


def daycount(orders_tsv : str, start_date : str, end_date : str, type : str) -> pd.DataFrame:
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
            -'sailor_orders' aggregates by individual sailor with order types broken out
            -'sailor_total' aggregates by individual sailor with only a total daycount
            -'all' provides the sum of person-days on orders
            -'none' (or any other input) simply returns the input tsv with dates transformed to a 
                pandas datetime object
    
    Output :
        A pandas.DataFrame with orders count aggregation using the chosen method.
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
    
    orders = date_range(orders, start_dt, end_dt)
    
    if type == 'order_coarse':
        return coarse_orders(orders)
    elif type == 'order_fine':
        return fine_orders(orders)
    elif type == 'sailor_orders':
        return sailor_orders(orders)
    elif type == 'sailor_total':
        return sailor_all(orders)
    elif type == 'all':
        return orders['Total Days'].sum()
    else:
        return orders


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i', '--input', type = str, required = True, 
                        help = 'Input data file path in TSV format')
    parser.add_argument('-o', '--output', type = str, 
                        help = 'Desired output path in TSV format; required to save file')
    parser.add_argument('-w', '--write_mode', type = str, choices = ['a', 'w', 'x'], default = 'x',
                        help = 'Write mode for output file. See Python docs for definitions. \
                        Default "x", meaning this will not overwrite existing files.')
    parser.add_argument('-s', '--start_date', type = str, default = '19700101',
                        help = 'Start date for window in YYYYMMDD format, defaults to 19700101')
    parser.add_argument('-e', '--end_date', type = str, default = 'today',
                        help = 'End date for window in YYYYMMDD format, defaults to today')
    parser.add_argument('-t', '--type_aggregation', type = str, default = 'order_coarse',
                        choices = ['order_coarse', 'order_fine', 'sailor_orders', 'sailor_total',
                                   'all', 'none'], 
                        help = 'Defines how to aggregate counts')
    parser.add_argument('-d', '--display', action = 'store_true', help = 'Print output to console')
    
    args = parser.parse_args()
    
    out = daycount(args.input, args.start_date, args.end_date, args.type_aggregation, index = False)
    
    if args.output is not None:
        out.to_csv(args.output, sep = '\t', mode = args.write_mode)
    
    if args.display:
        print(out)