import os

import pandas as pd
import matplotlib.pyplot as plt
import bokeh


if __name__ == '__main__':
    data = pd.from_csv('../../data/processed/frequencies_riksdag_all.csv')
