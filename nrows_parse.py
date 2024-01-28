import pandas as pd
import argparse
import os

'''
NROWS Orders Analysis Tool
v0.1, January 2024
All rights belong to the U.S. Government.
POC: Github mbalexander19 (contact for official email)

Written in Python v3.12.1 with pandas v2.2.0. There is no guarantee of compatibility 
for prior or future versions.

Note: This code requires understaning of command line inputs to run. There is no GUI. 
'''


def parse_to_tsv(file_path : str, output_path : str = 'nrows_data.csv', 
                 write_mode : str = 'a', include_cancelled : bool = False) -> None:
    '''
    Input
    path : 
        a str, the path of the saved NROWS HTML page
    output_path : 
        a str, the file path of the csv output; nrows_data.csv by default
    write_mode : 
        a str from 'a', 'w', or 'x'. 'a' appends to an existing file if it exists (otherwise creates
        a new file), 'w' creates a new file and overwrites any existing data, 'x' creates a new file
        only if a file does not already exist and fails otherwise. 'a' by default.
    include_cancelled : 
        a bool, False by default, whether or not to include cancelled orders
    
    Output
        NROWS orders data in tab-separated value form saved to location in output_path.
        Returns nothing.
    '''
    
    orders_table = pd.read_html(file_path)[5]
    orders_table = orders_table.drop(0, axis = 1) # remove blank column on left side of table
    names = orders_table.loc[1] # row 1 contains column headers
    orders_table = orders_table.drop([0,1], axis = 0) # remove blank row 0 and headers
    orders_table.columns = names # set column names

    # remove cancelled orders if desired
    if not include_cancelled:
        orders_table = orders_table.loc[orders_table['Status'] != 'CANCEL']
    
    if write_mode == 'a':
        write_header = not(os.path.exists(output_path))
    else:
        write_header = True
    
    # write to tab-separate values
    orders_table.to_csv(output_path, sep = '\t', mode = write_mode, index = False, header = write_header)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i', '--input_path', type = str, default = 'data/nrows_data.html')
    parser.add_argument('-o', '--output_path', type = str, default = 'nrows_data.csv')
    parser.add_argument('-wm', '--write_mode', type = str, default = 'a')
    parser.add_argument('-canc', '--include_cancelled', action = 'store_true', default = False)
    
    args = parser.parse_args()
    
    parse_to_tsv(args.input_path, args.output_path, args.write_mode, args.include_cancelled)