from pathlib import Path

import pandas as pd
import gensim


def get_closest_words(
        *,
        models: dict,
        words: list,
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
        word_data: dict,
) -> pd.DataFrame:

    df = pd.DataFrame.from_dict(word_data)
    df = df.applymap(lambda e: e[0])

    return df


def make_close_words_lists(
        input_file: Path,
        input_column: str,
        output_dir: Path,
        models: dict,
) -> None:
    words = pd.read_csv(str(input_file))[input_column]
    words = [w.casefold() for w in words]

    closest_words = get_closest_words(
        models=models,
        words=words,
    )

    for w, d in closest_words.items():
        table = make_closest_words_table(d)
        table.to_csv(str(output_dir / f'closest_{w}.csv'))


if __name__ == '__main__':
    model_dir = Path('../../models/SGNS_UPDATE')

    years = list(range(1740, 1901, 20))

    models = {
        f'sv_{year}': gensim.models.Word2Vec.load(str(model_dir / 'sv' / f'sv_{year}.w2v'))
        for year
        in years
    }

    make_close_words_lists(
        input_file=Path('../../wordlists/seed_words.csv'),
        input_column='Swedish',
        output_dir=Path('../../wordlists/sv_close_words'),
        models=models,
    )
