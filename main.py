import pandas as pd 
import os.path
from os import path
import sys
import argparse
import logging
import numpy as np
import multiprocessing
from multiprocessing import  Pool
from utils.loggerinitializer import *
from distutils.dir_util import mkpath

from srrwebscp import retry_srr as rs
from srrwebscp import srr_splited as ss
from addtitles import gpl_gse_targets as gg


mkpath(os.getcwd() + "/logs/")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
initialize_logger(os.getcwd() + "/logs/", logger)


def read_csv(csv_file):

    '''open a csv file with header and returns a df'''

    df = pd.read_csv(csv_file)

    return df

def read_df_header(file_name, list_to_header:[]):

    '''open a csv file without header. In this case the df will be gsm_srx_srr generated by srx/srr webscrapper (csv).
    It will return a df'''

    df = pd.read_csv(file_name, names=list_to_header)
        
    return df

def read_tsv(file_name, list_to_header:[]):

    '''open a tsv file'''

    df = pd.read_csv(file_name, names=list_to_header, sep='\t')
        
    return df


def filter_Hs_chipseq(df):

    '''This funcion receives a df to filter the columns ORGANISM by Homo sapiens AND Library_strategy by chip-seq.
    The duplicated rowns will be dropped by GSM column. It will return a filtered df withoud duplicates.'''

    df_Hs_chipseq = df[(df['Organism'].str.contains('Homo sapiens', case=False, na=False)) & (df['Library_strategy'].str.contains('chip-seq', case=False, na=False))]
    df_Hs_chipseq_no_dup = df_Hs_chipseq.drop_duplicates(subset='GSM', keep='first')
    
    return df_Hs_chipseq, df_Hs_chipseq_no_dup


def drop_duplicates(df, col_dup):

    '''This function receives a df (in this case the srr/srx df) and remove the duplicates by one column. It will return a df without duplicates'''
    
    df_drop = df.copy()
    df_drop.drop_duplicates(subset=col_dup, keep=False, inplace=True)
    
    return df_drop  


def missed_srr(df_drop):

    '''This function reveices a df without duplicates and will return a list of SRX/SRP/DRX address for samples with no SRR/SRP/DRR 
    information. This list will be used to do a new webscrapper.'''

    df_no_SRR = df_drop[df_drop.isnull().any(axis=1)].reset_index()
    list_srx_address = df_no_SRR['Address'].tolist()

    return list_srx_address


def df_srx_srr_missed(SRR_srx_ncbi):

    '''This function receives a list of recovered missed srr sampels (from retry_wecscrp) and returns a df generated
    from this list'''

    header = ['SRX', 'SRR']
    df_1 = pd.DataFrame(SRR_srx_ncbi, columns=header)
    df_srx_srr = df_1.groupby('SRX')['SRR'].apply(lambda x: "%s" % ','.join(x)).reset_index()

    return df_srx_srr


def webscraper_missed(list_srx_address):

    logger.info("Starting web scraper of " + str(len(list_srx_address)))
        
    SRR_srx_ncbi = rs.srr_web_scrapping(list_srx_address) #Just do this step one time and save the df (246)
    logger.info("Web scraper succesfully done")
        
    df2 = df_srx_srr_missed(SRR_srx_ncbi)
    save_csv(df2, 'webscraper.csv')
        
    logger.info("Missed srr/srx dataframe created and saved as webscraper.csv")
        

def save_csv(df, name_out):
    
    '''receives a df and return a csv file'''

    df.to_csv(name_out, index=False)


def check_scraper_file():

    '''Check if webscraper.csv file exist. If the file does not exist, the program will stop'''

    if os.path.isfile('webscraper.csv'):
        return 0
    
    else:
        logger.error('Missing webscraper.csv file. Run the script with -w argument.')
        print('Error: You should run this script with the "-w" option to create the webscrapper.csv file')
        sys.exit(1)


def parallelize_df(df_ctl_IP, regex_comp, target_CL):
    
    logger.info('parallelizing df')
    num_cores = multiprocessing.cpu_count()
    df_split = np.array_split(df_ctl_IP, num_cores)

    func_param = [(i,regex_comp) for i in df_split]

    pool = Pool(num_cores)
    df = pd.concat(pool.starmap(target_CL, func_param))
    pool.close()
    pool.join()
    
    return df


def main():
    
    logger.info("############### STARTING " + sys.argv[0] + " ###############")
    print('Starting script')

    #first - loading master table from xml web scraper / generate the filtered tables
    logger.info("Loading master table from xml web scrapper")
    df_parser = read_csv(args.file) 
    df_Hs_chipseq, df_Hs_chipseq_no_dup = filter_Hs_chipseq(df_parser) 
    logger.info("Filtered dataframe (H. sapiens and ChIP-seq) without duplicates created. Length: " + str(len(df_Hs_chipseq_no_dup)) + " rows")

    #second - generate the missed gsm-srr list (list of address to do the web scrapper)
    logger.info("Loading the gsm/address/srr/srx dataframe and removing duplicates")
    df_srx_srr = read_df_header(args.srr, ['GSM', 'Address', 'SRX', 'SRR']) 
    df_srx_srr_drop = drop_duplicates(df_srx_srr, 'GSM')
    logger.info("Dataframe SRR/SRX without duplicates created. Length: " + str(len(df_srx_srr_drop)) + " rows")
    logger.info("Creating list of address of samples without SRR information")
    list_srx_address = missed_srr(df_srx_srr_drop) 
    logger.info("List created. Length: " + str(len(list_srx_address)))
    
    #web scraper
    if args.webscraper:
        webscraper_missed(list_srx_address)
        
    #third
    logger.info("Splitting SRR per sample step")
    check_scraper_file()
    df_missed_recorver = read_csv('webscraper.csv') # (158)
    df_drop_na = ss.merge_concat_df(df_srx_srr_drop, df_missed_recorver) #54886 gsm
    srr_split_final = ss.split_SRR(df_drop_na) #74490 #fixed bug about "1" and "2"
    save_csv(srr_split_final, 'log_srr_to_mamouth.csv') #saving file to mammouth 
    logger.info("Splitted GSM/SRR csv file saved. Length: " + str(len(srr_split_final)) + " rows")
    df_gsm_adr_srx_srr_final = ss.srr_gsm_metadata(srr_split_final, df_drop_na)
    save_csv(df_gsm_adr_srx_srr_final, 'log_gsm_adr_srx_srr_final.csv') #54886
    logger.info("gsm_adr_srx_srr csv file saved. Length: " + str(len(df_gsm_adr_srx_srr_final)) + " rows")
    
    #fourth - master final table including all informations 
    logger.info("Loading GPL and GSE title tsv files")
    df_gpl_title = read_tsv('xml_gpltitle_out.tsv', ['GPL', 'GPL_title'])
    df_gse_title = read_tsv('xml_gsetitle_out.tsv', ['GSE', 'GSE_title'])
    df_gse_gpl = gg.gpl_gse_title(df_Hs_chipseq_no_dup,df_gpl_title,df_gse_title )
    logger.info("GPL and GSE title columns added to master dataframe. Length: " + str(len(df_gse_gpl)) + " rows")
    logger.info("Creating new columns: Categories, Target and Confidence level (CL)")
    
    df_ctl_IP = gg.fill_na(df_gse_gpl) #just fill NA 
    
    dict_name = gg.load_dict(args.dict) #added to parallel

    regex_comp = gg.list_regex_values(dict_name) #added to parallel

    #df_almost = gg.columns_target_CL(df_ctl_IP, list_target, CL)
    df_almost = parallelize_df(df_ctl_IP, regex_comp, gg.target_CL)
    
    logger.info("Adjusting target and confidence level for INPUT samples")
    
    logger.info("Reordering columns")
    df_col_reorder = gg.reorder_cols(df_almost)
    logger.info("Saving whole metadata datafrane. Length: " + str(len(df_col_reorder)) + " rows")
    save_csv(df_col_reorder, 'all_metadata.csv' )
    logger.info("Adding the SRR/DRR/ERR count column")
    df_final = gg.add_srr_count_col(df_col_reorder, df_gsm_adr_srx_srr_final)
    save_csv(df_final, 'GEO_metadata_2021_'+str(len(df_final))+'.csv')
    logger.info("GEO Metadata saved")
    print('GEO metadata csv saved')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = 'A script to organize the GEO metadata scrapped by XML_scraper tool, including SRX, SRR, SRR_Count, GPL and GSE titles.'
    )

    parser.add_argument('-f', '--file', action='store',
                        help='The absolute path to the csv file with the metadata information obtained via XML webscraper script',
                        required=True)
    
    parser.add_argument('-s', '--srr', action='store',
                        help='The absolute path to the csv file with the metadata SRX address, SRX and SRR information obtained via SRX/SRR XML webscraper script',
                        required=True)
    
    parser.add_argument('-d', '--dict', action='store',
                        help='The absolute path to the csv file with the target regexs (JF file)',
                        required=True)

    parser.add_argument('-w', '--webscraper', default=False, action='store_true',
                        help='Argument to run the web scraper if you are running the code for the first time',
                        )


    args = parser.parse_args()
    main()