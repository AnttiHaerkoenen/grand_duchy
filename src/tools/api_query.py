from pathlib import Path

import pandas as pd
import requests
from requests.exceptions import ConnectionError, HTTPError

from src.tools.utils import read_word_list
from src.tools.exceptions import EmptyDataFrameError

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/53.0.2785.143 Safari/537.36',
}


def combine_regex_and_lemma_df(
        *,
        lemma_df: pd.DataFrame,
        regex_df: pd.DataFrame,
):
    if lemma_df.empty and regex_df.empty:
        raise EmptyDataFrameError

    if lemma_df.empty:
        regex_df.set_index('url', inplace=True)
        regex_df['type'] = ['regex'] * len(regex_df.index)
        regex_df.reset_index(inplace=True)

        return regex_df

    if regex_df.empty:
        lemma_df.set_index('url', inplace=True)
        lemma_df['type'] = ['lemma'] * len(lemma_df.index)
        lemma_df.reset_index(inplace=True)

        return lemma_df

    lemma_df.set_index('url', inplace=True)
    regex_df.set_index('url', inplace=True)

    duplicates_idx = lemma_df.index.intersection(regex_df.index)
    only_lemma_idx = lemma_df.index.difference(duplicates_idx)
    only_regex_idx = regex_df.index.difference(duplicates_idx)

    duplicates = lemma_df.loc[duplicates_idx]
    only_lemma = lemma_df.loc[only_lemma_idx]
    only_regex = regex_df.loc[only_regex_idx]

    duplicates['type'] = ['both'] * len(duplicates_idx)
    only_lemma['type'] = ['lemma'] * len(only_lemma_idx)
    only_regex['type'] = ['regex'] * len(only_regex_idx)

    data = pd.concat([duplicates, only_regex, only_lemma])
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'url'}, inplace=True)

    return data


def make_request(
        url,
        query_params,
        retries=10,
        timeout=120,
):
    print(f"Making query {query_params.get('cqp', query_params)}")

    for i in range(1, retries + 1):
        print(f"Attempt {i}")
        try:
            req = requests.get(
                url=url,
                timeout=timeout * i,
                headers=HEADERS,
                params=query_params,
            )
            req.raise_for_status()
            print("Success!")
            return req.json()
        except ConnectionError as e:
            print(f"Connection error: {e}")
            continue
        except HTTPError as e:
            print(f"HTTP Error: {e}")
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
        try:
            context = ' '.join([w['word'] for w in hit['tokens']])
        except TypeError:
            context = ''

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
    data_totals = data_totals.rename(columns=lambda w: w.replace(' ', '_') if w != 'Unnamed: 0' else w)

    data_lemma_relative = data_lemma.div(data_totals, axis=0) * 100_000
    data_regex_relative = data_regex.div(data_totals, axis=0) * 100_000

    data_lemma['year'] = data_lemma.index
    data_regex['year'] = data_regex.index
    data_lemma_relative['year'] = data_lemma_relative.index
    data_regex_relative['year'] = data_regex_relative.index

    data_lemma.to_csv(output_dir / 'lemma_abs.csv')
    data_regex.to_csv(output_dir / 'regex_abs.csv')
    data_lemma_relative.to_csv(output_dir / 'lemma_rel.csv')
    data_regex_relative.to_csv(output_dir / 'regex_rel.csv')


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

        kwic_lemma = pd.DataFrame.from_dict(kwic_lemma).drop_duplicates('url')

        _, kwic_regex = query(
            word=word,
            regex=regex,
            url=korp_url,
            corpora=corpora,
            use_lemma=False,
            **params
        )

        kwic_regex = pd.DataFrame.from_dict(kwic_regex).drop_duplicates('url')

        try:
            kwic_data = combine_regex_and_lemma_df(
                regex_df=kwic_regex,
                lemma_df=kwic_lemma,
            )
            kwic_data.to_csv(output_dir / f'{word}.csv')
        except EmptyDataFrameError:
            print(f'No data to save for {word}.')


if __name__ == '__main__':
    wordlist_dir = Path('../../wordlists')
    output_dir = Path.home() / 'gd_data/processed'

    words = read_word_list(wordlist_dir / 'wordlist_fi_newspapers.csv')

    years = range(1820, 1911)
    corpora = {y: f"KLK_FI_{y}" for y in years if y not in (1828, 1843)}

    # print("Test run:")
    # freq, kwic = query(
    #     word='keisari',
    #     regex='(K|k)eisar.+',
    #     url='https://korp.csc.fi/cgi-bin/korp.cgi',
    #     corpora=corpora,
    #     use_lemma=True,
    # )

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
        output_dir=Path('../../data/processed') / 'frequencies_fi_newspapers',
        korp_url='https://korp.csc.fi/cgi-bin/korp.cgi',
        corpora=corpora,
    )
