#!/usr/bin/env python
import sys
import os
import os.path
from pathlib import Path as ph
import time  #only needed for the Time 1, 2, 3, printing stuff 
import csv
import km
#import pdb
import skim
import tv
import cmdlogtime

SHOW_TIMES = False
COMMAND_LINE_DEF_FILE = "./processLincsCommandLine.txt"
def main():
    (start_time_secs, pretty_start_time, my_args, logfile) = cmdlogtime.begin(COMMAND_LINE_DEF_FILE, sys.argv[0])
    
    if SHOW_TIMES: print ("Time 1:", time.localtime() )	
    c_terms_file = process_LINCS_file(my_args)
    if SHOW_TIMES: print ("Time 2:", time.localtime()	)
    # For KM: keep ones with FET < some value. Default is 1e-2. Trying to get MORE KM hits, to be conservative, as we will remove drugs with a KM hit.
    km_parms = (" --kp-file " + my_args["a_terms"] + " --tg-file " + c_terms_file + " --fet " + str(my_args["km_fet"]) + " -t -db " + my_args["database"])
    km_res = km.km(km_parms)
    if SHOW_TIMES: print ("Time 3:", time.localtime()	)
    # rms.  may want to try list format for km.km call
    logfile.write("km parameters: " + km_parms + "\n")
    logfile.write("Getting KM information\n")
    res_lookup_km = {el.MT2.id: el for el in km_res}
    if SHOW_TIMES: print ("Time 4:", time.localtime()	)
    res_lookup_tv = {} 
    print("before tv")
    if (my_args["get_treats_vectors"]): # might skip treats vector stuff some of the time, especially during testing as it slows it way down.
        print("getting TV stuff")
        logfile.write("Getting Treats Vector cosine similarity information\n")
        log_list, result_list, left_term_list = tv.tv("outTV " + my_args["a_terms"] + " " + c_terms_file + 
          " -tv_term1 " + my_args["treats_vector_term1"] + " -tv_term2 " + my_args["treats_vector_term2"])  # "outTV ./in_left_termsNewFormat.txt ../LexiconsForSKiM/drugsShort.txt")
        #  " -tv_term1 metformin -tv_term2 diabetes")  # "outTV ./in_left_termsNewFormat.txt ../LexiconsForSKiM/drugsShort.txt")
        i = 0
        
        for res_tups in result_list:
            #print("-------------  Results for: ", left_term_list[i])
            i = i + 1
            for res_tup in res_tups:
                #print(res_tup[0], "\t", res_tup[1], "\t", res_tup[2])
                res_lookup_tv[res_tup[1]] = res_tup[2]  # cosine similarity hashed by drug
    if SHOW_TIMES: print ("Time 5:", time.localtime()	)
    intermediate_out_dir = os.path.join(my_args["out_dir"], "intermediate")
    cmdlogtime.make_dir(intermediate_out_dir)

    logfile.write("Run Skim here for each of the B terms files in B_TERMS_DIR")
    ctr = 0
    skim_bc_out_file_types = []
    bc_ress = []
    if SHOW_TIMES: print ("Time 6:", time.localtime()	)
    for f in os.listdir(my_args["b_terms_dir"]):
        if os.path.isfile(os.path.join(my_args["b_terms_dir"], f)):
            ctr = ctr + 1
            b_terms_file = os.path.join(my_args["b_terms_dir"], f)
            file_pieces = f.split("_")
            skim_bc_out_file_types.append(file_pieces[0])
            # RON may want to make some of this parameters:  20 -s -t -a  (which is num of level2 queries, then s t a, which I can't remember what they are)
            skim_parms = (" --A_file " + my_args["a_terms"] + " --B_file " + b_terms_file + " --C_file " + c_terms_file + " -n 20 -t -db " + my_args["database"] + " --fet "  + str(my_args["skim_fet"]))
            (ab_res, bc_res) = skim.skim(skim_parms)
            if SHOW_TIMES: print ("Time 7.", ctr, ":", time.localtime()	)
            logfile.write("skim parameters " + str(ctr) + ": " + skim_parms + "\n")
            bc_ress.append(bc_res)
    logfile.write("SKiM Processes completed successfully." + "\n")
    if SHOW_TIMES: print ("Time 8:", time.localtime()	)
    curr_out_file = os.path.join(intermediate_out_dir, "first_out.txt")  # rms.  Still need to remove this intermediate file stuff if I can.
    with open(curr_out_file, "w") as first_out_file, open(c_terms_file, "r") as c_file:
        line = c_file.readline()
        line_mod = line.replace("Perturbation\n", "Perturbation\tRatio_KM\tFET_KM\tKM?")  # Note that this replace is dependent on c-terms file having "Perturbation" in header
        for ft in skim_bc_out_file_types:
            line_mod = line_mod + "\t" + ft + "\t" + ft + "?"
        line_mod = line_mod + "\tSkim_tot"
        line_mod = line_mod + "\tTreatVecCosSim"
        for ft in skim_bc_out_file_types:
            line_mod = (line_mod + "\t\ttarget_with_keyphrase_count_" + ft + "\ttarget_count_" + ft + "\tkeyphrase_count_" + ft + "\tdb_article_count_" + ft + "\tfet_p_value_" + ft + "\tratio_" + ft + "\tscore_" + ft + "\t" + ft)
        line_mod = line_mod + "\n"
        first_out_file.write(line_mod)
        ctr = 0

        res_lookup_skims = []
        for bc_res in bc_ress:
            res_lookup_skims.append(get_result_map(bc_res))
            ctr = ctr + 1
        logfile.write("Adding KM information\n")
        logfile.write("Adding SKiM Summary information\n")
        logfile.write("Adding Treats Vector information\n")
        logfile.write("Adding remaining SKiM information\n")

        for line in c_file:
            ctr = 0
            first_out_file.write(get_km_match(line, res_lookup_km))
            skim_tot = 0
            for ft in (skim_bc_out_file_types):  #  the bc_ress list should be in the same order as the skim_bc_out_file_types list. hopefully!
                (line_to_write, ret_skim_hit) = get_skim_match_summary(line, res_lookup_skims[ctr])
                skim_tot = skim_tot + ret_skim_hit
                first_out_file.write(line_to_write)
                ctr = ctr + 1
            first_out_file.write("\t" + str(skim_tot))
            mod_line = line.strip()
            mod_line = mod_line.lower()  # RMS,  for treats vector stuff, we are lowercasing everything, because, at least for the 
            # word vector model I'm currently using everything is lowercase.  Probably will need to make this a parameter, that gets passed around that indicates whether 
            # the word vector model is lowercase, uppercase, or mixed case.
            pieces = mod_line.split("\t")
            #print("pieces1:", pieces[1])
            cos_sim = ""
            if pieces[1] in res_lookup_tv:
                cos_sim = str(res_lookup_tv[pieces[1]])
            first_out_file.write("\t" + cos_sim)
            ctr = 0
            for ft in (skim_bc_out_file_types):  #  the bc_ress list should be in the same order as the skim_bc_out_file_types list. hopefully!
                first_out_file.write(get_skim_match_details(line, res_lookup_skims[ctr]))
                ctr = ctr + 1
            first_out_file.write("\n")
    if SHOW_TIMES: print ("Time 9:", time.localtime()	)
    km_skim_out_skim_tot_sorted_by_skim_tot = sort_file_by_skim_tot(curr_out_file, skim_bc_out_file_types, my_args["keep_km_hit_info"])
    # now lets copy the final files into final_out_dir
    final_out_dir = os.path.join(my_args["out_dir"], "final")
    cmdlogtime.make_dir(final_out_dir)
    full_list_out_file = os.path.join(final_out_dir, "fullList.txt")
    os.system("cp " + curr_out_file + " " + full_list_out_file)
    sorted_list_out_file = os.path.join(final_out_dir, "sortedTrimmedList.txt")
    os.system("cp " + km_skim_out_skim_tot_sorted_by_skim_tot + " " + sorted_list_out_file)
    
    if SHOW_TIMES: print ("Time 10:", time.localtime()	)
    cmdlogtime.end(logfile, start_time_secs)


#    -------------------------------------- FUNCTIONS ----------------------------------------------
def get_result_map(res):
    my_map = {}
    for el in res:
        try:
            my_map[el.MT2.id].append(el)
        except KeyError:
            my_map[el.MT2.id] = [el]
    return my_map

def get_km_match(line, res_lookup_km):
    c_id = line.split()[0]
    if c_id in res_lookup_km:
        #if(res_lookup_km[c_id].MT2.text == ["PCSK9"]):
        #    import pdb
        #    pdb.set_trace()
        extra = f"\t{res_lookup_km[c_id].rat:5f}\t{res_lookup_km[c_id].fet:5f}\t1"
    else:
        extra = "\t\t\t"
    return line.strip() + extra
    
def get_skim_match_summary(line, res_lookup_skim):
    c_id = line.split()[0]
    skim_hit = 0
    extra = "\t"
    #       for res1 in res_lookup_skim:
    if c_id in res_lookup_skim:
        # extra = f'\t{res_lookup_skim[c_id].fet:.5f}\t{res_lookup_skim[c_id].rat:.5f}\t'
        # import pdb
        # pdb.set_trace()
        extra = extra + "|".join([el.MT1.text[0] for el in res_lookup_skim[c_id]])
        extra = extra + "\t1"
        skim_hit = 1
    else:
        extra = "\t\t"
    return extra, skim_hit

def get_skim_match_details(line, res_lookup_skim):
    c_id = line.split()[0]
    if c_id in res_lookup_skim:
        # extra = f'\t{res_lookup_skim[c_id].fet:.5f}\t{res_lookup_skim[c_id].rat:.5f}\t'
        # import pdb
        # pdb.set_trace()
        extra = "\t\t" + "|".join([str(el.counts[2]) for el in res_lookup_skim[c_id]])  # {res_lookup_skim[c_id].counts[2]}
        extra = (extra + "\t" + "|".join([str(el.counts[0]) for el in res_lookup_skim[c_id]]))  # "{res_lookup_skim[c_id].counts[0]}'
        extra = (extra + "\t" + "|".join([str(el.counts[1]) for el in res_lookup_skim[c_id]]))  # "{res_lookup_skim[c_id].counts[1]}'
        extra = (extra + "\t" + "|".join([str(el.counts[3]) for el in res_lookup_skim[c_id]]))  # "{res_lookup_skim[c_id].counts[3]}'
        extra = (extra + "\t" + "|".join([str(el.fet) for el in res_lookup_skim[c_id]]))  # "{res_lookup_skim[c_id].fet}'
        extra = (extra + "\t" + "|".join([str(el.rat) for el in res_lookup_skim[c_id]]))  # "{res_lookup_skim[c_id].rat}'
        extra = (extra + "\t" + "|".join([str(el.score) for el in res_lookup_skim[c_id]]))  # "{res_lookup_skim[c_id].score}'
        extra = (extra + "\t" + "|".join([el.MT1.text[0] for el in res_lookup_skim[c_id]]))  # "{res_lookup_skim[c_id].MT1.text}'
        # extra = extra + f'\t{res_lookup_skim[c_id].fet}'
    else:
        extra = "\t\t\t\t\t\t\t\t\t"
    return extra

def process_LINCS_file(my_args):
    # process LINCS file here,  some regexs, remove ID/perturbation (1st line),  remove duplicates.
    c_terms_file = my_args["lincs_file"] + "_c.txt"
    with open(c_terms_file, "w") as c_file:
        drugs = {}
        with open(my_args["lincs_file"], "r") as lincs_file:
            for (ctr, line) in enumerate(lincs_file.readlines()):
                if ctr == 0:
                    c_file.write("ID\tPerturbation\n")
                    continue
                line_pieces = line.strip().split("\t")
                drug = line_pieces[2].replace('"', "")
                if drug not in drugs.keys():
                    c_file.write(str(line_pieces[0]) + "\t" + str(drug) + "\n")
                drugs[drug] = line_pieces[0]
    return c_terms_file

def sort_file_by_skim_tot(in_file, skim_file_types, keep_km_hit_info):
    num_cols_before_skim_stuff_in_out_file = 5  #RMS number of columns to the left of the skim stuff in the out file
    skim_tot_col = (2 * len(skim_file_types)) + num_cols_before_skim_stuff_in_out_file 
    print("skim_tot_col:", skim_tot_col)
    out_file = in_file + "_skimTotSorted.txt"
    just_skim_hit_file = in_file + "justSKiMHits.txt"
    with open(just_skim_hit_file, "w") as out_f1, open(in_file, "r") as f:
        #print("just opened the skim hit file for writing")
        for (line_ctr, line) in enumerate(f.readlines()):
            #print("in the in_file:", in_file, " line: ", line)
            line_pieces = line.strip().split("\t")
            #print("lenlinepieces:", len(line_pieces))
            if len(line_pieces) >= skim_tot_col and line_pieces[skim_tot_col] != "":
                if ((keep_km_hit_info) or (line_pieces[num_cols_before_skim_stuff_in_out_file -1] != "1")):  #this assume KM>? flag is column right before the skim stuff
                    out_f1.write(line)
    with open(out_file, "w") as out_f:
        file_reader = csv.reader(open(just_skim_hit_file), delimiter="\t")
        header = next(file_reader, None)
        out_f.write("\t".join(header) + "\n")
        for line in sorted(
            file_reader, key=lambda x: int(x[skim_tot_col]), reverse=True
        ):
            out_f.write("\t".join(line) + "\n")
    return out_file

if __name__ == "__main__":
    main()
