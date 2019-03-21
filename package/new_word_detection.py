from .utils import get_absolute_path, get_dict, check_docs
from .tokenizer import Jieba
from .trie import Trie
import logging


DEFAULT_DICT = 'adept_dict.txt'

# Log Setting
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_console = logging.StreamHandler()
logger.addHandler(log_console)


class NWD(object):
    """New Word Detection

    Main class in this package
    """

    def __init__(self, dict_file=DEFAULT_DICT, cut=False, tokenizer='jieba'):
        # TODO: useless currently, remove in future
        """
        if dict_file == DEFAULT_DICT:
            dict_file = get_absolute_path(dict_file)
        self.dict = get_dict(dict_file)
        """
        self.cut = cut

        if cut:
            if tokenizer == 'jieba':
                self.tokenizer = Jieba()
            else:
                raise ValueError(f'Unknown tokenizer {tokenizer}')

    def fit(self, docs):
        """Fit model according to documents

        Returns
        -------
        None
        """
        check_docs(docs)
        if self.cut:
            # Cut doc to a list of words
            docs = self.cut_docs(docs)

        # Build trie tree and reverse trie tree
        self.trie = Trie()
        self.rev_trie = Trie()
        for doc in docs:
            # Regular trie tree
            """
            self.trie.build(doc)
            """

            # PAT tree, build on semi-infinite string
            for l in range(len(doc)):
                self.trie.build(doc[l:])
                self.rev_trie.build(doc[::-1][l:])

    def detect(self, docs):
        """Detect new words from documents

        Returns
        -------
        newwords : list
        """
        check_docs(docs)

    def cut_docs(self, docs):
        for i, doc in enumerate(docs):
            docs[i] = [word for word in self.tokenizer.cut(doc)]
        return docs
