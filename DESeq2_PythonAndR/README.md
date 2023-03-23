# DESeq2_RScript
The goal of this project is to wrap DESeq2 into a command line exetubale R script


Packages I needed to install:
DESeq2  (see https://bioconductor.org/packages/release/bioc/html/DESeq2.html)
EnhancedVolcano (see https://bioconductor.org/packages/release/bioc/html/EnhancedVolcano.html)
optparse (from cran)
ashr (from cran)

# DE run all contrasts python script
This script is a wrapper to the runDeseq2.py script in order to run multiple contrasts at once.

* You will need the same packages as above, as well as the cmdlogtime package from python
* input files include:
    - working directory where output files go
    - expression file: counts tsv file
    - metadata file: ID column (sample replicate names) and Group column (sample group to contrast)
* options:
    - control (-c) to give a single control for all contrasts
    - control file (-cf) a file with all control-sample pairs for contrasts

Example run:

      python run_all_DE_contrasts_cmdlogtime.py example_contrasts_in_out_cmdline/out/ genes.no_mt.ec.tab_nodescr_example.txt metadata_file.txt -cf control_file.txt
