from pathlib import Path

import pandas as pd
import gensim


def get_closest_words(
        model,
        words: list,
        topn: int,
):
    closest = model.wv.most_similar(*words, topn=topn)

    result = pd.DataFrame(closest, columns="words similarity".split())

    return result


if __name__ == '__main__':
    model_dir = Path('../../models/SGNS_UPDATE')

    # model_1820 = gensim.models.Word2Vec.load(str(model_dir / 'fi' / 'fi_1820.w2v'))
    # model_1840 = gensim.models.Word2Vec.load(str(model_dir / 'fi' / 'fi_1840.w2v'))
    # model_1860 = gensim.models.Word2Vec.load(str(model_dir / 'fi' / 'fi_1860.w2v'))
    # model_1880 = gensim.models.Word2Vec.load(str(model_dir / 'fi' / 'fi_1880.w2v'))

    # # print(model_1820.wv.similarity('keisari', 'suuriruhtinas'))
    # # print(model_1840.wv.similarity('keisari', 'suuriruhtinas'))
    # print(model_1860.wv.similarity('keisari', 'suuriruhtinas'))
    # print(model_1880.wv.similarity('keisari', 'suuriruhtinas'))

    # # print(f"1820-1840: {get_closest_words(model_1820, 'valtio'.split(), 10)}")
    # # print(f"1840-1860: {get_closest_words(model_1840, 'valtio'.split(), 10)}")
    # print(f"1860-1880: \n {get_closest_words(model_1860, 'valtio'.split(' '), 50)}")
    # print(f"1880-1900: \n {get_closest_words(model_1880, 'valtio'.split(' '), 50)}")

    model_1740 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1740.w2v'))
    model_1760 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1760.w2v'))
    model_1780 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1780.w2v'))
    model_1800 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1800.w2v'))
    model_1820 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1820.w2v'))
    model_1840 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1840.w2v'))
    model_1860 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1860.w2v'))
    model_1880 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1880.w2v'))
    model_1900 = gensim.models.Word2Vec.load(str(model_dir / 'sv' / 'sv_1900.w2v'))

    # print(f"1740-1760: {get_closest_words(model_1740, 'nation'.split(), 10)}")
    print(f"1760-1780: \n {get_closest_words(model_1760, 'nation'.split(), 100)}")
    print(f"1780-1800: \n {get_closest_words(model_1780, 'nation'.split(), 100)}")
    print(f"1800-1820: \n {get_closest_words(model_1800, 'nation'.split(), 100)}")
    print(f"1820-1840: \n {get_closest_words(model_1820, 'nation'.split(), 100)}")
    print(f"1840-1860: \n {get_closest_words(model_1840, 'nation'.split(), 100)}")
    print(f"1860-1880: \n {get_closest_words(model_1860, 'nation'.split(), 100)}")
    print(f"1880-1900: \n {get_closest_words(model_1880, 'nation'.split(), 100)}")
    print(f"1900-1920: \n {get_closest_words(model_1900, 'nation'.split(), 100)}")
