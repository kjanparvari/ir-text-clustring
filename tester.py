import math
from indexer import Dictionary, PostingList, Posting, DICT_DIST, POSTING_DIST
import os
import pickle

from tokenizer import Token, Tokenizer
from stemmer import Stemmer

CENTROIDS_DIR = "./dist/centroids/"
TEST_SET_DIR = "./dataset/test/"


class Tester:
    _dictionary: Dictionary
    _tokenizer: Tokenizer
    _stemmer: Stemmer

    def __init__(self):
        self._dictionary = Dictionary(load=True)
        self._tokenizer = Tokenizer()
        self._stemmer = Stemmer()
        print(self._dictionary)

    def test_doc(self, doc: str, real_class: int) -> bool:
        query_tokens = self._tokenizer.tokenizeDoc(doc)
        normalized_query_tokens = self._stemmer.normalize_list(query_tokens)
        test_vector = self.buildVector(normalized_query_tokens)
        centroids = self._dictionary.getCentroids()
        compare_result: dict = {}
        for _class, c_vector in centroids:
            _score = self.cosine(test_vector, c_vector)
            compare_result[_class] = _score
        _max_score = max(*compare_result.values())
        _guessed_classes: list = []
        for key, val in compare_result.items():
            if val == _max_score:
                _guessed_classes.append(key)

        if real_class in _guessed_classes:
            print(f"Guessed Right. class: {real_class}")
            return True
        else:
            print(f"real class: {real_class}. guessed class {str(_guessed_classes)}")
            return False

    def buildVector(self, query_tokens: [Token]) -> dict:
        idfs: dict = {}
        tfs: dict = {}
        t: Token
        for t in query_tokens:
            if tfs.__contains__(t.getWord()):
                tfs[t.getWord()] += 1
            else:
                tfs[t.getWord()] = 1
                idfs[t.getWord()] = self._dictionary.getIDF(t.getWord())
        _vector: dict = {}
        for key, value in tfs.items():
            _vector[key] = self._dictionary.getWeight(tfs[key], idfs[key])
        return _vector

    @staticmethod
    def getVectorSize(vector: dict) -> float:
        s: float = 0
        for key, value in vector.items():
            s += value * value
        return math.sqrt(s)

    def cosine(self, vector1: dict, vector2: dict) -> float:
        vector1_size: float = self.getVectorSize(vector1)
        vector2_size: float = self.getVectorSize(vector2)
        if vector1_size * vector2_size == 0:
            return 0.0
        dot_product: float = 0.0
        for key in vector1.keys():
            if key in vector2.keys():
                dot_product += vector1[key] * vector2[key]
        return dot_product / (vector1_size * vector2_size)

    def tmp(self):
        # self._query_result.printKBestCandidates()
        # pl = self._dictionary.getPostingList("لیگ")
        # cl = self._dictionary.getChampionList("لیگ")
        # print(pl)
        # print(cl)
        vec = self._dictionary.getVector("5")
        print(vec)


def main():
    tester = Tester()
    test_set: list = []
    test_set.append((1, getTestDocs("history")))
    test_set.append((2, getTestDocs("hygin")))
    test_set.append((3, getTestDocs("math")))
    test_set.append((4, getTestDocs("physics")))
    test_set.append((5, getTestDocs("technology")))
    accuracy: float = 0.0
    for real_class, docs in test_set:
        for doc in docs:
            result = tester.test_doc(doc, real_class)
            if result:
                accuracy += 1
    accuracy /= 25
    print(f"accuracy: {accuracy * 100}%")
    # se.tmp()


def getTestDocs(_class_name: str) -> list:
    from os import listdir
    from os.path import isfile, join
    result: list = []
    _dir = TEST_SET_DIR + _class_name + "/"
    only_files = [f for f in listdir(_dir) if isfile(join(_dir, f))]
    for _filename in only_files:
        with open(_dir + _filename, "r", encoding='utf-8') as file:
            doc = file.read()
            file.close()
        result.append(doc)
    return result


if __name__ == '__main__':
    main()
