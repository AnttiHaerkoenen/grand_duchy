import os
import re
from pathlib import Path

import pandas as pd

from src.tools.utils import text_file_generator, read_word_list


def get_kwic(
        file: Path,
        regex_dict: dict,
        year: int,
        window_size: int,
):
    rows = []

    print(f'Processing file {file.name}')

    text = file.read_text()

    for w, r in regex_dict.items():
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


def get_kwic_all(
        *,
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

    files = []

    for file, year, text in texts:
        kwic = get_kwic(
            file=file,
            regex_dict=regex,
            year=year,
            window_size=window_size,
        )
        files.append(kwic)

    return pd.concat(files, axis=0).sort_values('keyword')


if __name__ == '__main__':
    input_dir = Path('../../data')
    output_dir = Path('../../data/processed/kwic_riksdag')
    wordlist = Path('../../wordlists/wordlist_riksdag.csv')
    bins = Path('../../wordlists/riksdag_bins.csv')

    output_dir.mkdir(parents=True, exist_ok=True)

    kwic = get_kwic_all(
        data=input_dir,
        rule='*.txt',
        wordlist=wordlist,
        window_size=20,
    )

    for word in read_word_list(wordlist):
        print(f'Saving data ({word})')
        word_data = kwic[kwic['keyword'].isin([word])]
        word_data.to_csv(output_dir / f'{word}.csv')
