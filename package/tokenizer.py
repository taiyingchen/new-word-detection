import jieba
from abc import ABC, abstractmethod
from .utils import get_absolute_path


jieba.set_dictionary(get_absolute_path('dict.txt.big'))
jieba.load_userdict(get_absolute_path('adept_dict.txt'))


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
        # self.cut = jieba.cut
        pass

    def cut(self, doc):
        return jieba.cut(doc, HMM=False)


class CRF(Tokenizer):
    pass
