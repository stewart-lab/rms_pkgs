#!/usr/bin/env python
#Computes AUCROC and other statistics, given an input file in csv format:
#   1 header line: postive,drug,cosine_similarity
#   example line:  True,iressa,0.558
#   example line:  False,pancreatin,0.453
#   basically, I'm not currently using the second entry, so the format is really 1 or 0 (or True or False)\tANYTHING\tSomeNumericScore
import os.path
import numpy as np
import cmdlogtime
# we're going to look at ROC here
from sklearn.metrics import roc_curve, average_precision_score, auc, precision_recall_curve
import matplotlib.pyplot as plt

try:
    from inspect import signature
except ImportError:
    from sklearn.externals.funcsigs import signature
    
COMMAND_LINE_DEF_FILE = "./computeROCcommandLine.txt"
def main():
	(start_time_secs, pretty_start_time, my_args, addl_logfile) = cmdlogtime.begin(COMMAND_LINE_DEF_FILE)   
	outdir  = my_args["out_dir"]
	infile = my_args["infile"]
	print_every_x_threshold = my_args["print_every_x_threshold"]
	addl_logfile.write("Starting computeROC")
	#read in input File
	ctr = 0
	tfs = []
	pred_vals = []
	trues = 0
	falses = 0
	with open(infile) as tf_calls_file:
		for line in tf_calls_file:
			ctr = ctr + 1
			if (ctr == 1):
				continue
			results = line.strip().split("\t")  
			#print (line)
			if (results[0] == "True" or results[0] == "1"):
				tfs.append(1)
				trues = trues + 1
			else:
				tfs.append(0)
				falses = falses + 1
			#if (ctr > 2):	
			#	pred_vals.append(0.5)
			#else:
			#	pred_vals.append(0.2)
			pred_vals.append(float(results[2]))
	# get the ROC
	fpr,tpr, thresholds = roc_curve(tfs, pred_vals, pos_label=1)
	roc_auc = auc(fpr, tpr)
	# get the Avg Precision
	ap = average_precision_score(tfs, pred_vals, average='micro')
	addl_logfile.write('')
	addl_logfile.write('ROC AUC: {0}'.format(roc_auc))
	addl_logfile.write('Avg Precision: {0}'.format(ap))
	addl_logfile.write('Trues:' + str(trues))
	addl_logfile.write('Falses:' + str(falses))
	# make ROC plot
	plt.xlabel("False Positive Rate")
	plt.ylabel("True Positive Rate")
	plt.ylim([0.0, 1.05])
	plt.xlim([0.0, 1.0])
	plt.title("ROC curve: AUCROC={0:0.2f}".format(roc_auc))	
	plt.plot(fpr, tpr, linestyle='--', label="ROC")
	plt.plot([0, 1], [0, 1], 'r--', label="Random")
	plt.legend(loc="lower right")
	plt.grid(True)
	# plot some thresholds on the ROC plot # RMS make this a function
	thresholdsLength = len(thresholds)
	colorMap=plt.get_cmap('jet', thresholdsLength)
	for i in range(0, thresholdsLength, 1):
	    threshold_value_with_max_four_decimals = str(thresholds[i])[:5]
	    if i % print_every_x_threshold == 0:
	        plt.text(fpr[i] - 0.03, 
	            tpr[i] + 0.005, 
	            threshold_value_with_max_four_decimals, 
	            fontdict={'size': 5}, 
	            color=colorMap(i/thresholdsLength));
	roc_suffix = "_xxx_"
	roc_fig_local = "./roc_curve_" + roc_suffix + "_.pdf"
	roc_fig_local = os.path.join(outdir, roc_fig_local)
	addl_logfile.write(roc_fig_local)
	plt.savefig(roc_fig_local)
	plt.clf()
	plt.cla()
	plt.close()
	# Make a PR plot
	precision, recall, thresholds = precision_recall_curve(tfs, pred_vals)
	precision_at_recall_1 = trues/(trues + falses) # Can calculate based on TP/Total
	# In matplotlib < 1.5, plt.fill_between does not have a 'step' argument
	step_kwargs = ({"step": "post"} if "step" in signature(plt.fill_between).parameters else {})
	plt.step(recall, precision, color="b", alpha=0.2, where="post")
	plt.fill_between(recall, precision, alpha=0.2, color="b", **step_kwargs)
	plt.xlabel("Recall")
	plt.ylabel("Precision")
	plt.ylim([0.0, 1.05])
	plt.xlim([0.0, 1.0])
	plt.title("2-class Precision-Recall curve: AP={0:0.2f}, P@R1={1:0.2f}".format(ap, precision_at_recall_1))
	plt.axhline(y=precision_at_recall_1,color='gray',linestyle='--')
	plt.grid(True)
	# plot some thresholds on the PR plot # RMS make this a function
	thresholdsLength = len(thresholds)
	colorMap=plt.get_cmap('jet', thresholdsLength)
	for i in range(0, thresholdsLength, 1):
	    threshold_value_with_max_four_decimals = str(thresholds[i])[:5]
	    if i % print_every_x_threshold == 0:
	        plt.text(recall[i] - 0.03, 
	            precision[i] + 0.005, 
	            threshold_value_with_max_four_decimals, 
	            fontdict={'size': 5}, 
	            color=colorMap(i/thresholdsLength));
	pr_suffix = "_xxx_"
	pr_fig_local = "./pr_curve_" + pr_suffix + "_.pdf"
	pr_fig_local = os.path.join(outdir, pr_fig_local)
	addl_logfile.write(pr_fig_local)
	plt.savefig(pr_fig_local)
	plt.clf()
	plt.cla()
	plt.close()
	cmdlogtime.end(addl_logfile, start_time_secs)
	
if __name__ == "__main__":
    main()