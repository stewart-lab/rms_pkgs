import seaborn as sns
import sys
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

in_f = sys.argv[1]

df = pd.read_csv(in_f, sep='\t', index_col=0)

#ax = sns.heatmap(df, annot=True) 
#bottom, top = ax.get_ylim()
#ax.set_ylim(bottom + 0.5, top - 0.5)

sns.heatmap(df, annot=np.array(df), cmap='viridis', square=True )

plt.show()

