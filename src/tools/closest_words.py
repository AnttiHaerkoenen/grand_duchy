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
    words = {w.casefold() for w in words.dropna()}

    closest_words = get_closest_words(
        models=models,
        words=words,
        **kwargs
    )

    for w, d in closest_words.items():
        table = make_closest_words_table(d)
        table.to_csv(str(output_dir / f'closest_{w}.csv'))


if __name__ == '__main__':
    model_dir = Path('../../models/SGNS_UPDATE')
    wordlist_dir = Path('../../wordlists')

    years = list(range(1740, 1901, 20))

    models = {
        f'sv_{year}': gensim.models.Word2Vec.load(
            str(model_dir / 'sv' / f'sv_{year}.w2v')
        )
        for year
        in years
    }

    make_close_words_lists(
        input_file=wordlist_dir / 'seed_words.csv',
        input_column='Swedish',
        output_dir=wordlist_dir / 'sv_close_words',
        models=models,
        min_similarity=0,
        max_n=100,
    )
