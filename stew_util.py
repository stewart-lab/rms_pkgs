import seaborn as sns
import matplotlib.pyplot as plt 
    
def make_box_plot(in_df, x, y, title, x_label, y_label, outboxfile):
    box = sns.boxplot(data=in_df, x=x, y=y)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(outboxfile)
    
# A function for creating a single heatmap
def create_heatmap(df_to_use, 
        out_path, 
        colormap,
        cluster_rows, 
        cluster_columns,
        keep_sd0,
        standardize,
        link,
        dist,
        title,
        suppress_row_dendrogram,
        suppress_col_dendrogram,
        height,
        width,
        title_fontsize,
        x_fontsize,
        y_fontsize):

    #height = 2 + 0.8 * df_to_use.shape[0]
    #print (height, "  df ", df_to_use.shape[0])
    #height = (2+0.2*len(rows_to_keep))  
    #print (height, " rows ", rows_to_keep) 
    #width = 10 
    # Set figure size
    figsize=(width, height)
    
    if standardize:        
        stand = 0      
    else:
        stand = None
    # Generate figure
    try: 
        cm = sns.clustermap(
            df_to_use, 
            row_cluster=cluster_rows, 
            col_cluster=cluster_columns, 
            cmap=colormap,
            standard_scale=stand,
            vmin=-3,   # -3
            vmax=3,  # 3
            dendrogram_ratio=(2/10, 2/height),
            figsize=figsize,
            xticklabels=1,
            yticklabels=1,
            metric=dist,
            method=link
            #cbar_pos=None
        )
        cm.ax_heatmap.set_ylabel('')
        print("title:", title)
        if title is not None:
            print ("title is true")
            cm.ax_heatmap.set_title(title, fontsize=title_fontsize)  # need to figure out how to put the title above the column dendrogram.  RMS.
        if (suppress_row_dendrogram):	
            cm.ax_row_dendrogram.set_visible(False) #suppress row dendrogram
        if (suppress_col_dendrogram):	
            cm.ax_col_dendrogram.set_visible(False) #suppress column dendrogram
        if x_fontsize is not None:
            cm.ax_heatmap.set_xticklabels(cm.ax_heatmap.get_xmajorticklabels(), fontsize = x_fontsize)
        #cm.ax_heatmap.set_yticklabels(cm.ax_heatmap.get_ymajorticklabels(), rotation = 0, fontsize = 18)
        if y_fontsize is not None:
            cm.ax_heatmap.set_yticklabels(cm.ax_heatmap.get_ymajorticklabels(), fontsize = y_fontsize)
    
        # Save the figure
        plt.tight_layout()
        plt.savefig(out_path, format='pdf')
        #plt.show()
    except BaseException as e:
        ex_type, ex_value, ex_traceback = sys.exc_info()
        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        print("Exception type : %s " % ex_type.__name__)
        print("Exception message : %s" %ex_value)
        print("Stack trace : %s" %stack_trace)
        print(e)
        if keep_sd0:
            print("Clustermap failed. Often this is because of divide by zero when keep_sd0 is set.")
        else:
            print ("Clustermap failed.")   
    
    return cm