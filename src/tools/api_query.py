from pathlib import Path
import re

import pandas as pd
import requests

from src.tools.utils import read_word_list

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/53.0.2785.143 Safari/537.36',
}


def query(
        word: str,
        regex: str,
        url: str,
        corpora: dict,
        start: int = 0,
        end: int = 10,
        use_lemma: bool = True,
) -> tuple:

    query_params = {
        'command': 'query',
        'start': start,
        'end': end,
        'corpus': ','.join(corpora.values()),
    }

    if use_lemma:
        query_params['cqp'] = f'[lemma="{word}"]'
    else:
        query_params['cqp'] = f'[word="{regex}"]'

    req = requests.get(
        url,
        headers=headers,
        timeout=60,
        params=query_params,
    )
    result = req.json()

    freq = {y: result['corpus_hits'].get(c, None) for y, c in corpora.items()}

    kwic = {}
    for hit in result['kwic']:
        context = ' '.join([w['word'] for w in hit['tokens']])
        kwic[hit['corpus']] = context

    return freq, kwic


def save_frequencies(
        regex_dict: dict,
        output_dir: Path,
        korp_url: str,
        corpora: dict,
        **params,
) -> None:

    freqs_lemma = {}
    freqs_regex = {}

    for word, regex in regex_dict.items():
        word = word.casefold()

        freq_lemma, _ = query(
            word=word,
            regex=regex,
            url=korp_url,
            corpora=corpora,
            use_lemma=True,
            **params
        )

        freqs_lemma[word] = freq_lemma

        freq_regex, _ = query(
            word=word,
            regex=regex,
            url=korp_url,
            corpora=corpora,
            use_lemma=False,
            **params
        )

        freqs_regex[word] = freq_regex

    data_lemma = pd.DataFrame.from_dict(freqs_lemma)
    data_regex = pd.DataFrame.from_dict(freqs_regex)

    data_lemma.to_csv(output_dir / 'frequencies_FI_newspapers_lemma.csv')
    data_regex.to_csv(output_dir / 'frequencies_FI_newspapers_regex.csv')


if __name__ == '__main__':
    wordlist_dir = Path('../../wordlists')
    output_dir = Path('../../data/processed')

    words = read_word_list(wordlist_dir / 'wordlist_FI_newspapers.csv')

    years = range(1820, 1911)
    corpora = {y: f"KLK_FI_{y}" for y in years if y not in (1828, 1843)}

    freq, kwic = query(
        word='keisari',
        regex='(K|k)eisar.+',
        url='https://korp.csc.fi/cgi-bin/korp.cgi',
        corpora=corpora,
        use_lemma=False,
    )

    save_frequencies(
        regex_dict=words,
        output_dir=output_dir,
        korp_url='https://korp.csc.fi/cgi-bin/korp.cgi',
        corpora=corpora,
    )
