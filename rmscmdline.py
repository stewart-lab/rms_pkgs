#!/usr/bin/env python
import argparse
import os.path
from pathlib import Path as ph
import rmslogging
# ---------------  FUNCTIONS -------------------
def build_arg_parser(command_line_def_file):
    with open(command_line_def_file, "r") as cmd_line_f:
        first_line = skip_headers(cmd_line_f)
        parser = argparse.ArgumentParser(description=get_description_from_first_line(first_line))
        for line in cmd_line_f:
            if line:
                (arg_def_list, arg_def_kwargs_dict) = get_arg_defs_needed_to_add(line)
                parser.add_argument(*arg_def_list, **arg_def_kwargs_dict)
    return parser

def skip_headers(f, header_flag="#"):
    line = f.readline()
    while line.startswith(header_flag):
        line = f.readline()
    return line

def get_description_from_first_line(line):
    return line.strip()

def get_args_from_line(line, sep="|"):
    # if we want defaults, so line doesnt need to be full,
    # add them now: args_defs = {'key': default_val}
    keys = ("name", "help", "is_out_dir", "is_dir", "check_dir", "is_file", "check_file", "alt_name", "default","type")
    return {k: v for (k, v) in zip(keys, line.strip().split(sep))}

def get_arg_defs_needed_to_add(line):
    arg_defs = get_args_from_line(line)
    if is_positional(arg_defs):
        return get_defs_for_positional_arg(arg_defs)
    else:
        return get_defs_for_flagged_arg(arg_defs)
    
def is_positional(arg_defs):
    return not arg_defs["name"].startswith("-")

def get_defs_for_positional_arg(arg_defs):
    assert arg_defs["alt_name"] == ""
    assert arg_defs["default"] == ""
    arg_def_list = []
    arg_def_list.append(arg_defs["name"])
    arg_def_kwargs_dict = {}
    arg_def_kwargs_dict["help"] = arg_defs["help"]
    if arg_defs["type"]:
        arg_def_kwargs_dict["type"] = eval(arg_defs["type"])
    return (arg_def_list, arg_def_kwargs_dict)
    
def get_defs_for_flagged_arg(arg_defs):
    assert(arg_defs["alt_name"])
    arg_def_list = []
    arg_def_list.append(arg_defs["name"])
    arg_def_list.append(arg_defs["alt_name"])
    arg_def_kwargs_dict = {}
    arg_def_kwargs_dict["help"] = arg_defs["help"]
    if (arg_defs["default"]):
        arg_def_kwargs_dict['default'] = arg_defs["default"]
    typestr = ""
    if (arg_defs["type"]):
        arg_def_kwargs_dict['type'] = eval(arg_defs["type"]) 
        if (arg_defs["default"]):
            arg_def_kwargs_dict['default'] =  arg_def_kwargs_dict['type']( arg_def_kwargs_dict['default'])    
    return (arg_def_list, arg_def_kwargs_dict)
    
def massage_and_validate_args(args, start_time_secs, pretty_start_time, command_line_def_file):
    new_args = {}
    dirs_to_check = []
    file_paths_to_check = []
    the_out_dir = ""
    with open(command_line_def_file, "r") as cmd_line_f:
        first_line = skip_headers(cmd_line_f) #first_line at this point will contain the description line.
        for line in cmd_line_f:
            if line:
                arg_defs = get_args_from_line(line)
                tmp_name = arg_defs["name"]
                if (arg_defs["name"].startswith("-")):
                	tmp_name = arg_defs["alt_name"].lstrip("-")
                new_args[tmp_name] = args.__dict__[tmp_name]  # if it is a directory or file,  new_args[tmp_name] will be overlain below
                if (arg_defs["is_dir"] == "1" or arg_defs["is_file"] == "1"):
                    if (args.__dict__[tmp_name]): #rms. I don't like this.  I think I need a different way to check that the flagged arg is NOT filled in, versus filled in incorrecdtly
                	    new_args[tmp_name] = os.path.abspath(args.__dict__[tmp_name]) 	   
                if (arg_defs["is_out_dir"]  == "1"):
                	the_out_dir = new_args[tmp_name]
                if (arg_defs["check_dir"] == "1"):
                    if (args.__dict__[tmp_name]):  #rms. I don't like this.  I think I need a different way to check that the flagged arg is NOT filled in, versus filled in incorrecdtly
                	    dirs_to_check.append(new_args[tmp_name])
                if (arg_defs["check_file"] == "1"):  # same goes for files, see rms comment 2 lines above.
                	if (not args.__dict__[tmp_name].endswith("ZZZ")): #I think this is the correct logic... RMS.
                		file_paths_to_check.append(new_args[tmp_name])  
    for dir in dirs_to_check:
        assert os.path.isdir(dir), dir + " directory does NOT exist!"
    for fpath in file_paths_to_check:
        assert os.path.isfile(fpath), fpath + " file does NOT exist!"
    new_args["start_time_secs"] = start_time_secs
    new_args["pretty_start_time"] = pretty_start_time
    assert(the_out_dir != "")
    if ((new_args["rerun_out_directory"])):
        the_out_dir = new_args["rerun_out_directory"]
        print("rerundir:", new_args["rerun_out_directory"])
    else:
        make_dir(the_out_dir)
        the_out_dir = os.path.join(the_out_dir, pretty_start_time)
    make_dir(the_out_dir)
    print("theoutdir:", the_out_dir)
    
    print(new_args["remove_sra_files"])
    
    new_args["out_dir"] = the_out_dir
    new_args["log_file"] = rmslogging.build_log_file(the_out_dir, pretty_start_time)  #requires an out_dir RMS!!!
    print ("logfile: ", new_args["log_file"])
    return new_args
                      
def get_args(start_time_secs, pretty_start_time, command_line_def_file):
    parser = build_arg_parser(command_line_def_file)
    my_args = massage_and_validate_args(parser.parse_args(), start_time_secs, pretty_start_time, command_line_def_file)
    return my_args

def make_dir(dir):
    x = ph(dir).mkdir(exist_ok=True)       