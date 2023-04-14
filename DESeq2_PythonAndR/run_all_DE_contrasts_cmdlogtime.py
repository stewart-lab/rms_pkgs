import itertools
import os
import pandas as pd
import cmdlogtime

# get command line arguments
COMMAND_LINE_DEF_FILE = "./runDeseq2ContrastsCommandLine.txt"
def main():
    (start_time_secs, pretty_start_time, my_args, addl_logfile) = cmdlogtime.begin(COMMAND_LINE_DEF_FILE)
    wd = my_args["wd"]
    expr_file = my_args["expr_file"]
    metadata_file = my_args["metadata"]
    ctrl = my_args["control"]
    ctrlfile = my_args["control_file"]
    batch = my_args["batch"]
    addl_logfile.write("Starting run_all_DE_constrasts with runDeseq2\n")

    # get metadata file with sample types
    df= pd.read_csv(metadata_file, sep="\t")
    print(df)
    typelist= df.iloc[:,1].values.tolist()
    typelist= list(set(typelist))
    print(typelist)
    # get all combinations of sample types
    tup= list(itertools.combinations(typelist, 2))
    print(tup)
    # get dictionary with samples IDs for each group
    if batch == False:
        df2 = df[['Group', 'ID']].copy()
        sample_dict=df2.groupby('Group').apply(lambda dfg: dfg.drop('Group', axis=1).to_dict(orient='list')).to_dict()
        print(sample_dict)
    else:
        df2 = df[['Group', 'ID', 'Batch']].copy()
        sample_dict=df2.groupby('Group').apply(lambda dfg: dfg.drop('Group', axis=1).to_dict(orient='list')).to_dict()
        print(sample_dict)
    # writing meta files function
    def make_metafiles(tup1,tup2,sample_dict,oup,batch):
        if batch == False:
            oup.write("Sample\tCType\n")
            if tup1 in sample_dict.keys():
                data1= sample_dict[tup1]
                for d in data1['ID']:
                    oup.write("%s\t%s\n" % (d,tup1))
            if tup2 in sample_dict.keys():
                data2= sample_dict[tup2]
                for d in data2['ID']:
                    oup.write("%s\t%s\n" % (d,tup2))
        else:
            oup.write("Sample\tCType\tBatch\n")
            if tup1 in sample_dict.keys():
                data1= sample_dict[tup1]
                for d in data1['ID']:
                    i= data1['ID'].index(d)
                    oup.write("%s\t%s\t%s\n" % (d,tup1,data1['Batch'][i]))
            if tup2 in sample_dict.keys():
                data2= sample_dict[tup2]
                for d in data2['ID']:
                    i= data2['ID'].index(d)
                    oup.write("%s\t%s\t%s\n" % (d,tup2,data2['Batch'][i]))        
    # reverse tuple function
    def Reverse(tuples):
        new_tup = tuples[::-1]
        return new_tup
    #expression file with count data
    counts= expr_file
    # get all combinations and write contrast files
    # loop through tuples, ask if control sample or not
    # also write output directories
    # then run runDeseq2.py for each contrast
    for i in tup:
        if ctrl != None: # check for control
            if i[0] == ctrl:
                outfile= wd+"/metadata_"+str(i[0])+"vs"+str(i[1])+".txt"
                oup= open(outfile,"w")
                make_metafiles(i[0],i[1],sample_dict,oup,batch)
                oup.close()
                directory= str(i[0])+"vs"+str(i[1])
                path = os.path.join(wd, directory)
                os.mkdir(path)
                if batch == False:
                    os.system("python runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[1]), str(i[0])))
                else:
                    os.system("python runDeseq2.py {} {} {} CType Batch+CType {} {} -f CType:CType,Batch:Batch".format(path, counts, outfile, str(i[1]), str(i[0])))
            else:
                if i[1] == ctrl:
                    outfile= wd+"/metadata_"+str(i[1])+"vs"+str(i[0])+".txt"
                    oup= open(outfile,"w")
                    make_metafiles(i[1],i[0],sample_dict,oup,batch)
                    oup.close()
                    directory= str(i[1])+"vs"+str(i[0])
                    path = os.path.join(wd, directory)
                    os.mkdir(path)
                    if batch == False:
                        os.system("python runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[0]), str(i[1])))
                    else:
                        os.system("python runDeseq2.py {} {} {} CType Batch+CType {} {} -f CType:CType,Batch:Batch".format(path, counts, outfile, str(i[0]), str(i[1])))
                else:
                    pass
        if ctrlfile != None: # check for control file
            df3= pd.read_csv(ctrlfile, sep="\t")
            records = df3.to_records(index=False)
            result = list(records)
            for r in result:
                # check if this pair is in your pair file
                    print(r,i)
                    if tuple(i) == tuple(r):
                        outfile= wd+"/metadata_"+str(i[0])+"vs"+str(i[1])+".txt"
                        oup= open(outfile,"w")
                        make_metafiles(i[0],i[1],sample_dict,oup,batch)
                        oup.close()
                        directory= str(i[0])+"vs"+str(i[1])
                        path = os.path.join(wd, directory)
                        os.mkdir(path)
                        if batch == False:
                            os.system("python runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[1]), str(i[0])))
                        else:
                            os.system("python runDeseq2.py {} {} {} CType Batch+CType {} {} -f CType:CType,Batch:Batch".format(path, counts, outfile, str(i[1]), str(i[0])))
                    # check if reverse pair is in pair file
                    elif tuple(Reverse(i)) == tuple(r):
                        outfile= wd+"/metadata_"+str(i[1])+"vs"+str(i[0])+".txt"
                        oup= open(outfile,"w")
                        make_metafiles(i[1],i[0],sample_dict,oup,batch)
                        oup.close()
                        directory= str(i[1])+"vs"+str(i[0])
                        path = os.path.join(wd, directory)
                        os.mkdir(path)
                        if batch == False:
                            os.system("python runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[0]), str(i[1])))
                        else:
                            os.system("python runDeseq2.py {} {} {} CType Batch+CType {} {} -f CType:CType,Batch:Batch".format(path, counts, outfile, str(i[0]), str(i[1])))
        else: # if no controls then do all pairs
            outfile= wd+"/metadata_"+str(i[0])+"vs"+str(i[1])+".txt"
            oup= open(outfile,"w")
            make_metafiles(i[0],i[1],sample_dict,oup,batch)
            oup.close()
            directory= str(i[0])+"vs"+str(i[1])
            path = os.path.join(wd, directory)
            os.mkdir(path)
            if batch == False:
                os.system("python runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[1]), str(i[0])))
            else:
                os.system("python runDeseq2.py {} {} {} CType Batch+CType {} {} -f CType:CType,Batch:Batch".format(path, counts, outfile, str(i[1]), str(i[0])))
    cmdlogtime.end(addl_logfile, start_time_secs)
	
if __name__ == "__main__":
    main()