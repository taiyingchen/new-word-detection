import jieba
from abc import ABC, abstractmethod


class Tokenizer(ABC):
    """Abstract class for tokenizer
    """

    @abstractmethod
    def cut(self):
        pass


class Jieba(Tokenizer):
    """Implement through jieba
    """

    def __init__(self):
        pass
        # self.cut = jieba.cut

    def cut(self, doc):
        return jieba.cut(doc, HMM=False)


class CRF(Tokenizer):
    pass
