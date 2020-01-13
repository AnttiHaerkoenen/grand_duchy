import re

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
                    'file': file,
                    'year': year,
                    'keyword': w,
                    'context': context,
                }
                rows.append(row)

    return pd.DataFrame(rows).sort_values('keyword')


if __name__ == '__main__':
    data = '../../data/raw/'
    words = '../../wordlists/wordlist_riksdag.csv'
    bins = '../../wordlists/riksdag_bins.csv'

    kwic = get_kwic(
        data=data,
        rule='*.txt',
        wordlist=words,
        window_size=150,
    )

    for word in read_word_list(words):
        kwic[kwic['keyword'].isin([word])].to_csv(f'../../data/processed/kwic_riksdag_{word}.csv')
