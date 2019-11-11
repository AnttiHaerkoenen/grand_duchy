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
    regex = {word: re.compile(regexpr, flags=re.IGNORECASE) for word, regexpr in words.items()}
    rows = []
    for file, text in texts:
        row = {'file': file, 'words': len(text)}
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
    bins = pd.read_csv(bins_file)['year']
    for b in bins:
        freq = get_frequency(
            data=data,
            rule=f"*{b}*.txt",
            wordlist=wordlist,
        )
        if freq.empty:
            continue
        freq = freq.drop(columns=['file'])
        freq = freq.sum()
        freq.name = b
        frequencies.append(freq)
    return pd.concat(frequencies, axis=1).T


if __name__ == '__main__':
    data = '../../data/raw/'
    rule = '*.txt'
    words = '../../wordlists/wordlist_riksdag.csv'
    bins = '../../wordlists/riksdag_bins.csv'
    freq = get_frequency_by_year(
        data=data,
        bins_file=bins,
        wordlist=words,
    )
    freq.to_csv('../../data/processed/frequencies_riksdag_all.csv')
    print(freq.sum())
