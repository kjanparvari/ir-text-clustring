import typing


class Token:
    _word: str
    _position: int

    def __init__(self, word: str, position: int):
        self._word = word
        self._position = position

    def getWord(self):
        return self._word

    def getPosition(self):
        return self._position

    def __str__(self):
        return self._word + " - " + str(self._position)


class Tokenizer:
    def __init__(self):
        pass

    @staticmethod
    def tokenizeDoc(doc: str) -> list:
        result: [Token] = []
        lst: list = doc.strip().replace("(", " ").replace(")", " ").replace("»", " ").replace("»", " ").split()
        # lst[:] = [word.strip().replace(".", "").replace("،", "") for word in lst]
        word: str
        for word in lst:
            pass
        position: int = 1
        for word in lst:
            if word != "":
                result.append(Token(word, position))
                position += 1
        return result
