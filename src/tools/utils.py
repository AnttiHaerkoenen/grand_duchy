from collections import Generator
from pathlib import Path
import re

import pandas as pd


def text_file_generator(
        data_path: Path,
        rule: str,
) -> Generator:
    if isinstance(data_path, str):
        data_path = Path(data_path)

    if not data_path.exists():
        raise FileNotFoundError(f"Specified data path {str(data_path)} does not exist.")

    for path in data_path.rglob(rule):
        text = path.read_text()
        year = re.findall(r'\d{4}', path.name)[0]

        yield path, year, text


def read_word_list(file):
    data = pd.read_csv(str(file), header=None)
    data.columns = 'word regex'.split()
    data.dropna(inplace=True)
    data.sort_values(by='word', inplace=True)

    words = data['word']
    regex = data['regex']

    return {w.casefold(): r for w, r in zip(words, regex)}


if __name__ == '__main__':
    DATA = '../../data/raw'
    texts = sorted(text_file_generator(DATA, 'roa_1809*.txt'))
    print(len(texts))
