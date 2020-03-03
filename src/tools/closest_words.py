from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd
import gensim


def get_closest_words(
        *,
        models: Mapping,
        words: Iterable,
        min_similarity: float = 0,
        max_n: int = 10,
) -> dict:
    results = {w: {} for w in words}

    for name, model in models.items():
        for w in words:
            print(f"Analysing word '{w}' ({name})")
            if w in model.wv:
                closest = model.wv.most_similar(w, topn=max_n)
                results[w][name] = [t for t in closest if t[1] >= min_similarity]

    return results


def make_closest_words_table(
        word_data: Mapping,
) -> pd.DataFrame:
    words = [
        pd.DataFrame.from_records(
            data,
            columns=[model, model + '_d']
        )
        for model, data
        in word_data.items()
    ]

    df = pd.concat(
        words,
        axis=1,
        sort=False,
    )

    df = df.applymap(lambda e: round(e, 3) if isinstance(e, float) else e)

    return df


def make_close_words_lists(
        input_file: Path,
        input_column: str,
        output_dir: Path,
        models: Mapping,
        **kwargs
) -> None:
    words = pd.read_csv(str(input_file))[input_column]
    words = {w.casefold().strip('-') for w in words.dropna()}

    closest_words = get_closest_words(
        models=models,
        words=words,
        **kwargs
    )

    for w, d in closest_words.items():
        if not d:
            continue

        table = make_closest_words_table(d)
        table.to_csv(str(output_dir / f'closest_{w}.csv'))


if __name__ == '__main__':
    model_dir = Path('../../models')
    wordlist_dir = Path('../../wordlists')

    sv_models = {
        f'sv_{year}': gensim.models.Word2Vec.load(
            str(model_dir / 'SGNS_UPDATE' / 'sv' / f'sv_{year}.w2v')
        )
        for year
        in list(range(1740, 1901, 20))
    }
    fi_models = {
        f'fi_{year}': gensim.models.Word2Vec.load(
            str(model_dir / 'SGNS_UPDATE' / 'fi' / f'fi_{year}.w2v')
        )
        for year
        in list(range(1820, 1881, 20))
    }
    en_models = {
        f'en_{year}': gensim.models.Word2Vec.load(
            str(model_dir / 'SGNS_ALIGN' / 'en' / f'en_{year}.w2v')
        )
        for year
        in list(range(1700, 1901, 20))
    }

    make_close_words_lists(
        input_file=wordlist_dir / 'seed_words.csv',
        input_column='English',
        output_dir=wordlist_dir / 'en_close_words',
        models=en_models,
        min_similarity=0,
        max_n=100,
    )
    make_close_words_lists(
        input_file=wordlist_dir / 'seed_words.csv',
        input_column='Swedish',
        output_dir=wordlist_dir / 'sv_close_words',
        models=sv_models,
        min_similarity=0,
        max_n=100,
    )
    make_close_words_lists(
        input_file=wordlist_dir / 'seed_words.csv',
        input_column='Finnish',
        output_dir=wordlist_dir / 'fi_close_words',
        models=fi_models,
        min_similarity=0,
        max_n=100,
    )
