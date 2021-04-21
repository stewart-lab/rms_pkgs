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
    
def write_args(my_args, logfile):
    logfile.write("args:\n")
    for attr, value in my_args.items():
        logfile.write(str(attr) + ":" + str(value) + "\n")       
    