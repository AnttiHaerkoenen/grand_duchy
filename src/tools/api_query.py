from pathlib import Path
import time
import logging

import pandas as pd
import requests
from requests.exceptions import ConnectionError, HTTPError
import click

from utils import read_word_list, retry
from exceptions import EmptyDataFrameError

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/53.0.2785.143 Safari/537.36',
}


def combine_regex_and_lemma_df(
        *,
        lemma_df: pd.DataFrame,
        regex_df: pd.DataFrame,
) -> pd.DataFrame:
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
        logger: logging.Logger,
        retries=10,
        timeout=120,
):
    logger.info(f"Making query {query_params.get('cqp', query_params)}")

    for i in range(1, retries + 1):
        logger.info(f"Attempt {i}")
        try:
            req = requests.get(
                url=url,
                timeout=timeout * i,
                headers=HEADERS,
                params=query_params,
            )
            req.raise_for_status()
            logger.info("Success!")
            return req.json()
        except ConnectionError as e:
            logger.exception(f"Connection Error: {e}")
            continue
        except HTTPError as e:
            logger.exception(f"HTTP Error: {e}")
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
        logger: logging.Logger,
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

    result = make_request(url=url, query_params=query_params, logger=logger)

    freq = pd.Series({y: result['corpus_hits'].get(c, None) for y, c in corpora.items()})

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
        logger: logging.Logger,
):
    query_params = {
        'command': 'info',
        'corpus': ','.join(corpora.values()),
    }

    result = make_request(
        url=url,
        query_params=query_params,
        logger=logger,
    )
    corpora_info = result['corpora']

    flipped_corpora = {v: k for k, v in corpora.items()}
    totals = {
        flipped_corpora.get(c, None): int(v['info']['Size'])
        for c, v
        in corpora_info.items()
    }

    return totals


@retry()
def get_and_save_results(
        regex_dict: dict,
        output_fp: Path,
        korp_url: str,
        corpora: dict,
        kwic_or_freq: str,
        logger: logging.Logger,
        **params,
) -> None:
    output_fp.mkdir(parents=True, exist_ok=True)

    freq = kwic_or_freq in ("freq", "both")
    kwic = kwic_or_freq in ("kwic", "both")

    freqs_lemma = {}
    freqs_regex = {}

    if kwic:
        kwic_fp = output_fp / "kwic"
        kwic_fp.mkdir(exist_ok=True)
    
    if freq:
        freq_fp = output_fp / "frequencies"
        freq_fp.mkdir(exist_ok=True)

    logger.info("Iterating over words")

    for word, regex in regex_dict.items():
        word = word.casefold()

        logger.info(f"Making query for {word}")

        freq_lemma, kwic_lemma = query(
            word=word,
            regex=regex,
            url=korp_url,
            corpora=corpora,
            use_lemma=True,
            logger=logger,
            **params
        )

        freq_regex, kwic_regex = query(
            word=word,
            regex=regex,
            url=korp_url,
            corpora=corpora,
            use_lemma=False,
            logger=logger,
            **params
        )

        freqs_regex[word] = freq_regex
        freqs_lemma[word] = freq_lemma

        if not kwic:
            continue

        kwic_regex_cleaned = pd.DataFrame.from_dict(kwic_regex).drop_duplicates('url')
        kwic_lemma_cleaned = pd.DataFrame.from_dict(kwic_lemma).drop_duplicates('url')

        logger.info(f"Regex results: {kwic_regex_cleaned.shape[0]}")
        logger.info(f"Lemma results: {kwic_lemma_cleaned.shape[0]}")

        try:
            kwic_data = combine_regex_and_lemma_df(
                regex_df=kwic_regex_cleaned,
                lemma_df=kwic_lemma_cleaned,
            )
            kwic_data.to_csv(kwic_fp / f'{word}.csv')
            logger.info(f'{word} saved to file')
        except EmptyDataFrameError:
            logger.exception(f'No data to save for {word}.')

    if kwic:
        logger.info(f"Keywords-in-context saved to {kwic_fp}")

    if freq:
        data_lemma = pd.DataFrame(freqs_lemma)
        data_regex = pd.DataFrame(freqs_regex)

        data_totals = pd.Series(query_totals(korp_url, corpora, logger=logger)).sort_index()
        # data_totals = data_totals.rename(lambda w: w.replace(' ', '_') if w != 'Unnamed: 0' else w)

        logger.info("Calculating relative frequencies")
        data_lemma_relative = data_lemma.div(data_totals, axis=0) * 100_000
        data_regex_relative = data_regex.div(data_totals, axis=0) * 100_000

        data_lemma['year'] = data_lemma.index
        data_regex['year'] = data_regex.index
        data_lemma_relative['year'] = data_lemma_relative.index
        data_regex_relative['year'] = data_regex_relative.index

        logger.info("Saving frequency data to csv files")
        data_lemma.to_csv(freq_fp / 'lemma_abs.csv')
        data_regex.to_csv(freq_fp / 'regex_abs.csv')
        data_lemma_relative.to_csv(freq_fp / 'lemma_rel.csv')
        data_regex_relative.to_csv(freq_fp / 'regex_rel.csv')
        logger.info(f"Frequencies saved to {freq_fp}")


@click.command()
@click.argument("output_dir", type=click.Path(exists=True))
@click.argument("wordlist_dir", type=click.Path(exists=True))
@click.argument("korp_url", type=click.STRING)
@click.option("--kwic-or-freq", type=click.Choice(['kwic', 'freq', 'both'], case_sensitive=False), default='both')
@click.option("--first-year", type=click.INT, help="first year to search")
@click.option("--last-year", type=click.INT, help="last year to search")
@click.option("-e", "--excluded", type=click.INT, help="excluded years", multiple=True)
def main(output_dir, wordlist_dir, korp_url, kwic_or_freq, first_year, last_year, excluded,):
    """
    Makes lemma or regex queries from korp interface 
    """
    logger = logging.getLogger(__name__)
    output_fp = Path(output_dir)
    wordlist_fp = Path(wordlist_dir)

    logger.info(f"Reading words from {wordlist_dir}")
    words = read_word_list(wordlist_fp / 'wordlist_fi_newspapers.csv')
    words = {k:v for k, v in words.items() if k=="demokratia"}

    years = range(first_year, last_year + 1)
    corpora = {y: f"KLK_FI_{y}" for y in years if y not in excluded}

    get_and_save_results(
        regex_dict=words,
        output_fp=output_fp,
        korp_url=korp_url,
        corpora=corpora,
        kwic_or_freq=kwic_or_freq,
        start=0,
        end=10_000,
        logger=logger,
    )


if __name__ == '__main__':
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
