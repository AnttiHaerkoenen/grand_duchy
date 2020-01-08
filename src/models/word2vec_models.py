from pathlib import Path

import gensim


def get_closest_words(
        model,
        words: list,
        topn: int,
):
    closest = model.wv.most_similar(*words, topn=topn)
    return [t[0] for t in closest]


if __name__ == '__main__':
    model_dir = Path('../../models/fi')
    model_1820 = gensim.models.Word2Vec.load(str(model_dir / 'fi_1820.w2v'))
    model_1840 = gensim.models.Word2Vec.load(str(model_dir / 'fi_1840.w2v'))
    model_1860 = gensim.models.Word2Vec.load(str(model_dir / 'fi_1860.w2v'))
    model_1880 = gensim.models.Word2Vec.load(str(model_dir / 'fi_1880.w2v'))

    # print(model_1820.wv.similarity('keisari', 'suuriruhtinas'))
    # print(model_1840.wv.similarity('keisari', 'suuriruhtinas'))
    print(model_1860.wv.similarity('keisari', 'suuriruhtinas'))
    print(model_1880.wv.similarity('keisari', 'suuriruhtinas'))

    print(f"1820-1840: {' '.join(get_closest_words(model_1820, 'kansa'.split(), 10))}")
    print(f"1840-1860: {' '.join(get_closest_words(model_1840, 'kansa'.split(), 10))}")
    print(f"1860-1880: {' '.join(get_closest_words(model_1860, 'kansa'.split(), 10))}")
    print(f"1880-1900: {' '.join(get_closest_words(model_1880, 'kansa'.split(), 10))}")
