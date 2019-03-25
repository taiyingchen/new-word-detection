import jieba
from abc import ABC, abstractmethod
from .utils import get_absolute_path


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
        jieba.set_dictionary(get_absolute_path('dict.txt.big'))
        jieba.load_userdict(get_absolute_path('adept_dict.txt'))
        # self.cut = jieba.cut

    def cut(self, doc):
        return jieba.cut(doc, HMM=False)


class CRF(Tokenizer):
    pass
