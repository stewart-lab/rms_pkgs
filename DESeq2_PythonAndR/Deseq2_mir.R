#!/usr/bin/env Rscript  # do I need this??

#Import gene expression data to DESeq2 to analyze RNAseq with different visualization tools
#Run this before Venn diagram and volcano plot
# RMS. Not sure yet how to make a Venn diagram
library("DESeq2")
library("ggplot2")
library("EnhancedVolcano")
library("optparse")

option_list = list(
  make_option(c("-c", "--counts"), type="character", default=NULL, 
              help="counts file name (should be a tsv of un-normalized counts)", metavar="character"),
  make_option(c("-m", "--metadata"), type="character", default=NULL, 
              help="metadata file name (should be a tsv)", metavar="character"),
  make_option(c("-d", "--design"), type="character", default=NULL, 
              help="design to use (e.g. Gender2+group)  (no ~)", metavar="character"),
  make_option(c("-t", "--contrast"), type="character", default=NULL, 
              help="contrast (e.g. Gender2)", metavar="character"),
  make_option(c("-a", "--condition1"), type="character", default=NULL, 
              help="condition1 (e.g. 1)", metavar="character"),
  make_option(c("-b", "--condition2"), type="character", default=NULL, 
              help="condition2 (e.g. 0)", metavar="character"),
  make_option(c("-f", "--factorize"), type="character", default=NULL, 
              help="Name1:val1,Name2:Val2, list of name:value pairs to factorize (e.g. group:CType,Gender2:Gender) ", metavar="character"),
  make_option(c("-o", "--out_dir"), type="character", default="./out/", 
              help="output directory", metavar="character"),
  make_option(c("-g", "--gene_id_header"), type="character", default="gene_id", 
              help="header for gene column in count matrix (e.g. gene_id, or symbol)", metavar="character"),
  make_option(c("-s", "--sample_header"), type="character", default="Sample", 
              help="header for Sample column in metadata file (e.g. Sample)", metavar="character"),
  make_option(c("-l", "--low_count_cutoff"), type="double", default=1, 
              help="Lower bound cutoff for counts in a sample to consider the gene useful for DE.", metavar="character"),
  make_option(c("-p", "--proportion_of_samples_above_low_count_cutoff"), type="double", default=0.33, 
              help="Proportion of samples with gene counts above lower bound cutoff to consider the gene useful for DE.", metavar="character")
); 
opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);
#  check parameters
if (is.null(opt$counts)){
  print_help(opt_parser)
  stop("Must provide a counts tsv file", call.=FALSE)
}
if (is.null(opt$metadata)){
  print_help(opt_parser)
  stop("Must provide a metadata tsv file", call.=FALSE)
}
if (is.null(opt$contrast)){
  print_help(opt_parser)
  stop("Must provide a contrast", call.=FALSE)
}
if (is.null(opt$design)){
  print_help(opt_parser)
  stop("Must provide a design", call.=FALSE)
}
if (is.null(opt$condition1)){
  print_help(opt_parser)
  stop("Must provide a condition1", call.=FALSE)
}
if (is.null(opt$condition2)){
  print_help(opt_parser)
  stop("Must provide a condition2", call.=FALSE)
}
#  Load parameters into variables
count_tsv <- opt$counts
metadata_tsv <- opt$metadata
factorize_these <- opt$factorize
out_dir <- opt$out_dir
design_to_use = opt$design
contrast = opt$contrast
cond1 = opt$condition1
cond2 = opt$condition2
sample_header = opt$sample_header
gene_id_header = opt$gene_id_header
low_count_cutoff = opt$low_count_cutoff
proportion_of_samples_above_low_count_cutoff = opt$proportion_of_samples_above_low_count_cutoff

# read metaData 
metaData <- read.csv(metadata_tsv, header=TRUE, sep ="\t")

# set up output directory and output files
out_prefix = paste0("DE_contrast_", contrast, "_design_", design_to_use, "_cond1_", cond1, "_cond2_", cond2) 
out_name_full  = paste0(out_prefix, ".tsv")
out_name_ct  = paste0(out_prefix, "_normalized_counts.txt")
volc_name_full = paste0("volc_", out_prefix, ".pdf")
out_name_fp = file.path(out_dir, out_name_full)
out_name_fp2 = file.path(out_dir, out_name_ct)
volc_name_fp = file.path(out_dir, volc_name_full)
if (! startsWith(out_dir, "/")) {
  out_dir = file.path(getwd(), out_dir)
} 
ifelse(!dir.exists(out_dir), dir.create(file.path(out_dir)), TRUE)

# Factorize stuff to factorize
if (! is.null(factorize_these)){
  to_factorize <- unlist(strsplit(factorize_these, ","))  
  for (f in to_factorize){
    print(f)
    name_val <- unlist(strsplit(f, ":"))
    print (paste("nameval1:", name_val[1]))
    print (paste("nameval2:", name_val[2]))
    col_to_add <- factor(metaData[[name_val[2]]])
    metaData[name_val[1]] <- col_to_add
  }
}
print(metaData)

#Get counts, use raw (un-normalized) data
countData <- read.csv(count_tsv, header = TRUE, sep = "\t")
head(countData)
print(metaData[sample_header])
# require that the first column is named "symbol" in the genes file
# and that header for the sample names is "Sample"
name_vector = unlist(metaData[sample_header])
name_vector = append(name_vector, gene_id_header, 0)
countData <- countData[name_vector]
head(countData)
# Round the data
rnd <- function(x) trunc(x+sign(x)*0.5)
rnd_countData <- rnd(countData[,-1])
rnd_countData <- data.frame(GENE_ID = countData[,1],rnd_countData)

# run deseq2 function
run_deseq <- function(counts_mtx, meta_data, cond1, cond2, out_f, out_f2, design_to_use, contrast, low_count_cutoff, proportion_of_samples_above_low_count_cutoff) {
  design_to_use <- paste0("~", design_to_use)
  dds <- DESeqDataSetFromMatrix(
        countData=counts_mtx, 
        colData=meta_data, 
        design=formula(design_to_use),
        tidy = TRUE
      )
  ncol = (ncol(dds))
  # Filter out some genes based on a count_cutoff and a sample_cutoff
  num_samples_cutoff = round(ncol * proportion_of_samples_above_low_count_cutoff)
  print(num_samples_cutoff)
  keep <- rowSums(counts(dds) >= low_count_cutoff) > num_samples_cutoff  # filters out genes with some number of samples that have low counts
  #  maybe particularly useful to get rid of some genes when you have a LOT of samples. E.g. scRNAseq
  dds <- dds[keep,]
  # get normalized counts across samples (median of ratios method)
  dds2 <- estimateSizeFactors(dds) # estimate normalization
  print(sizeFactors(dds2)) # normalization factor
  normalized_counts <- counts(dds2, normalized=TRUE) # normalized counts
  # write normalized counts
  
  write.table(normalized_counts, file= out_f2, sep="\t", quote=F, col.names=NA)
  # get contrasts
  dds@colData[contrast] <- relevel(unlist(dds@colData[contrast]), ref = cond1)  
  
  dds <- DESeq(dds)
  # Note that independentFiltering does NOT seem to be happening, even though it is the default.
  res <- results(dds, contrast=c(contrast,cond1, cond2))
  res <- lfcShrink(dds, contrast=c(contrast,cond1, cond2), res = res, type = "ashr")
  
  write.table(data.frame(res), file = out_f, sep='\t', row.names=T, quote=F, col.names = NA)
  volc <- EnhancedVolcano(res, lab = rownames(res), x = "log2FoldChange", y = "pvalue", xlim = c(-10,10), axisLabSize = 12, title = "", subtitle = "", captionLabSize = 8, pCutoff = 0.05, FCcutoff = 1.5, pointSize = 3.0, labFace = "bold", labSize = 3.0, legendPosition = 'none', legendLabSize = 10)
  pdf(volc_name_fp)
  plot(volc)
  dev.off()
  resultsNames(dds)
  head(res)
}  # END run_deseq function

# run deseq2
run_deseq(rnd_countData, metaData, cond1, cond2, out_name_fp, out_name_fp2, design_to_use, contrast, low_count_cutoff, proportion_of_samples_above_low_count_cutoff)

#   -------------------------  END -----------------------
#   NOTES BELOW ON PARAMETERS THAT RON HAS BEEN USING, AND OTHER NOTES ABOUT DESIGN formulae etc...
#  Already parameterized:
#count_tsv <- 'g.ec.tsv'
#metadata_tsv <- 'metadata2.tsv'
#factorize_these <- "group:CType,Gender2:Gender"
#out_dir <- "./out/"
#design_to_use = "Gender2+group"
#contrast = "Gender2"
#cond1 = "1"
#cond2 = "0"

#design_to_use = "AgeScaled+group"
#contrast = "group"
#cond1 = "H9"
#cond2 = "CAR"

# Note on NOT factorizing a continous variable
#Converting design variables into factors (not necessary)
#Making AgeScaled a factor  is not really valid, as it is essentially a continuous numeric
#metaData$AgeScaled2 <- factor(metaData$AgeScaled)   # don't try to factorize a continuous variable
#  if you factorize a continuous variable, then use it in the design matrix, you'll get  a message saying 
#  "matrix is not full rank".
#  this is because you get one category for each instance of the continous variable (such as age)
#  you can acheive full rank if, in this case, some of the ages are SHARED across the other columns
#   in the design matrix.  e.g.  same age in both H9 and CAR. This is a hack.
#  So, don't factorize a continous variable.

# Note on Design formulae:
#design=~Gender2+group,    #compares by group, controlling for gender
#design=~AgeScaled+group,  # order matters here if you don't specify a contrast. 
#Contrast is done on the last one specified. Not sure how it chooses 
# which one as level 1 vs other levels.
# it seems that if "group" is at the end, and later you specify H9 is level 1,
# then it finds other "groups", in this case "CAR" to compare to.
# However if AgeScaled is the last in the design formula, it still works. 
# Not sure why.  In this case, I specified "H9" as level 1 for group.  However
# nothing was specified at a particular level with regard to AgeScaled.  
# Matt says that in this case, it will compare AgeScaled  to the "first column" 
# which I think in the case of design=~group+AgeScaled would be group?  
# Not really sure about this.  
# The main lessons are:
#  1.  always specify a contrast
#  2.  always relevel so you know what will be the denominator
#
#  If you specify design=~AgeScaled+group, and contrast the groups, 
# then in this case you are contrasting across the groups and correcting 
# for the effect of age while you do this contrast.
# you can add "interactions" like design=~AgeScaled+ group + AgeScaled:group.   
#I don't fully understand interactions and when you would use them quite yet. 
#Something to ponder.
# Need to read: 
#https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html#interactions 


# a couple of example rscript commands to run from the command line:
#     Rscript Deseq2_NOD_analysisForAECvsSidePop.R -c g.ec.tsv -m metadata.tsv -f group:CType,Gender2:Gender -o out4 -t group -d AgeScaled+group -a H9 -b CAR
#     Rscript Deseq2_NOD_analysisForAECvsSidePop.R -c g.ec.tsv -m metadata.tsv -f group:CType,Gender2:Gender -o out4 -t Gender2 -d Gender2+group -a 1 -b 0
