import re
from pathlib import Path
import logging
from typing import Generator

import pandas as pd
from pandas import DataFrame
import nltk
import click


def text_file_generator(
        data_path: Path,
        rule: str,
) -> Generator:
    if isinstance(data_path, str):
        data_path = Path(data_path)

    if not data_path.exists():
        raise FileNotFoundError(f"Specified data path {str(data_path)} does not exist.")

    paths = list(data_path.rglob(rule))
    years = [re.findall(r'\d{4}', path.name)[0] for path in paths]

    for path, year in sorted(zip(paths, years), key=lambda x: x[1]):
        text = path.read_text()
        yield path, year, text


def read_word_list(file):
    data = pd.read_csv(str(file), header=None)
    data.columns = 'word regex'.split()
    data.dropna(inplace=True)
    data.sort_values(by='word', inplace=True)

    words = data['word']
    regex = data['regex']

    return {w.casefold(): r for w, r in zip(words, regex)}


def retry(retries=10, timeout=5):
    def wraps(f):
        def inner(*args, **kwargs):
            for i in range(retries):
                if i > 0:
                    logging.info(f'Retrying, attempt {i}')
                try:
                    result = f(*args, **kwargs)
                except Exception as e:
                    logging.error(f'Unknown error: {e}')
                    time.sleep(timeout + i * 10)
                    continue
                else:
                    return result
            else:
                logging.critical("Operation failed.")
        return inner
    return wraps


@retry(5, 1)
def get_frequency(
        data: str,
        rule: str,
        wordlist: Path,
) -> DataFrame:
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


@retry()
def get_frequency_by_year(
        data,
        bins_file: Path,
        wordlist: Path,
) -> DataFrame:
    frequencies = []
    bins = pd.read_csv(bins_file)

    for year, bin in bins.itertuples(index=False):
        logging.debug(f'Processing year {year}')

        freq = get_frequency(
            data=data,
            rule=f"*_{bin}_*.txt",
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
    result = result.rename(columns=lambda w: w.replace(' ', '_') if w != 'Unnamed: 0' else w)

    return result


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
@click.argument('wordlist_filepath', type=click.Path(exists=True))
@click.argument('bins_filepath', type=click.Path(exists=True))
def main(
    input_filepath, 
    output_filepath, 
    wordlist_filepath,
    bins_filepath,
    ) -> None:
    """
    Performs absolute and relative word frequency analysis and saves results in csv files
    """
    logger = logging.getLogger(__name__)
    input_fp = Path(input_filepath)
    output_fp = Path(output_filepath)
    output_fp.mkdir(exist_ok=True)
    wordlist_fp = Path(wordlist_filepath)
    bins_fp = Path(bins_filepath)

    absolutes = get_frequency_by_year(
        data=input_fp,
        bins_file=bins_fp,
        wordlist=wordlist_fp,
    )
    words = absolutes['words']
    absolutes.to_csv(output_fp / 'all_abs.csv')
    freq = absolutes.drop(columns=['year', 'words'])
    freq = freq[freq.columns].div(words, axis='index') * 100_000
    freq['year'] = absolutes['year']
    freq.to_csv(output_fp / 'all_rel.csv')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
