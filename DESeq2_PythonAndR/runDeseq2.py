#!/usr/bin/env python
#  Run Deseq2 via subprocess call to an Rscript

import cmdlogtime
from subprocess import run

COMMAND_LINE_DEF_FILE = "./runDeseq2CommandLine.txt"


def main():
    (start_time_secs, pretty_start_time, my_args, addl_logfile) = cmdlogtime.begin(COMMAND_LINE_DEF_FILE)
    out_dir = my_args["out_dir"]
    counts_file = my_args["counts"]
    metadata_file = my_args["metadata"]
    factorize = my_args["factorize_these"]
    contrast = my_args["contrast"]
    design = my_args["design"]
    cond1 = my_args["cond1"]
    cond2 = my_args["cond2"]
    gene_id_header = my_args["gene_id_header"]
    sample_header = my_args["sample_header"]
    low_count_cutoff = my_args["low_count_cutoff"]
    proportion_of_samples_required = my_args["proportion_of_samples_required"]
    addl_logfile.write("Starting runDeseq2\n")

    # build cmd from parameters.
    factor_string = ""
    if (factorize is not None):
        factor_string = " -f " + factorize
    gene_id_header_string = ""
    if (gene_id_header is not None):
        gene_id_header_string = " -g " + gene_id_header
    sample_header_string = ""
    if (sample_header is not None):
        sample_header_string = " -s " + sample_header
    cmd = ("Rscript Deseq2_mir.R -c " + counts_file + " -m " + metadata_file
           + " -o " + out_dir + " -t " + contrast + " -d " + design + " -a  " + cond1 + " -b  " + cond2
           + gene_id_header_string + sample_header_string + factor_string
           + " -l " + low_count_cutoff + " -p " + proportion_of_samples_required
           )
    addl_logfile.write("\n\nCmd: " + cmd + "\n")
    result = run(cmd, capture_output=True, text=True, shell=True)
    if (result.returncode):
        print("RC:", result.returncode, "\nOUT:", result.stdout, "\nERR:", result.stderr)
    addl_logfile.write("RC:" + str(result.returncode) + "\nOUT:" + result.stdout + "\nERR:" + result.stderr)
    # print("aboveFor:", result.stdout)
    # stdout_str = "".join(map(chr, result.stdout))
    # res1 = result.stdout.split('\n')
    # for res in res1:
    #    if (len(res) == 0):
    #         continue #rms, not sure why some lines are blank. UGH!
    #    parms_file = res.split("^")[0]  # NOTE, This assumes that the file path includes NO ^s!
    #    date_dir = parms_file.split("/")[DATE_DIR_POS]
    #    this_set.add(date_dir)

    cmdlogtime.end(addl_logfile, start_time_secs)


if __name__ == "__main__":
    main()
