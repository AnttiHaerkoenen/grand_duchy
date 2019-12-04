import os

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import bokeh


if __name__ == '__main__':
    data = pd.read_csv('../../data/processed/frequencies_riksdag_all_abs.csv')
    fig = data.plot.bar(title="Total number of words", y='words', x='year', figsize=(12, 6))
    fig.yaxis.set_major_formatter(ScalarFormatter())
    fig.ticklabel_format(style='plain', axis='y')
    plt.savefig(fname='../../reports/figures/total_words')
