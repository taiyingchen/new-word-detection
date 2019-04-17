import jieba
from abc import ABC, abstractmethod
from .utils import get_absolute_path
from .config import config

jieba.set_dictionary(config['DEFAULT']['jieba_dict_path'])
jieba.load_userdict(config['DEFAULT']['jieba_dict_path'])
jieba.enable_parallel()


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

    def cut(self, doc):
        return jieba.cut(doc, HMM=False)


class CRF(Tokenizer):
    pass
