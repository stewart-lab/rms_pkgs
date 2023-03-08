import itertools
import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Run DEseq on mulitple contrasts')
parser.add_argument('filename', help='metadata file with ID (sample replicate names) and Group (type of sample, ie. control)')
parser.add_argument('wd', help='working directory where metadata files should go')
parser.add_argument('expr_file', help= 'file with expression count data')
parser.add_argument('-ctrl', help='option to include one control for contrasts', default='NA')
parser.add_argument('-ctrlfile', help='option to include multiple controls for contrasts, file with control\tsample pairs', default='NA')
args = parser.parse_args()
print(args.filename)
df= pd.read_csv(args.wd+args.filename, sep="\t")
print(df)
typelist= df.iloc[:,1].values.tolist()
print(typelist)
typelist= list(set(typelist))
print(typelist)
# get all combinations
tup= list(itertools.combinations(typelist, 2))
print(tup)
# get dictionary with samples
df2 = df[['Group', 'ID']].copy()
sample_dict=df2.groupby('Group').apply(lambda dfg: dfg.drop('Group', axis=1).to_dict(orient='list')).to_dict()
print(sample_dict)
# writing meta files function
def make_metafiles(tup1,tup2,sample_dict,oup):
    oup.write("Sample\tCType\n")
    if tup1 in sample_dict.keys():
        data1= sample_dict[tup1]
        for d in data1['ID']:
            oup.write("%s\t%s\n" % (d,tup1))
    if tup2 in sample_dict.keys():
        data2= sample_dict[tup2]
        for d in data2['ID']:
            oup.write("%s\t%s\n" % (d,tup2))
# reverse tuple function
def Reverse(tuples):
    new_tup = tuples[::-1]
    return new_tup
#expression file
counts= args.wd+args.expr_file
# get all combinations and write contrast files
# loop through tuples, ask if control sample or not
# also write output directories
# then run runDeseq2.py for each contrast
for i in tup:
    if args.ctrl=='NA' and args.ctrlfile=='NA':
        outfile= args.wd+"/metadata_"+str(i[0])+"vs"+str(i[1])+".txt"
        oup= open(outfile,"w")
        make_metafiles(i[0],i[1],sample_dict,oup)
        oup.close()
        directory= str(i[0])+"vs"+str(i[1])
        path = os.path.join(args.wd, directory)
        os.mkdir(path)
        os.system("python3 runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[0]), str(i[1])))
    else:
        if args.ctrlfile=='NA':
            ctrl_list= args.ctrl.split(",")
            if i[0] in ctrl_list:
                outfile= args.wd+"/metadata_"+str(i[0])+"vs"+str(i[1])+".txt"
                oup= open(outfile,"w")
                make_metafiles(i[0],i[1],sample_dict,oup)
                oup.close()
                directory= str(i[0])+"vs"+str(i[1])
                path = os.path.join(args.wd, directory)
                os.mkdir(path)
                os.system("python3 runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[0]), str(i[1])))
            else:
                if i[1] in ctrl_list:
                    outfile= args.wd+"/metadata_"+str(i[1])+"vs"+str(i[0])+".txt"
                    oup= open(outfile,"w")
                    make_metafiles(i[1],i[0],sample_dict,oup)
                    oup.close()
                    directory= str(i[1])+"vs"+str(i[0])
                    path = os.path.join(args.wd, directory)
                    os.mkdir(path)
                    os.system("python3 runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[1]), str(i[0])))
                else:
                    pass
        else:
            df3= pd.read_csv(args.wd+args.ctrlfile, sep="\t")
            #print(df3)
            records = df3.to_records(index=False)
            result = list(records)
            #print(result)
            for r in result:
                # check if this pair is in your pair file
                print(r,i)
                if tuple(i) == tuple(r):
                    outfile= args.wd+"/metadata_"+str(i[0])+"vs"+str(i[1])+".txt"
                    oup= open(outfile,"w")
                    make_metafiles(i[0],i[1],sample_dict,oup)
                    oup.close()
                    directory= str(i[0])+"vs"+str(i[1])
                    path = os.path.join(args.wd, directory)
                    os.mkdir(path)
                    os.system("python3 runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[0]), str(i[1])))
                # check if reverse pair is in pair file
                elif tuple(Reverse(i)) == tuple(r):
                    outfile= args.wd+"/metadata_"+str(i[1])+"vs"+str(i[0])+".txt"
                    oup= open(outfile,"w")
                    make_metafiles(i[1],i[0],sample_dict,oup)
                    oup.close()
                    directory= str(i[1])+"vs"+str(i[0])
                    path = os.path.join(args.wd, directory)
                    os.mkdir(path)
                    os.system("python3 runDeseq2.py {} {} {} CType CType {} {} -f CType:CType".format(path, counts, outfile, str(i[1]), str(i[0])))



