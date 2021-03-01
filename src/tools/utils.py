from collections.abc import Generator
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
                    print(f'Retrying, attempt {i}')
                try:
                    result = f(*args, **kwargs)
                except Exception as e:
                    print(f'Unknown error: {e}')
                    time.sleep(timeout + i * 10)
                    continue
                else:
                    return result
            else:
                print("Operation failed.")
        return inner
    return wraps


if __name__ == '__main__':
    DATA = Path.home() / 'gd_data/external/'
    texts = text_file_generator(DATA, 'roa*.txt')
    print([(p, y) for p, y, _ in texts])
