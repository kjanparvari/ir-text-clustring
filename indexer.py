import errno
import math
import os
import pickle
import shutil
import typing
import json

from tokenizer import Tokenizer, Token
from stemmer import Stemmer

DICT_DIST = "./dist/"
POSTING_DIST = "./dist/postings-lists/"
VECTOR_DIST = "./dist/vectors/"


class Posting:
    _docId: int
    _positions: [int]

    def __init__(self, doc_id):
        self._docId = doc_id
        self._positions = []

    def addPosition(self, position: int):
        if not self._positions.__contains__(position):
            self._positions.append(position)

    def getDocId(self):
        return self._docId

    def getPositions(self):
        return self._positions.copy()

    def __str__(self):
        s: str = ""
        s += "doc: " + str(self._docId) + " | "
        for p in self._positions:
            s += str(p) + " "
        s += " *** "
        return s


class PostingList:
    _id: int
    _term: str
    _list: [Posting]
    POSTFIX: str = '.pl'

    def __init__(self, term: str, pl_id: int):
        self._list = []
        self._term = term
        self._id = pl_id

    def getId(self):
        return self._id

    def addToken(self, token: Token, doc_id: int):
        p: Posting
        for p in self._list:
            if p.getDocId() == doc_id:
                p.addPosition(token.getPosition())
                self._save()
                return
        p = Posting(doc_id)
        p.addPosition(token.getPosition())
        self._list.append(p)
        self._save()

    def getFrequency(self) -> int:
        return len(self._list)

    def getTerm(self):
        return self._term

    def getPostings(self):
        return self._list

    def getBestPostings(self, r=5):
        p: Posting
        max_posting: Posting or None
        max_tf: int
        result: [Posting] = []
        r = r if r < len(self._list) else len(self._list)
        for i in range(0, r):
            max_tf = -1
            max_posting = None
            for p in self._list:
                if (not result.__contains__(p)) and len(p.getPositions()) > max_tf:
                    max_tf = len(p.getPositions())
                    max_posting = p
            if max_posting is not None:
                result.append(max_posting)
        return result

    def getPosting(self, doc_id: int) -> Posting or None:
        posting: Posting
        for posting in self._list:
            if posting.getDocId() == doc_id:
                return posting
        return None

    def __str__(self):
        s: str = ""
        s += "term: " + self._term + " -> "
        for p in self._list:
            s += str(p)
        return s

    def _save(self):
        pl_addr: str = POSTING_DIST + str(self._id) + self.POSTFIX
        if not os.path.exists(os.path.dirname(pl_addr)):
            try:
                os.makedirs(os.path.dirname(pl_addr))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        try:
            with open(pl_addr, 'wb') as pl_file:
                pl = pickle.dump(self, pl_file)
                pl_file.close()
        except (FileNotFoundError, FileExistsError) as e:
            print("error")

    def __eq__(self, other):
        if not isinstance(other, PostingList):
            return False
        return True if self._id == other.getId() else False


class ChampionList(PostingList):
    POSTFIX: str = '.cl'

    def __init__(self, term: str, pl_id: int, pl: PostingList):
        super().__init__(term, pl_id)
        self._list = pl.getBestPostings()

    def save(self):
        self._save()


class Dictionary:
    _dict: {str, int}

    def __init__(self, load=False):
        self._dict = {}
        if load:
            self._load()

    def addToken(self, token: Token, doc_id: int):
        term = token.getWord()
        pl: PostingList
        x = self.getPostingList(term)
        if x is None:
            pl_id: int = len(self._dict)
            self._dict[term] = pl_id
            pl = PostingList(term, pl_id)
            self._save()

        else:
            pl = x
        pl.addToken(token, doc_id)

    def getPostingList(self, term: str, postfix=PostingList.POSTFIX) -> typing.Union[PostingList, None]:
        pl_id: int = self.getPostingListId(term)
        pl: PostingList
        pl_addr: str = POSTING_DIST + str(pl_id) + postfix
        if os.path.exists(pl_addr):
            with open(pl_addr, 'rb') as pl_file:
                pl = pickle.load(pl_file)
                pl_file.close()
            return pl
        else:
            return None

    def getChampionList(self, term: str):
        return self.getPostingList(term, postfix=ChampionList.POSTFIX)

    def getPostingListId(self, term: str) -> int:
        return self._dict.get(term) if self._dict.__contains__(term) else -1

    def getIDF(self, term: str) -> float:
        pl: PostingList
        pl = self.getPostingList(term)
        return 1 / len(pl.getPostings()) if pl is not None else 0

    def getTF(self, term: str, doc_id: int) -> int:
        posting: Posting
        posting = self.getPostingList(term).getPosting(doc_id)
        if posting is None:
            return 0
        return len(posting.getPositions())

    def _getVector(self, doc_id: int):
        vector: dict = {}
        term: str
        pl_id: int
        pl: PostingList
        posting: Posting or None
        for term, pl_id in self._dict.items():
            tf = self.getTF(term, doc_id)
            idf = self.getIDF(term)
            weight = self.getWeight(tf, idf)
            if weight > 0:
                vector[term] = weight
        return vector

    def getVector(self, doc_id: int):
        # return self._getVector(doc_id)
        return self.loadVector(doc_id)

    def saveVector(self, doc_id: int):
        vector = self._getVector(doc_id)
        vec_addr: str = VECTOR_DIST + str(doc_id) + '.vec'
        if not os.path.exists(os.path.dirname(vec_addr)):
            try:
                os.makedirs(os.path.dirname(vec_addr))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        try:
            with open(vec_addr, 'w') as outFile:
                json.dump(vector, outFile)
        except (FileNotFoundError, FileExistsError) as e:
            print("error")

    @staticmethod
    def loadVector(doc_id: int):
        vec_addr: str = VECTOR_DIST + str(doc_id) + '.vec'
        vector: dict
        if not os.path.exists(os.path.dirname(vec_addr)):
            try:
                os.makedirs(os.path.dirname(vec_addr))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        try:
            with open(vec_addr, 'r') as inputFile:
                vector = json.load(inputFile)
            return vector
        except (FileNotFoundError, FileExistsError) as e:
            print("error")

    @staticmethod
    def getWeight(tf: int, idf: float = None) -> float:
        if tf == 0 or idf == 0:
            return 0
        weight: float
        if idf is None:
            weight = (1 + math.log(tf))
        else:
            pass
            # weight = (1 + math.log(tf)) * math.log(DOCS_SIZE * idf)
        return weight

    def generateChampions(self):
        _size = len(self._dict.items())
        term: str
        pl_id: int
        pl: PostingList
        for term, pl_id in self._dict.items():
            pl = self.getPostingList(term)
            cl = ChampionList(term, pl_id, pl)
            cl.save()

    def _load(self):
        dic_addr: str = DICT_DIST + 'dictionary.json'
        if not os.path.exists(os.path.dirname(dic_addr)):
            try:
                os.makedirs(os.path.dirname(dic_addr))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        try:
            with open(dic_addr, 'r') as inputFile:
                self._dict = json.load(inputFile)
        except (FileNotFoundError, FileExistsError) as e:
            print("error")

    def _save(self):
        dic_addr: str = DICT_DIST + 'dictionary.json'
        if not os.path.exists(os.path.dirname(dic_addr)):
            try:
                os.makedirs(os.path.dirname(dic_addr))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        try:
            with open(dic_addr, 'w') as outFile:
                json.dump(self._dict, outFile)
        except (FileNotFoundError, FileExistsError) as e:
            print("error")

    def __str__(self):
        return str(self._dict)


class Indexer:
    _docs_size: int
    _docs_dir: str

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.stemmer = Stemmer()
        self.dictionary = Dictionary(load=False)
        self._clean()
        self._index("./dataset/train/math/", 2)

    def _index(self, _dir: str, _class: int):
        from os import listdir
        from os.path import isfile, join
        only_files = [f for f in listdir(_dir) if isfile(join(_dir, f))]
        print(len(only_files))

    # def _setup(self):
    #     from os import listdir
    #     from os.path import isfile, join
    #     my_path = [
    #
    #     ]
    #     only_files = [f for f in listdir(my_path) if isfile(join(my_path, f))]
    #     for doc_id in range(1, self._docs_size + 1):
    #         print(f"progress: {round((doc_id / (self._docs_size + 1)) * 100, 2)} %")
    #         # doc = self.docLoader.getDoc(doc_id)
    #         tokens = self.tokenizer.tokenizeDoc(doc)
    #         # print("tokens: ")
    #         # for token in tokens:
    #         # print(token)
    #         normalized_words = self.stemmer.normalize_list(tokens)
    #         # print("normalized_words: ")
    #         # for token in normalized_words:
    #         # print(token)
    #         for token in normalized_words:
    #             self.dictionary.addToken(token, doc_id)
    #     print("generating champions list")
    #     self.dictionary.generateChampions()
    #     print("caching vectors")
    #     for doc_id in range(1, DOCS_SIZE + 1):
    #         self.dictionary.saveVector(doc_id)

    @staticmethod
    def _clean():
        if os.path.exists(os.path.dirname("./dist")):
            try:
                shutil.rmtree("./dist")
            except (FileNotFoundError, FileExistsError) as e:
                print("error")
