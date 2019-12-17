from pathlib import Path
import re

import pandas as pd


def text_file_generator(
        data: str,
        rule: str,
):
    fp = Path(data)

    if not fp.exists():
        raise ValueError(f"Specified data path {str(fp)} does not exist")

    for path in fp.rglob(rule):
        text = path.read_text()
        year = re.findall(r'\d{4}', path.name)[0]
        yield str(path), year, text


def read_word_list(file):
    data = pd.read_csv(file, header=None)
    data.columns = 'word regex'.split()
    words = data['word']
    regex = data['regex']
    return {w: r for w, r in zip(words, regex)}


if __name__ == '__main__':
    DATA = '../../data/raw'
    texts = sorted(text_file_generator(DATA, 'roa_1809*.txt'))
    print(len(texts))
