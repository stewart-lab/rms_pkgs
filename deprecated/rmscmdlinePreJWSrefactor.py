#!/usr/bin/env python
import argparse
import os.path
from pathlib import Path as ph
import rmslogging
# ---------------  FUNCTIONS -------------------
def build_arg_parser(command_line_def_file):
    with open(command_line_def_file, "r") as cmd_line_f:
        line = cmd_line_f.readline()
        first_line = True
        while (line):
            if line.startswith('#'): 
                line = cmd_line_f.readline()
                continue
            if (first_line):
                descr = line.strip()
                parser = argparse.ArgumentParser(description=descr)
                first_line = False
                line = cmd_line_f.readline()
                continue
            (arg_name, arg_help, is_out_dir, is_dir, check_dir, is_file, check_file, alt_arg_name, default, arg_type) = line.strip().split("|")
      
            if (not arg_name.startswith("-")):
                assert (alt_arg_name == "")
                assert (default == "")
                if (arg_type):
                    parser.add_argument(arg_name, help=arg_help, type=eval(arg_type)) 
                    #print("adding typed arg: ", arg_name, " help:", arg_help,  " type:", eval(arg_type))
                else:
                    parser.add_argument(arg_name, help=arg_help)
            else: 
                assert(alt_arg_name)
                kwargs = {'help':arg_help}
                if (default):
                   kwargs['default'] = default
                typestr = ""
                if (arg_type):
                   kwargs['type'] = eval(arg_type) 
                   typestr= " type: " + arg_type 
                   if (default):
                       kwargs['default'] = kwargs['type'](kwargs['default'])    
                parser.add_argument(arg_name, alt_arg_name, **kwargs)
                #print("adding KV arg: ", arg_name, " alt_arg_name:", alt_arg_name,  " default:", default,  "help:", arg_help,  typestr)
            line = cmd_line_f.readline()                    
    return parser     
    
def massage_and_validate_args(args, start_time_secs, pretty_start_time, command_line_def_file):
    new_args = {}
    dirs_to_check = []
    file_paths_to_check = []
    the_out_dir = ""
    with open(command_line_def_file, "r") as cmd_line_f:
        line = cmd_line_f.readline()
        first_line = True
        while (line):
            if line.startswith('#'): 
                line = cmd_line_f.readline()
                continue
            if (first_line):  # skip description line
                first_line = False
                line = cmd_line_f.readline()
                continue
            (arg_name, arg_help, is_out_dir, is_dir, check_dir, is_file, check_file, alt_arg_name, default, arg_type) = line.strip().split("|")
            tmp_arg_name = arg_name
            if (arg_name.startswith("-")):
                tmp_arg_name = alt_arg_name.lstrip("-")
            new_args[tmp_arg_name] = args.__dict__[tmp_arg_name]  # if it is a directory or file,  new_args[tmp_arg_name] will be overlain below
            if (is_dir == "1" or is_file == "1"):
                #print (tmp_arg_name)
                #print (args.__dict__[tmp_arg_name])
                new_args[tmp_arg_name] = os.path.abspath(args.__dict__[tmp_arg_name])    
            if (is_out_dir  == "1"):
                make_dir(new_args[tmp_arg_name])
                new_args[tmp_arg_name] = os.path.join(new_args[tmp_arg_name], pretty_start_time)
                make_dir(new_args[tmp_arg_name])
                the_out_dir = new_args[tmp_arg_name]
            
            if (check_dir == "1"):
                dirs_to_check.append(new_args[tmp_arg_name])
            if (check_file =="1"):
                if (args.__dict__[tmp_arg_name] != "ZZZ"): #not sure if this is correct... RMS.
                    file_paths_to_check.append(new_args[tmp_arg_name])
            line = cmd_line_f.readline()     
    
    for dir in dirs_to_check:
        assert os.path.isdir(dir), dir + " directory does NOT exist!"
    for fpath in file_paths_to_check:
        assert os.path.isfile(fpath), fpath + " file does NOT exist!"
    new_args["start_time_secs"] = start_time_secs
    new_args["pretty_start_time"] = pretty_start_time
    new_args["log_file"] = rmslogging.build_log_file(the_out_dir, pretty_start_time)  #requires an out_dir RMS!!!
    return new_args

def get_args(start_time_secs, pretty_start_time, command_line_def_file):
    parser = build_arg_parser(command_line_def_file)
    my_args = massage_and_validate_args(parser.parse_args(), start_time_secs, pretty_start_time, command_line_def_file)
    return my_args

def make_dir(dir):
    x = ph(dir).mkdir(exist_ok=True)       