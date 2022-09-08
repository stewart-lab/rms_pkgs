import seaborn as sns; sns.set_theme(color_codes=True)
import sys
import traceback
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import zscore
import cmdlogtime
import stew_util as su
import os
import conorm

COMMAND_LINE_DEF_FILE = "./heatmap_from_tsv2_commandLine.txt"
def main():
    (start_time_secs, pretty_start_time, my_args, addl_logfile)= cmdlogtime.begin(COMMAND_LINE_DEF_FILE)   
    out_pdf = os.path.join(my_args["out_dir"], "heatmap.pdf")
    
    df = read_infile(my_args["infile"])
    
    df = filter_cols(my_args["cols_to_keep_for_heatmap"], df)
    
    df  = filter_rows_with_all_zeros(df)
    df, rows_to_keep = specify_rows_to_keep(my_args["rows_to_keep_for_heatmap"], df)
    # need rows_to_keep later, as this will be used to filter the dataframe AFTER further zscore stddev0 filtering
    
    df = maybe_take_log2(my_args["log2"], df)
    
    df = maybe_norm(my_args['median_ratio_norm'], df)    
    
    df = maybe_standardize(my_args["standardize_rows"], my_args["keep_standarddev_zero"], df)
    
    df = maybe_compute_zscores(my_args["use_raw_values"], my_args["standardize_rows"], df)
     
    df = filter_rows (rows_to_keep, df) 
    
    
    
    # Set height based on number of genes. Set width to 10.  RMS. seems problematic
    height = (2+0.2*len(rows_to_keep))  
    width  = 10  
    
    su.create_heatmap(
        df, 
        out_pdf,
        my_args["colormap"],
        my_args["cluster_row_data"],
        my_args["cluster_column_data"],
        my_args["keep_standarddev_zero"],
        my_args["standardize_rows"],
        my_args["linkage_method"],
        my_args["distance_metric"],
        my_args["title_for_heatmap"],
        my_args["suppress_row_dendrogram"] ,
        my_args["suppress_col_dendrogram"] ,
        height,
        width,
        my_args["title_fontsize"],
        my_args["x_fontsize"],
        my_args["y_fontsize"]
    )
    cmdlogtime.end(addl_logfile, start_time_secs) 

# ----------------------------------- FUNCTIONS  -------------------------------------
def read_infile(infile):
    df = pd.read_csv(infile, sep='\t', index_col=0)
    print('Shape of data before any filtering: ', df.shape)
    print(df)
    return df

def filter_cols(cols_to_keep_file, df):
    if (cols_to_keep_file.endswith("ALLZZZ")):
        df_cols = pd.DataFrame()
    else:
        df_cols = pd.read_csv(cols_to_keep_file, sep='\t', index_col=0, header=None)
    print('Shape of columns: ', df_cols.shape)
    # Filter to keep only columns we want to plot
    if (not  df_cols.shape == (0,0)):
        df = df[df_cols.index]  
    print('Shape of data after filtering columns: ', df.shape)    
    return df

def filter_rows_with_all_zeros(df): 
    at_least_one_non_zero = np.sum(np.array(df), axis=1) != 0  
    df = df.loc[at_least_one_non_zero]
    print('Shape of data after filtering out all zeros: ', df.shape)
    return df
    
def specify_rows_to_keep(rows_to_keep, df): 
    if (rows_to_keep.endswith("ALLZZZ")):
        df_rows = df
    else:
        df_rows = pd.read_csv(rows_to_keep, sep='\t', index_col=0, header=None)
    print('shape of df_rows:', df_rows.shape)
    
    rows_to_keep = set()
    rows_to_keep = (set(df.index) & set(df_rows.index)) 
    return df, rows_to_keep    
    
def maybe_take_log2(log2, df):
    if log2:
        # take log2(val + 1)
        df = pd.DataFrame(
            data=np.log(np.array(df)+1),
            index=df.index,
            columns=df.columns
        )
    return df
def maybe_norm(norm, df):
    if norm:
        df = conorm.mrn(df)
    return df
                   
def maybe_standardize(standardize_rows, keep_standarddev_zero, df):
    if keep_standarddev_zero:
        if standardize_rows:
            std_is_zero = np.std(np.array(df), axis=1) == 0
            if (std_is_zero.any()):
                print("Note that keeping the ones with standard deviation of zero and choosing to standardize WILL lead to divide by zero errors for this dataset!!!!")
            print("Note that keeping the ones with standard deviation of zero and choosing to standardize can lead to divide by zero errors!!!!")
    else:    
        # Filter to only keep genes with std deviation != 0
        std_not_zero = np.std(np.array(df), axis=1) != 0
        df = df.loc[std_not_zero]
        print('Shape of data after filtering stddev0: ', df.shape)
    return df

def maybe_compute_zscores(use_raw_values, standardize_rows, df):
    if (use_raw_values  or standardize_rows):
        df_to_use = df  
    else:  
        # Compute Z-scores row-wise (i.e. for each gene)
        #X_zscore = df_input.apply(my_zscore, axis=1).to_list()  #rms see note on my_zscore()      
        X_zscore = zscore(np.array(df), axis=1)
        
        # Note. May need way to do a different non-traditional z-score calculation.
        # The code below is for the traditional z score calculation
        df_zscore = pd.DataFrame(
            data=X_zscore,
            index=df.index,
            columns=df.columns
        ) 
        df_to_use = df_zscore.replace(np.nan, 0)  
        #df_to_use = df_zscore  # rms, this is what we would do if we fix the my_zscore() function       
    return df_to_use

def filter_rows (rows_to_keep, df):    
    # Filter the data for the rows of interest
    rows_to_keep = rows_to_keep & set(df.index)
    print("length rows to keep after all filtering:", len(rows_to_keep))
    df = df.loc[rows_to_keep]
    print('Shape of df_to_use after filtering rows: ', df.shape)
    print(df)    
    return df
#def my_zscore(row):
# RMS NOTE:  keeping this here as an example of apply.
# RMS NOTE:  This won't work in that we will never hit the exception, as zscore returns nan
#            if stddev is zero.  So, we'd have to do something fancy in the function to 
#            replace the Nans with zeros.
#            so doing it with relpace(np.nan, 0) as above in the create_heatmap function is
#            what we will do for now.
#    try:
#        return zscore(np.array(row))  
#    except ZeroDivisionError:
#        return np.zeros(row.shape)
#    
      
if __name__ == "__main__":
    main()
