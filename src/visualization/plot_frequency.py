import os

import pandas as pd
import matplotlib.pyplot as plt
import bokeh


if __name__ == '__main__':
    data = pd.read_csv('../../data/processed/frequencies_riksdag_all.csv')
    data.plot(x='year', title="Frequency / 100 000 words")
    plt.savefig(fname='storfurste_freq')
