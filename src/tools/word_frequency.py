import nltk
import re

import pandas as pd

from src.tools.utils import text_file_generator


def get_frequency(
        data: str,
        rule: str,
        words: dict,
):
    texts = text_file_generator(data, rule)
    regex = {word: re.compile(regexpr) for word, regexpr in words.items()}
    rows = []
    for file, text in texts:
        row = {'file': file, 'words': len(text)}
        for w, r in regex.items():
            row[w] = len(r.findall(text))
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == '__main__':
    data = '../../data/raw'
    rule = '*.txt'
    words = {'storfurste': '[Ss]torfurst', 'storfurstedömet': '[Ss]torfurstendöme'}
    freq = get_frequency(
        data=data,
        rule=rule,
        words=words,
    )
    print(freq.sort_values(by='storfurstedömet'))
    print(freq.sum())
