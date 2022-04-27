#!/usr/bin/env python
#  Find output from scripts using cmdlogtime based on parameters passed in
import os.path
import cmdlogtime
from subprocess import PIPE, run
import re

DATE_DIR_POS = -3  #Some Assumptions: 1) dir_of_out_dirs contains NO ^s. 
                   #                  2) DATE_DIR is third from the end. This could change if I change my parms_log structure 
COMMAND_LINE_DEF_FILE = "./findOutputByParmsCommandLine.txt"
def main():
	(start_time_secs, pretty_start_time, my_args, addl_logfile) = cmdlogtime.begin(COMMAND_LINE_DEF_FILE)   
	dir_of_out_dirs  = my_args["dir_of_out_dirs"]
	if "^" in dir_of_out_dirs:
	    print(dir_of_out_dirs)
	    print("We have BIG problems. Your dir_of_out_dirs contains a ^. The split below assumes no ^ in dir_of_out_dirs")
	    sys.exit(1)
	out_dir = my_args["out_dir"]
	out_file = os.path.join(out_dir, "common_directories.txt")
	kv_pair_string = my_args["key_values"]
	addl_logfile.write("Starting findOutputByParms\n")
	kv_pairs = kv_pair_string.split(",")
	addl_logfile.write("dir to look at: " + dir_of_out_dirs +"\n")
	file_spec = os.path.join(dir_of_out_dirs, "*/parms_log/*.txt" )  #DATE_DIR_POS = -3 because this filespec implies the date directory is in the -3 position. See below.
	addl_logfile.write("filespec: " + file_spec + "\n")
	intersection_of_all_sets = set([])
	first_time = True
	with open(out_file, "w") as out_f:
	    out_f.write("Date Directories in " + dir_of_out_dirs + " that contain the following key value pairs:"+ "\n")     
	for kv in kv_pairs:
	    this_set = set([])
	    key, value = kv.split("^")
	    addl_logfile.write("key: " +  key + " value: " + value + "\n") 
	    with open(out_file, "a") as out_f:
	        out_f.write(kv + "\n") 
	    cmd = "grep -i " + kv + " " + file_spec
	    addl_logfile.write("\n\nCmd: " + cmd + "\n")
	    result = run(cmd, capture_output=True, text=True, shell=True)
	    #print("RC:", result.returncode, "\nOUT:", result.stdout, "\nERR:", result.stderr)
	    #print("aboveFor:", result.stdout)
	    #stdout_str = "".join(map(chr, result.stdout))
	    res1 = result.stdout.split('\n')
	    for res in res1:
	        if (len(res) == 0):
	            continue #rms, not sure why some lines are blank. UGH!
	        parms_file = res.split("^")[0]  # NOTE, This assumes that the file path includes NO ^s!
	        date_dir = parms_file.split("/")[DATE_DIR_POS]
	        this_set.add(date_dir)
	    
	    addl_logfile.write("this_set within KV loop:\n")
	    for date_dir in this_set:
	        addl_logfile.write(date_dir + "\n")    
	    if first_time:
	        intersection_of_all_sets = this_set.copy()  
	    else:
	         intersection_of_all_sets = intersection_of_all_sets.intersection(this_set)
	    first_time = False
	    addl_logfile.write("intersection set within loop *****************************\n")
	    for date_dir in intersection_of_all_sets:
	        addl_logfile.write(date_dir + "\n")    
	addl_logfile.write("at end:\n")
	with open(out_file, "a") as out_f:
	    for date_dir in sorted(intersection_of_all_sets):
	        addl_logfile.write(date_dir +"\n") 
	        out_f.write(date_dir + "\n")   
	cmdlogtime.end(addl_logfile, start_time_secs)
	
if __name__ == "__main__":
    main()