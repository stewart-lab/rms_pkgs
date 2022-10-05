#Import gene expression data to DESeq2 to analyze RNAseq with different visualization tools
#Make sure to edit "GROUP" in metaData based on clustering from dendrogram
#Run this before Venn diagram and volcano plot
library("DESeq2")
library("ggplot2")
library("EnhancedVolcano")

#Use raw data
countData <- read.csv("/Users/matthewbernstein/Development/anna_karenina_beta_cell/data_for_DESeq2/Raw_Matrix_filter_rmDup.NOD_comparison.csv", header = TRUE, sep = ",")
head(countData)

#metaData without E13.5 samples, separate diabetic group into T1D and T2D
metaData <- read.csv("/Users/matthewbernstein/Development/anna_karenina_beta_cell/data_for_DESeq2/AKP_Metadata_v2.NOD_comparison.csv", header = TRUE, sep = ",")

head(metaData)

# Round the data
rnd <- function(x) trunc(x+sign(x)*0.5)
rnd_countData <- rnd(countData[,-1])
rnd_countData <- data.frame(GENE_ID = countData[,1],rnd_countData)

#Converting design variables into factors (not necessary)
metaData$NOD_GROUP <- as.factor(metaData$NOD_GROUP)
metaData$COND <- as.factor(metaData$COND)
metaData$BATCH <- as.factor(metaData$BATCH)

run_deseq <- function(counts_mtx, meta_data, cond1, cond2, out_f) {
  dds <- DESeqDataSetFromMatrix(
    countData=counts_mtx, 
    colData=meta_data, 
    design=~NOD_GROUP, 
    tidy = TRUE
  )
  keep <- rowSums(counts(dds) >= 2) > 5
  dds <- dds[keep,]
  dds$NOD_GROUP <- relevel(dds$NOD_GROUP, ref = cond1)
  dds <- DESeq(dds)
  res <- results(dds)
  head(results(dds, tidy=TRUE))
  res <- results(dds, contrast=c("NOD_GROUP",cond1, cond2))
  res <- lfcShrink(dds, contrast=c("NOD_GROUP",cond1, cond2), res = res, type = "ashr")
  write.csv(res, out_f)
  EnhancedVolcano(res, lab = rownames(res), x = "log2FoldChange", y = "pvalue", xlim = c(-10,10), axisLabSize = 12, title = "", subtitle = "", captionLabSize = 8, pCutoff = 0.05, FCcutoff = 1.5, pointSize = 3.0, labFace = "bold", labSize = 3.0, legendPosition = 'none', legendLabSize = 10)

}

#run_deseq(rnd_countData, metaData, "NOD_ND_HealthyAdult", "NOD_ND_Diabetic", "/Users/matthewbernstein/Development/anna_karenina_beta_cell/results/NOD_ND_HealthyAdult_vs_NOD_ND_Diabetic.csv")
#run_deseq(rnd_countData, metaData, "NOD_ND_Diabetic", "NOD_T1D_Diabetic", "/Users/matthewbernstein/Development/anna_karenina_beta_cell/results/NOD_ND_Diabetic_vs_NOD_T1D_Diabetic.csv")
run_deseq(rnd_countData, metaData, "NOD_ND_HealthyAdult", "NOD_T1D_Diabetic", "/Users/matthewbernstein/Development/anna_karenina_beta_cell/results/NOD_ND_HealthyAdult_vs_NOD_T1D_Diabetic.csv")