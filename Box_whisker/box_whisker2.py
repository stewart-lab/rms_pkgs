import pandas as pd
import cmdlogtime
import os
import stew_util as su

COMMAND_LINE_DEF_FILE = "./boxWhiskerCommandLine.txt"


def main():
    (start_time_secs, pretty_start_time, my_args, logfile) = cmdlogtime.begin(COMMAND_LINE_DEF_FILE)
    outdir = my_args["out_dir"]
    outfile = my_args["outfile"]
    outboxfile = os.path.join(outdir, outfile)
    infile = my_args["infile"]
    metadata = my_args["metadata"]
    title = my_args["title_for_plot"]
    x_label = my_args["x_label"]
    y_label = my_args["y_label"]

    metadata_dict = {}
    with open(metadata, "r") as metadata_f:
        for line in metadata_f.readlines():
            cols = line.strip().split("\t")
            metadata_dict[cols[0]] = cols[1]

    with open(infile, "r") as infile_f:
        headerline = infile_f.readline()
        samples = headerline.strip().split("\t")
        dataline = infile_f.readline()
        data = dataline.strip().split("\t")

    metadata_list = []
    for sample in samples:
        metadata_list.append(metadata_dict[sample])

    df = pd.DataFrame(zip([float(el) for el in data], samples)).rename(columns={0: "DATA", 1: "SAMPLE"})

    df["comparator"] = metadata_list

    print(df)

    su.make_box_plot(df, "comparator", "DATA", title, x_label, y_label, outboxfile)

    cmdlogtime.end(logfile, start_time_secs)


if __name__ == "__main__":
    main()
