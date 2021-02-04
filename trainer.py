from indexer import Indexer


class Trainer:
    _indexer: Indexer

    def __init__(self):
        self._indexer = Indexer(dictionary_load=True)  # to only generate vectors and centroids set True
        self._indexer.train()


def main():
    trainer = Trainer()


if __name__ == '__main__':
    main()
