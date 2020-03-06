import os
import re
from pathlib import Path

import pandas as pd

from src.tools.utils import text_file_generator, read_word_list


def get_kwic(
        data: str,
        rule: str,
        wordlist: str,
        window_size: int,
):
    texts = text_file_generator(data, rule)
    words = read_word_list(wordlist)

    regex = {
        word: re.compile(regexpr, flags=re.IGNORECASE)
        for word, regexpr
        in words.items()
    }

    rows = []

    for file, year, text in texts:
        print(f'Processing file {file.name}')

        for w, r in regex.items():
            matches = r.finditer(text)

            for m in matches:
                start, end = m.span()
                start = start - window_size
                if start < 0:
                    start = 0

                end = end + window_size

                if end >= len(text):
                    end = len(text) - 1

                context = text[start:end].replace('\n', ' ')
                row = {
                    'file': file.stem,
                    'year': year,
                    'keyword': w,
                    'context': context,
                }
                rows.append(row)

    return pd.DataFrame(rows).sort_values('keyword')


if __name__ == '__main__':
    data = Path('../../data')
    words = Path('../../wordlists/wordlist_riksdag.csv')
    bins = Path('../../wordlists/riksdag_bins.csv')

    kwic = get_kwic(
        data=data,
        rule='*.txt',
        wordlist=words,
        window_size=50,
    )

    for word in read_word_list(words):
        print(f'Saving data ({word})')
        word_data = kwic[kwic['keyword'].isin([word])]
        word_data.to_csv(data / 'processed' / f'kwic_riksdag_{word}.csv')
