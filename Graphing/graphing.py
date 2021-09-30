import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


if __name__ == '__main__':
    data = pd.read_csv("Graphing/plotdata", index_col=0)
    # data.index = ['Actual', 'Time-Reversal', 'Inter-Event Shuffling']

    ax = sns.heatmap(data, square=True, norm=LogNorm(), cmap="YlGnBu")
    ax.set_ylim(3, -0.5)
    ax.set_xlim()
    plt.title('MovieLens Actual vs. RRM Results at dc=2x(t)')
    plt.savefig('Graphing/test.png', bbox_inches='tight')
