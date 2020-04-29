from pathlib import Path
import re

import pandas as pd
import requests
from requests.exceptions import ReadTimeout, HTTPError

from src.tools.utils import read_word_list

TIMEOUT = 60
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/53.0.2785.143 Safari/537.36',
}


def make_request(
        url,
        query_params,
):
    print(f"Making query {query_params.get('cqp', query_params)}")

    for i in range(1, 6):
        print(f"Attempt {i}")

        try:
            timeout = TIMEOUT * i

            req = requests.get(
                url=url,
                timeout=timeout,
                headers=HEADERS,
                params=query_params,
            )
            req.raise_for_status()
            print("Success!")
            return req.json()

        except ReadTimeout:
            print("Read timed out")
            continue

        except HTTPError:
            print("HTTP Error")
            continue

    return {
        'corpus_hits': {},
        'kwic': [],
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

    structs = 'text_binding_id text_issue_date text_issue_no ' \
              'text_page_no text_publ_title text_publ_type'.split()

    query_params = {
        'command': 'query',
        'start': start,
        'end': end,
        'show_struct': ','.join(structs),
        'corpus': ','.join(corpora.values()),
    }

    if use_lemma:
        query_params['cqp'] = f'[lemma="{word}"]'
    else:
        query_params['cqp'] = f'[word="{regex}"]'

    result = make_request(url=url, query_params=query_params)

    freq = {y: result['corpus_hits'].get(c, None) for y, c in corpora.items()}

    kwic = []
    for hit in result['kwic']:
        context = ' '.join([w['word'] for w in hit['tokens']])
        hit_data = hit.get('structs', dict())

        text_type = hit_data.get('text_publ_type', None)
        publication = hit_data.get('text_publ_title', None)
        text_binding_id = hit_data.get('text_binding_id', None)
        page = hit_data.get('text_page_no', 0)

        url = f'{text_type}/binding/{text_binding_id}?term={word}&page={page}'

        year = hit_data.get('text_issue_date', '').split('.')[-1]
        if len(year) != 4:
            year = hit.get('corpus')[-4:]

        kwic.append({
            'publication': publication,
            'corpus': hit.get('corpus', None),
            'context': context,
            'url': url,
            'year': int(year),
        })

    return freq, kwic


def query_totals(
        url: str,
        corpora: dict,
):
    query_params = {
        'command': 'info',
        'corpus': ','.join(corpora.values()),
    }

    result = make_request(
        url=url,
        query_params=query_params,
    )
    corpora_info = result['corpora']

    flipped_corpora = {v: k for k, v in corpora.items()}
    totals = {
        flipped_corpora.get(c, None): int(v['info']['Size'])
        for c, v
        in corpora_info.items()
    }

    return totals


def save_frequencies(
        regex_dict: dict,
        output_dir: Path,
        korp_url: str,
        corpora: dict,
        **params,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

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

    data_totals = pd.Series(query_totals(korp_url, corpora)).sort_index()

    data_lemma_relative = data_lemma.div(data_totals, axis=0) * 100_000
    data_regex_relative = data_regex.div(data_totals, axis=0) * 100_000

    data_lemma['year'] = data_lemma.index
    data_regex['year'] = data_regex.index
    data_lemma_relative['year'] = data_lemma_relative.index
    data_regex_relative['year'] = data_regex_relative.index

    data_lemma.to_csv(output_dir / 'frequencies_fi_newspapers_lemma_abs.csv')
    data_regex.to_csv(output_dir / 'frequencies_fi_newspapers_regex_abs.csv')
    data_lemma_relative.to_csv(output_dir / 'frequencies_fi_newspapers_lemma.csv')
    data_regex_relative.to_csv(output_dir / 'frequencies_fi_newspapers_regex.csv')


def save_kwics(
        regex_dict: dict,
        output_dir: Path,
        korp_url: str,
        corpora: dict,
        **params,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for word, regex in regex_dict.items():
        word = word.casefold()

        _, kwic_lemma = query(
            word=word,
            regex=regex,
            url=korp_url,
            corpora=corpora,
            use_lemma=True,
            **params
        )

        kwic_lemma = pd.DataFrame.from_dict(kwic_lemma)
        kwic_lemma.to_csv(output_dir / f'{word}_lemma.csv')

        _, kwic_regex = query(
            word=word,
            regex=regex,
            url=korp_url,
            corpora=corpora,
            use_lemma=False,
            **params
        )

        kwic_regex = pd.DataFrame.from_dict(kwic_regex)
        kwic_regex.to_csv(output_dir / f'{word}_regex.csv')


if __name__ == '__main__':
    wordlist_dir = Path('../../wordlists')
    output_dir = Path('../../data/processed')

    words = read_word_list(wordlist_dir / 'wordlist_fi_newspapers.csv')

    years = range(1820, 1911)
    corpora = {y: f"KLK_FI_{y}" for y in years if y not in (1828, 1843)}

    freq, kwic = query(
        word='keisari',
        regex='(K|k)eisar.+',
        url='https://korp.csc.fi/cgi-bin/korp.cgi',
        corpora=corpora,
        use_lemma=True,
    )

    save_kwics(
        regex_dict=words,
        output_dir=output_dir / 'kwic_fi_newspapers',
        korp_url='https://korp.csc.fi/cgi-bin/korp.cgi',
        corpora=corpora,
        start=0,
        end=10_000,
    )

    save_frequencies(
        regex_dict=words,
        output_dir=output_dir,
        korp_url='https://korp.csc.fi/cgi-bin/korp.cgi',
        corpora=corpora,
        start=0,
        end=10,
    )
