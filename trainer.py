from indexer import Indexer


class Trainer:
    _indexer: Indexer

    def __init__(self):
        self._indexer = Indexer()


def main():
    trainer = Trainer()


if __name__ == '__main__':
    main()
