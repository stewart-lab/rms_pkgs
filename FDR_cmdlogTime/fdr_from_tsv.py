import pandas as pd
import numpy as np
import cmdlogtime
import os
from statsmodels.stats import multitest

COMMAND_LINE_DEF_FILE = "./fdr_from_tsv_commandLine.txt"
def main():
    (start_time_secs, pretty_start_time, my_args, addl_logfile)= cmdlogtime.begin(COMMAND_LINE_DEF_FILE)   
    outdir  = my_args["out_dir"]
    in_f = my_args["infile"]
    genes_to_keep_f = my_args["genes_to_keep_for_fdr"]
    output_file_prefix = my_args["output_file_prefix"]
    
    df = pd.read_csv(in_f, sep='\t', index_col=0)
    print('Shape of data before any filtering: ', df.shape)

    if (output_file_prefix.endswith("ALLZZZ")):
        out_file = os.path.join(outdir, "fdrs.tsv")
    else:
        out_file = os.path.join(outdir, output_file_prefix + "_fdrs.tsv")  
        
    if (genes_to_keep_f.endswith("ALLZZZ")):
        df_genes = df
    else:
        df_genes = pd.read_csv(genes_to_keep_f, sep='\t', index_col=0) #header=None)
    print('shape of df_genes:', df_genes.shape)
    genes_to_keep = set()
    genes_to_keep = (set(df.index) & set(df_genes.index))
    df_to_use = df.loc[genes_to_keep]
    print('Shape of df_to_use after filtering genes: ', df_to_use.shape)
    
    df_to_use['fdr'] = multitest.multipletests(df_to_use['pval'].to_numpy(), method='fdr_bh')[1]
    df_to_use = df_to_use.sort_index(ascending=True)
    df_to_use.to_csv(out_file, sep='\t')    
    
    cmdlogtime.end(addl_logfile, start_time_secs) 

#   ---------------------------------------- FUNCTIONS -------------------------

if __name__ == "__main__":
    main()
