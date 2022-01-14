#!/usr/bin/env python
import argparse
import os.path
from pathlib import Path as ph
import rmslogging


def build_arg_parser(command_line_def_file):
    with open(command_line_def_file, "r") as cmd_line_f:
        first_line = skip_headers(cmd_line_f)
        parser = argparse.ArgumentParser(
            description=get_description_from_first_line(first_line)
        )
        for line in cmd_line_f:
            if line:
                add_parser_argument_from_line(line)
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
    keys = (
        "name",
        "help",
        "is_out_dir",
        "is_dir",
        "check_dir",
        "is_file",
        "check_file",
        "alt_name",
        "default",
        "type",
    )
    return {k: v for (k, v) in zip(keys, line.strip().split(sep))}


def is_positional(arg_defs):
    return not arg_defs["name"].startswith("-")


def positional_arg(arg_defs):
    assert arg_defs["alt_name"] == ""
    assert arg_defs["default"] == ""


"""

if arg_type:
    parser.add_argument(
        arg_name, help=arg_help, type=eval(arg_type)
    )
    # print("adding typed arg: ", arg_name, " help:", arg_help,  " type:", eval(arg_type))
else:
    parser.add_argument(arg_name, help=arg_help)
"""


def flagged_arg(arg_defs):
    pass


"""
            else:
                assert alt_arg_name
                kwargs = {"help": arg_help}
                if default:
                    kwargs["default"] = default
                typestr = ""
                if arg_type:
                    kwargs["type"] = eval(arg_type)
                    typestr = " type: " + arg_type
                    if default:
                        kwargs["default"] = kwargs["type"](kwargs["default"])
                parser.add_argument(arg_name, alt_arg_name, **kwargs)
"""


def add_parser_argument_from_line(line):
    arg_defs = get_args_from_line(line)
    if is_positional(arg_defs):
        return positional_arg(arg_defs)
    return flagged_arg(arg_defs)


def massage_and_validate_args(
    args, start_time_secs, pretty_start_time, command_line_def_file
):
    new_args = {}
    dirs_to_check = []
    file_paths_to_check = []
    the_out_dir = ""
    with open(command_line_def_file, "r") as cmd_line_f:
        line = cmd_line_f.readline()
        first_line = True
        while line:
            if line.startswith("#"):
                line = cmd_line_f.readline()
                continue
            if first_line:  # skip description line
                first_line = False
                line = cmd_line_f.readline()
                continue
            (
                arg_name,
                arg_help,
                is_out_dir,
                is_dir,
                check_dir,
                is_file,
                check_file,
                alt_arg_name,
                default,
                arg_type,
            ) = line.strip().split("|")
            tmp_arg_name = arg_name
            if arg_name.startswith("-"):
                tmp_arg_name = alt_arg_name.lstrip("-")
            new_args[tmp_arg_name] = args.__dict__[
                tmp_arg_name
            ]  # if it is a directory or file,  new_args[tmp_arg_name] will be overlain below
            if is_dir == "1" or is_file == "1":
                # print (tmp_arg_name)
                # print (args.__dict__[tmp_arg_name])
                new_args[tmp_arg_name] = os.path.abspath(
                    args.__dict__[tmp_arg_name]
                )
            if is_out_dir == "1":
                make_dir(new_args[tmp_arg_name])
                new_args[tmp_arg_name] = os.path.join(
                    new_args[tmp_arg_name], pretty_start_time
                )
                make_dir(new_args[tmp_arg_name])
                the_out_dir = new_args[tmp_arg_name]

            if check_dir == "1":
                dirs_to_check.append(new_args[tmp_arg_name])
            if check_file == "1":
                if (
                    args.__dict__[tmp_arg_name] != "ZZZ"
                ):  # not sure if this is correct... RMS.
                    file_paths_to_check.append(new_args[tmp_arg_name])
            line = cmd_line_f.readline()

    for dir in dirs_to_check:
        assert os.path.isdir(dir), dir + " directory does NOT exist!"
    for fpath in file_paths_to_check:
        assert os.path.isfile(fpath), fpath + " file does NOT exist!"
    new_args["start_time_secs"] = start_time_secs
    new_args["pretty_start_time"] = pretty_start_time
    new_args["log_file"] = rmslogging.build_log_file(
        the_out_dir, pretty_start_time
    )  # requires an out_dir RMS!!!
    return new_args


def get_args(start_time_secs, pretty_start_time, command_line_def_file):
    parser = build_arg_parser(command_line_def_file)
    my_args = massage_and_validate_args(
        parser.parse_args(),
        start_time_secs,
        pretty_start_time,
        command_line_def_file,
    )
    return my_args


def make_dir(dir):
    ph(dir).mkdir(exist_ok=True)
