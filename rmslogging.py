#!/usr/bin/env python
import argparse
import os.path
from pathlib import Path as ph
# ---------------  FUNCTIONS -------------------
def build_log_file(out_dir, pretty_start_time):
    log_file = "log_" + str(pretty_start_time) + "_.txt"
    return (os.path.join(out_dir, log_file))

def open_log_file(log_file):
    return (open(log_file, "w+"))

def close_log_file(log_file_fh):
    log_file_fh.close()
        
def write_args_and_files (my_args, curr_executing_file, command_line_file, logfile):
    logfile.write("args:\n")
    for attr, value in my_args.items():
        logfile.write(str(attr) + ":" + str(value) + "\n") 
    write_file_contents(curr_executing_file, logfile)
    write_file_contents(command_line_file, logfile)
        
def write_file_contents(a_file, logfile):
    logfile.write("\n\n-------------- START " + a_file + " -----------------\n")
    with open(a_file, "r") as file_to_write_out:
        for line in file_to_write_out:
            logfile.write(str(line))
    logfile.write("\n\n-------------- END " + a_file + " -----------------\n")              
    