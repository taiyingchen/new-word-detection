import jieba
from abc import ABC, abstractmethod
import os
from .utils import get_absolute_path
from .config import config


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
        if 'jieba_dict_path' in config['DEFAULT'] and os.path.isfile(config['DEFAULT']['jieba_dict_path']) :
            jieba.set_dictionary(config['DEFAULT']['jieba_dict_path'])
        if 'user_dict_path' in config['DEFAULT'] and os.path.isfile(config['DEFAULT']['user_dict_path']) :
            jieba.load_userdict(config['DEFAULT']['user_dict_path'])
        jieba.enable_parallel()

    def cut(self, doc):
        return jieba.cut(doc, HMM=False)


class CRF(Tokenizer):
    pass
