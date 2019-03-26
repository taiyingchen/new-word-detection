import re
import jieba

SUB_SYMBOL = '。'
RE_PUNC = r'[\s,.?!@#$%^&*()\'\"]+|[，。？！＠＃＄％＾＆＊（）‘”]+'
RE_SENT_SEP = r'[.,!?]+|[，。！？]+'


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