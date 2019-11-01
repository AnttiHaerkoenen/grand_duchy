"""
From 10.5281/zenodo.3270648
"""

import os

import gensim


lang = "fi"  ## change this


class MySentences(object):  ## This class has been directly copied from gensim.
    def __init__(self, list_):
        self.list_ = list_

    def __iter__(self):
        for file in self.list_:
            with open(file, "r") as fname:  ## Our files are line-separated, with tab-separated, lowercased tokens
                for line in fname:
                    yield line.split("\t")


if __name__ == '__main__':
    dir_out = ''
    dict_files = {}  # todo
    count = 0
    for key in sorted(list(dict_files.keys())):  # dict_files is a dict with time bins as keys, and lists of filepaths as values
        number_of_files = len(dict_files[key])
        print("Number of files for double decade starting in", str(key), "is", str(number_of_files))
        if os.path.exists(dir_out + "/model_" + lang + "_" + str(key) + ".w2v") is False:
            print("model_" + lang + "_" + str(key) + " does not exist, running")
            if number_of_files > 0:
                if count == 0:  ## This is the first model.
                    count += 1
                    sentences = MySentences(dict_files[key])
                    model = gensim.models.Word2Vec(sentences, min_count=100, workers=14, seed=1830, epochs=5)
                    model.save(dir_out + "/model_" + lang + "_" + str(key) + ".w2v")
                    print("Model saved, on to the next")
                if count > 0:  ## this is for the subsequent models.
                    print("model for double decade starting in", str(key))
                    model = gensim.models.Word2Vec.load(dir_out + "/model_" + lang + "_" + str(
                        key - 20) + ".w2v")  ## If the script crashes, we make sure to have the latest model.
                    sentences = MySentences(dict_files[key])
                    model.build_vocab(sentences, update=True)
                    model.train(sentences, total_examples=model.corpus_count, start_alpha=model.alpha,
                                end_alpha=model.min_alpha, epochs=model.iter)
                    model.save(dir_out + "/model_" + lang + "_" + str(key) + ".w2v")
                    print("Model saved, on to the next")
