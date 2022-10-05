#Import gene expression data to DESeq2 to analyze RNAseq with different visualization tools
#Make sure to edit "GROUP" in metaData based on clustering from dendrogram
#Run this before Venn diagram and volcano plot
library("DESeq2")
library("ggplot2")
library("EnhancedVolcano")
do_by_group <- 1

#Use raw data
#countData <- read.csv("/Users/matthewbernstein/Development/anna_karenina_beta_cell/data_for_DESeq2/Raw_Matrix_filter_rmDup.NOD_comparison.csv", header = TRUE, sep = ",")
#countData <- read.csv("/Users/matthewbernstein/Development/anna_karenina_beta_cell/data_for_DESeq2/Raw_Matrix_filter_rmDup.NOD_comparison.csv", header = TRUE, sep = ",")
countData <- read.csv('g.ec.tsv', header = TRUE, sep = "\t")
head(countData)

#metaData without E13.5 samples, separate diabetic group into T1D and T2D
#metaData <- read.csv("/Users/matthewbernstein/Development/anna_karenina_beta_cell/data_for_DESeq2/AKP_Metadata_v2.NOD_comparison.csv", header = TRUE, sep = ",")
metaData <- read.csv('metadata.tsv', header=TRUE, sep ="\t")
metaData$AgeScaled <- c(1.2,5, 3, 2, 5, 10)
metaData$AgeScaled <- c(1.2,5, 3, 2, 6, 10)
#metaData$AgeScaled <- c(1.2,5, 3, 2, 5, 1.2)
metaData$Gender <- c(1,0,0,1,1,1)
metaData$group <- factor(metaData$CType)
#metaData$group <- metaData$CType

head(metaData)

# Round the data
rnd <- function(x) trunc(x+sign(x)*0.5)
rnd_countData <- rnd(countData[,-1])
rnd_countData <- data.frame(GENE_ID = countData[,1],rnd_countData)

#Converting design variables into factors (not necessary)
#metaData$NOD_GROUP <- as.factor(metaData$NOD_GROUP)
#metaData$COND <- as.factor(metaData$COND)
#metaData$BATCH <- as.factor(metaData$BATCH)
#Making AgeScaled a factor  is not really valid, as it is essentially a continuous numeric
#metaData$AgeScaled2 <- factor(metaData$AgeScaled)   # don't try to factorize a continuous variable
#  if you factorize a continuous variable, then use it in the design matrix, you'll get  a message saying "matrix is not full rank".
#  this is because you get one category for each instance of the continous variable (such as age)
#  you can acheive full rank if, in this case, some of the ages are SHARED across the other columns in the design matrix.  e.g.  same age in both H9 and CAR. This is a hack.
#  So, don't factorize a continous variable.
metaData$Gender2 <- factor(metaData$Gender) 
#head(metaData)
run_deseq <- function(counts_mtx, meta_data, cond1, cond2, out_f, do_by_group) {
  dds <- DESeqDataSetFromMatrix(
        countData=counts_mtx, 
        colData=meta_data, 
        #design=~Gender2+group,    #compares by group, controlling for gender
        design=~AgeScaled+group,   # order matters here if you don't specify a contrast. Contrast is done on the last one specified. Not sure how it chooses which one as level 1 vs other levels.
                                   # it seems that if "group" is at the end, and later you specify H9 is level 1, then it finds other "groups", in this case "CAR" to compare to.
                                   # However if AgeScaled is the last in the design formula, it still works.  Not sure why.  In this case, I specified "H9" as level 1 for group.  However
                                   # nothing was specified at a particular level with regard to AgeScaled.  Matt says that in this case, it will compare AgeScaled  to the "first column" 
                                   # which I think in the case of design=~group+AgeScaled would be group?  Not really sure about this.  The main lessons are:
                                   #  1.  always specify a contrast
                                   #  2.  always relevel so you know what will be the denominator
                                   #
                                   #  If you specify design=~AgeScaled+Group, and contrast the groups, then in this case you are contrasting across the groups and correcting for the effect of age while you do this contrast.
                                   # you can add "interactions" like design=~AgeScaled+ group + AgeScaled:group.    I don't fully understand interactions and when you would use them quite yet. Something to ponder.
                                   # Need to read: https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html#interactions 
       tidy = TRUE
      )
  
  keep <- rowSums(counts(dds) >= 2) > 5
  dds <- dds[keep,]
  #dds$NOD_GROUP <- relevel(dds$NOD_GROUP, ref = cond1)
  
  if(do_by_group){
      dds$group <- relevel(dds$group, ref = cond1)  #specify cond1 as level 1 here.
  } else{
      dds$Gender2 <- relevel(dds$Gender2, ref = cond1)
  }
  dds <- DESeq(dds)
  res <- results(dds)  # results just extracts stuff from dds
  #head(results(dds, tidy=TRUE))
  if (do_by_group){
     #res <- results(dds)  #testing to see what happens if you don't give it a contrast.  Dangerous.   Always specify a contrast.
     #res <- results(dds, contrast=c("group",cond2, cond1))  #if you flip the cond1 cond2 order, the l2fc is flipped (2.1 becomes -2.1)
     res <- results(dds, contrast=c("group",cond1, cond2))
     res <- lfcShrink(dds, contrast=c("group",cond1, cond2), res = res, type = "ashr")
     #res <- results(dds, name="AgeScaled")  # if you want to "compare" across a continuous variable use "name=". In this case, I think the L2FC is reported in units of that variable
     #res <- lfcShrink(dds, res = res, type = "ashr")
  } else{
     res <- results(dds, contrast=c("Gender2",cond1, cond2))
     res <- lfcShrink(dds, contrast=c("Gender2",cond1, cond2), res = res, type = "ashr")
  }
  
  #write.csv(res, out_f)
  write.table(data.frame(res), file = out_f, sep='\t', row.names=T, quote=F)
  EnhancedVolcano(res, lab = rownames(res), x = "log2FoldChange", y = "pvalue", xlim = c(-10,10), axisLabSize = 12, title = "", subtitle = "", captionLabSize = 8, pCutoff = 0.05, FCcutoff = 1.5, pointSize = 3.0, labFace = "bold", labSize = 3.0, legendPosition = 'none', legendLabSize = 10)
  resultsNames(dds)
  head(res)
}

#run_deseq(rnd_countData, metaData, "NOD_ND_HealthyAdult", "NOD_ND_Diabetic", "/Users/matthewbernstein/Development/anna_karenina_beta_cell/results/NOD_ND_HealthyAdult_vs_NOD_ND_Diabetic.csv")
#run_deseq(rnd_countData, metaData, "NOD_ND_Diabetic", "NOD_T1D_Diabetic", "/Users/matthewbernstein/Development/anna_karenina_beta_cell/results/NOD_ND_Diabetic_vs_NOD_T1D_Diabetic.csv")
#run_deseq(rnd_countData, metaData, "NOD_ND_HealthyAdult", "NOD_T1D_Diabetic", "/Users/matthewbernstein/Development/anna_karenina_beta_cell/results/NOD_ND_HealthyAdult_vs_NOD_T1D_Diabetic.csv")
if(do_by_group){
    run_deseq(rnd_countData, metaData, "H9", "CAR", "JueH9_vs_JueCAR_500_ageplusGroup_groupContrast.tsv", 1)
} else{
    run_deseq(rnd_countData, metaData, 1, 0, "JueH9_vs_JueCAR_500_gender_group_byGender2.tsv", 0)
}