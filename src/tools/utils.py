from pathlib import Path

import pandas as pd


def text_file_generator(
        data: str,
        rule: str,
):
    fp = Path(data)
    if not fp.exists():
        raise ValueError(f"Specified data path {str(fp)} does not exist")
    for file in fp.rglob(rule):
        text = file.read_text()
        yield str(file), text


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
