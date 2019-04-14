import re
import jieba
from .utils import get_list


SUB_SYMBOL = '。'
RE_PUNC = r'[\s,.?!@#$%^&*()\[\]{}\'\"\\/:;=~…]+|[，。？！＠＃＄％＾＆＊（）「」『』《》［］｛｝〔〕【】／‘”、：；＝～☎►▲]+'
RE_SENT_SEP = rf'{SUB_SYMBOL}+|[.,!?]+|[，。！？]+'
RE_PREP = '|'.join(get_list('dict/preposition.txt'))


class PreStr(str):
    """Subclass of built-in string for preprocessing
    """

    def sub_url(self):
        string = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', SUB_SYMBOL, self)
        return PreStr(string)

    def sub_punc(self, punc=RE_PUNC):
        """Substitute punctuation to `SUB_SYMBOL`

        Parameters
        ----------
        punc : str
            Regular expression for punctuation
        """
        string = re.sub(punc, SUB_SYMBOL, self)
        return PreStr(string)

    def sub_custom(self, custom):
        string = re.sub(custom, SUB_SYMBOL, self)
        return PreStr(string)

    def agg_sub_symbol(self):
        string = re.sub(rf'{SUB_SYMBOL}+', SUB_SYMBOL, self)
        return PreStr(string)

    def split_sent(self, sep=RE_SENT_SEP):
        """Split string to a list of sentences

        Using `sep` as the delimiter string

        Parameters
        ----------
        sep : str
            Regular expression for sentence delimiter

        Returns
        -------
        sents : list of sentences
        """
        return re.split(sep, self)

    def pipeline(self, methods):
        string = self
        for method in methods:
            string = method(string)
        return PreStr(string)


def is_sent_sep(string):
    return True if re.match(RE_SENT_SEP, string) else False


def get_sents_from_doc(doc):
    start = 0
    for i in range(len(doc)):
        # Seperate document to sentences
        if is_sent_sep(doc[i]):  # Check if char is sep symbol
            sent = doc[start:i]
            yield sent
            start = i + 1
        elif i == len(doc) - 1:  # End of document, last sentence
            sent = doc[start:]
            yield sent
    return


def filter_new_word(word_tmp):
    word = ''.join(word_tmp[0])
    if re.match(r'^(.)\1*$', word):  # Remove word with all same character
        return False
    elif re.match(r'^\d+.*|.*\d+$', word):  # Remove word start or end with digit
        return False
    elif re.match(rf'^[{RE_PREP}].*|.*[{RE_PREP}]$', word):  # Remove word start or end with preposition
        return False
    elif re.match(r'\d*年?\d*月\d*日?', word):  # Remove date
        return False
    else:
        return True
