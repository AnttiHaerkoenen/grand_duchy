from pathlib import Path

import pandas as pd
import gensim


def get_closest_words(
        *,
        models: list,
        words: list,
        min_similarity: int = None,
        max_n: int = 10,
):
    # TODO
    closest = model.wv.most_similar(*words, topn=max_n)

    return result


if __name__ == '__main__':
    model_dir = Path('../../models/SGNS_UPDATE')
