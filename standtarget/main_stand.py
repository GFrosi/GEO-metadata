import pandas as pd 
import re
import sys
import argparse
from tqdm import tqdm


def read_csv(file_name):
    '''Returns a dataframe'''
    
    return pd.read_csv(file_name) 


def create_list(df, col_name: str):
    '''Receives a dataframe and a column name.
    Returns a list.'''
    
    return df[col_name].to_list()


def create_dict_regex(dict_regex_file):
    '''Receives a csv file with targets and regex.
    Returns a dict with the targets as keys and the
    compiled regex as values'''
    
    dict_target = {}
    file_n = open(dict_regex_file, 'r')

    for line in file_n:

        line = line.strip() 
        target,expr = line.split(',')
        regex = re.compile(expr,re.IGNORECASE)
        dict_target[target] = regex

    return dict_target


def stand_target(list_target: list, dict_regex: dict):
    '''Receives a list and dictionary with regex as values.
    Returns a dictonary and a list.'''
    
    dict_stand = {}
    list_stand = []

    for tgt in tqdm(list_target):
        
        if 'GSM' in tgt:

            dict_stand[tgt] = 'None'
            list_stand.append('None')

        for k,v in dict_regex.items():
            
            match = re.search(v, tgt)

            if match is not None:

                dict_stand[match.group()] = k
                list_stand.append(k)
                break
    
    return dict_stand, list_stand


def add_col(df, list_stand: list):
    '''Receives a df and a list. Returns 
    a re-ordered df including the new column.
    '''
    
    df1 = df.copy()
    df1['Target-GEO'] = list_stand

    
    #categories column removed
    col = ['Release-date', 'Library-strategy', 'Organism', 'GPL', 'GPL-title',
       'GSE', 'GSE-title', 'GSM', 'GSM_title', 'Cell', 'Disease', 'Sex_GEO',
       'Source', 'ChIP-antibody-catalog', 'Target', 'Target-interest',
       'Target-target', 'Target-catalog', 'Target-GEO' ,'CL-target', 'Address', 'SRX', 'SRR',
       'SRR_Count'
       ]
    
    df1 = df1[col]
    
    return df1


def save_csv(df, name_out):
    '''receives a df and return a csv file'''

    df.to_csv(name_out, index=False)


def main():

    print('Starting script')
    df = read_csv(args.file)
    # print(df.head())
    list_tgt = create_list(df, 'Target-interest')
    dict_target = create_dict_regex(args.dict)
    # print(dict_target)
    print('Generating list of stand targets')
    dict_stand, list_stand = stand_target(list_tgt, dict_target)
    print('list generated: ', len(list_stand), 'items')
    print('adding Target-GEO column to the dataframe')
    df1 = add_col(df, list_stand)
    # print(df1.head())
    print('Column added, DONE')
    save_csv(df1, args.output)

if __name__ == "__main__":


    parser = argparse.ArgumentParser(
        description = 'A script to generate a standardized Target column from the GEO-Metadata csv file.'
    )

    parser.add_argument('-f', '--file', action='store',
                        help='The absolute path to the csv file with the metadata information obtained via GEO-Metadata tool',
                        required=True)
    
    
    parser.add_argument('-d', '--dict', action='store',
                        help='The absolute path to the csv file with the target regexs',
                        required=True)

    parser.add_argument('-o', '--output', action='store',
                        help='The absolute path to save the final GEO dataframe including the Target-GEO column',
                        required=True)

    args = parser.parse_args()
    main()