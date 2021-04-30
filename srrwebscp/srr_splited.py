import pandas as pd 


def merge_concat_df(df_srx_srr_drop, df_missed_recorver):

    '''this function receives two dfs. First, the second df (missed recover) will be merged with the first one to get all desired columns.
    After, both dfs will be concatenated. The function will return the concatenated df.'''

    df_merge = pd.merge(df_srx_srr_drop, df_missed_recorver, on='SRX').drop('SRR_x', 1)
    df_merge.rename(columns={'SRR_y':'SRR'}, inplace=True)
    
    df_plus_missed_concat = pd.concat([df_srx_srr_drop, df_merge])
    
    df_drop_na = df_plus_missed_concat.dropna().reset_index()
    df_drop_na = df_drop_na.drop('index', 1)

    return df_drop_na


def split_SRR(df_drop_na):

    '''This function receives a df where some samples (GSM) has more then one SRR. This function will split the SRR list and 
    create new rows with its respective GSM'''

    SRR_split_rows = pd.DataFrame(df_drop_na.SRR.str.split(',').tolist(), index=df_drop_na.GSM).stack()

    SRR_split_rows= SRR_split_rows.reset_index([0, 'GSM'])

    SRR_split_rows.columns = ['GSM', 'SRR']
    
    srr_split_final = SRR_split_rows[SRR_split_rows['SRR'].map(len) > 2] #we have 134 lines with just '1' and two with just '2' in the SRR column
    
    return srr_split_final


def srr_gsm_metadata(srr_split_final, df_drop_na):
    
    '''This function receives the splited srr_gsm file. It will return a df with the SRR per GSM (no splited) and the SRR count per GSM'''

    #creating SRR_count column
    SRR_split_rows_count = srr_split_final.groupby('GSM').count().reset_index() #ok
    SRR_split_rows_count = SRR_split_rows_count.rename(columns={'SRR':'SRR_Count'})

    #Creating the correct SRR (without 1 or 2 as strings) in a new df
    df = srr_split_final.groupby('GSM')['SRR'].apply(lambda x: "%s" % ','.join(x)).reset_index()
    
    df_merged = df_drop_na.merge(df, on='GSM').merge(SRR_split_rows_count, on='GSM')
    df_merged = df_merged.rename(columns = {'SRR_y':'SRR'}).drop('SRR_x', axis=1)
 
    return df_merged

    