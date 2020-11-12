import os
import re
from pathlib import Path
from typing import Callable

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


def get_kwic_for_word(
        *,
        data: Path,
        rule: str,
        term: str,
        regex: re.Pattern,
        window_size: int,
        size_limit: int,
):
    texts = text_file_generator(data, rule)

    print(f'Reading data for {term}')

    rows = []

    for file, year, text in texts:

        if len(rows) >= size_limit:
            break

        matches = regex.finditer(text)

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
                'keyword': term,
                'context': context,
            }

            rows.append(row)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame.from_records(rows).sort_values('year').head(size_limit).reset_index()


def save_kwic_by_word(
        *,
        input_dir: Path,
        output_dir: Path,
        rule: str,
        wordlist: str,
        window_size: int,
        size_limit: int,
        word_filter_rule: Callable[[str], bool],
):
    output_dir.mkdir(parents=True, exist_ok=True)
    words = read_word_list(wordlist)

    regex = {
        word: re.compile(regexpr, flags=re.IGNORECASE)
        for word, regexpr
        in words.items()
    }

    for term, regex in regex.items():
        if not word_filter_rule(term):
            continue

        kwic_term = get_kwic_for_word(
            data=input_dir,
            rule=rule,
            term=term,
            regex=regex,
            window_size=window_size,
            size_limit=size_limit,
        )
        kwic_term.to_csv(output_dir / f"{term.replace(' ', '_')}.csv")


def get_kwic_all(
        *,
        data: Path,
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

    return pd.concat(files, axis=0).sort_values('keyword').reset_index()


if __name__ == '__main__':
    input_dir = Path.home() / 'gd_data/external/'
    output_dir = Path.home() / 'gd_data/processed/kwic_sv_riksdag'
    wordlist = Path('../../wordlists/wordlist_sv_riksdag.csv')
    rule = '*.txt'

    save_kwic_by_word(
        output_dir=output_dir,
        input_dir=input_dir,
        rule=rule,
        wordlist=wordlist,
        window_size=300,
        size_limit=2000,
        word_filter_rule=lambda w: w in ("karelen", "k a r e l e n"),
    )
