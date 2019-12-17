import nltk
import re

import pandas as pd

from src.tools.utils import text_file_generator, read_word_list


def get_frequency(
        data: str,
        rule: str,
        wordlist: str,
):
    texts = text_file_generator(data, rule)
    words = read_word_list(wordlist)
    regex = {
        word: re.compile(regexpr, flags=re.IGNORECASE)
        for word, regexpr
        in words.items()
    }
    rows = []
    for file, _, text in texts:
        row = {
            'file': file,
            'words': len(re.findall(r'\w+', text))
        }
        for w, r in regex.items():
            row[w] = len(r.findall(text))
        rows.append(row)
    return pd.DataFrame(rows)


def get_frequency_by_year(
        data: str,
        bins_file: str,
        wordlist: str,
):
    frequencies = []
    bins = pd.read_csv(bins_file)
    for year, bin in bins.itertuples(index=False):
        freq = get_frequency(
            data=data,
            rule=f"*{bin}*.txt",
            wordlist=wordlist,
        )

        if freq.empty:
            continue

        freq = freq.drop(columns=['file'])
        freq = freq.sum()

        freq.name = bin
        freq['year'] = year
        frequencies.append(freq)

    result = pd.concat(frequencies, axis=1).T
    return result


if __name__ == '__main__':
    data = '../../data/raw/'
    words = '../../wordlists/wordlist_riksdag.csv'
    bins = '../../wordlists/riksdag_bins.csv'

    abs = get_frequency_by_year(
        data=data,
        bins_file=bins,
        wordlist=words,
    )

    words = abs['words']
    abs.to_csv('../../data/processed/frequencies_riksdag_all_abs.csv')
    freq = abs.drop(columns=['year', 'words'])
    freq = freq[freq.columns].div(words, axis='index') * 100_000
    freq['year'] = abs['year']
    freq.to_csv('../../data/processed/frequencies_riksdag_all.csv')
