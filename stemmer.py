import typing
import re
from tokenizer import Token


class Stemmer:
    _stop_words: [str]

    def __init__(self):
        with open("./stopwords/stopwords.txt", encoding="utf-8") as file:
            self._stop_words = file.read().strip().split()

    def normalize_list(self, tokens_list: [Token]) -> list:
        result: list = []
        token: Token
        for token in tokens_list:
            nw = self._normalize_word(token.getWord())
            if nw != "":
                if nw == "است":
                    print("shit")
                result.append(Token(nw, token.getPosition()))
                del token
        del tokens_list
        return result

    def _normalize_word(self, word: str) -> str:
        result: str = word.strip()

        result = self.correct_invalid_chars(result)
        if result == "":
            return ""
        result = self.remove_redundant_notations(result)
        if result == "":
            return ""
        if self._stop_words.__contains__(result):  # checking stop words
            return ""
        result = self.removeZamir(result, False)
        if result == "":
            return ""
        result = self.removeHa(result)
        if result == "":
            return ""
        if self._stop_words.__contains__(result):  # checking stop words
            return ""
        return result

    @staticmethod
    def hasNumbers(word: str):
        return any(char.isdigit() for char in word)

    @staticmethod
    def removeHa(word: str):
        ends = ['یی', ' ی', 'ها', 'ات']
        for end in ends:
            if word.endswith(end):
                word = word[:-len(end)]
        return word

    def remove_redundant_notations(self, word: str) -> str:
        word = word.replace("،", "").replace("؟", "").replace(":", "").replace("/", "").replace("\\", "")

        if self.hasNumbers(word):
            return word
        else:
            return word.replace(".", "")

    def removeZamir(self, sInput, bState):
        ln = 0
        s_rule = "^(?P<stem>.+?)((?<=(ا|و))ی)?(ها)?(ی)?((ات)?( تان|تان| مان|مان| شان|شان)|ی|م|ت|ش|ء)$"
        ln += 1
        if bState:
            ln += 2
            s_rule = "^(?P<stem>.+?)((?<=(ا|و))ی)?(ها)?(ی)?(ات|ی|م|ت|ش| تان|تان| مان|مان| شان|شان|ء)$"
        ln += 1
        return self.extractStem(sInput, s_rule)

    @staticmethod
    def extractStem(s_input, s_rule, s_replacement="\g<stem>"):
        r = 0
        return re.sub(s_rule, s_replacement, s_input).strip()
        r += 1

    @staticmethod
    def correct_invalid_chars(word: str) -> str:
        new_string: [str] = []
        for char in word:
            if char == "۱":
                new_string.append("1")
            elif char == "۲":
                new_string.append("2")
            elif char == "۳":
                new_string.append("3")
            elif char == "۴":
                new_string.append("4")
            elif char == "۵":
                new_string.append("5")
            elif char == "۶":
                new_string.append("6")
            elif char == "۷":
                new_string.append("7")
            elif char == "۸":
                new_string.append("8")
            elif char == "۹":
                new_string.append("9")
            elif char == "۰":
                new_string.append("0")
            elif char == 'ي':
                new_string.append('ی')
            elif char in ['ة', 'ۀ']:
                new_string.append('ه')
            elif char in ['‌', '‏']:
                new_string.append(' ')
            elif char == 'ك':
                new_string.append('ک')
            elif char == 'ؤ':
                new_string.append('و')
            elif char in ['إ', 'أ']:
                new_string.append('ا')
            elif char in ['\u064B',  # تنوین فتحه
                          '\u064C',  # تنوین ضمه
                          '\u064D',  # تنوین کسره
                          '\u064E',  # فتحه
                          '\u064F',  # ضمه
                          '\u0650',  # کسره
                          '\u0651',  #
                          '\u0652']:  # سکون
                pass
            else:
                new_string.append(char)

        return ''.join(new_string)
