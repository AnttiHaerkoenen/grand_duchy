from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd
import gensim

from src.tools.utils import read_word_list


def make_distance_matrix(
        words: Mapping,
        model,
) -> pd.DataFrame:
    idx = [word for word in words if word in model.wv]
    result = {}

    for word in idx:
        result[word] = pd.Series(
            [model.wv.similarity(w, word) for w in idx],
            index=idx,
        )

    result = pd.DataFrame(result)

    return result


def make_distance_matrices(
        *,
        models: Iterable,
        word_file: Path,
        output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    words = read_word_list(word_file)

    for name, model in models:
        print(f"Making similarity matrix from {name}")
        d = make_distance_matrix(words, model)
        d.to_csv(output_dir / f"{name}.csv")


if __name__ == '__main__':
    model_dir = Path('../../models')
    wordlist_dir = Path('../../wordlists')
    output_dir = Path('../../data/processed') / 'distances'

    en_models = (
        (f'en_{year}', gensim.models.Word2Vec.load(
            str(model_dir / 'SGNS_ALIGN' / 'en' / f'en_{year}.w2v')
        ))
        for year
        in list(range(1620, 1941, 20))
    )
    sv_models = (
        (f'sv_{year}', gensim.models.Word2Vec.load(
            str(model_dir / 'SGNS_UPDATE' / 'sv' / f'sv_{year}.w2v')
        ))
        for year
        in list(range(1740, 1901, 20))
    )
    fi_models = (
        (f'fi_{year}', gensim.models.Word2Vec.load(
            str(model_dir / 'SGNS_UPDATE' / 'fi' / f'fi_{year}.w2v')
        ))
        for year
        in list(range(1820, 1881, 20))
    )

    make_distance_matrices(
        models=sv_models,
        word_file=wordlist_dir / 'wordlist_riksdag.csv',
        output_dir=output_dir,
    )
    make_distance_matrices(
        models=fi_models,
        word_file=wordlist_dir / 'wordlist_fi_newspapers.csv',
        output_dir=output_dir,
    )
