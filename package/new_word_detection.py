from .utils import get_absolute_path, get_dict, check_docs
from .tokenizer import Jieba
from .trie import Trie
from .preprocessing import PreStr, is_sent_sep
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
        self.trie = Trie()
        self.rev_trie = Trie()
        self.cut = cut

        if cut:
            if tokenizer == 'jieba':
                self.tokenizer = Jieba()
            else:
                raise ValueError(f'Unknown tokenizer {tokenizer}')

    def fit(self, docs, ngram=5):
        """Fit model according to documents

        Returns
        -------
        None
        """
        check_docs(docs)

        # Text preprocessing
        docs = self.__preprocess_docs(docs)

        if self.cut:
            # Cut doc to a list of words
            docs = self.__cut_docs(docs)

        # Build trie tree and reverse trie tree
        for doc in docs:
            # Trie tree build on n-gram
            """
            rev_doc = doc[::-1]
            for i in range(len(doc)):
                self.trie.build(doc[i:i+ngram])
                self.rev_trie.build(rev_doc[i:i+ngram])
            """

            # PAT tree build on semi-infinite string
            start = 0
            for i in range(len(doc)):
                if is_sent_sep(doc[i]):
                    sent = doc[start:i]
                    rev_sent = doc[start:i][::-1]
                    for j in range(len(sent)):
                        self.trie.build(sent[j:])
                        self.rev_trie.build(rev_sent[j:])
                    start = i + 1

    def detect(self, docs):
        """Detect new words from documents

        Returns
        -------
        newwords : list
        """
        check_docs(docs)

    def test(self, docs, options):
        """Testing interface

        Parameters
        ----------
        docs: list of str
        options : list of PreStr class methods
        """
        check_docs(docs)
        if self.cut:
            # Cut doc to a list of words
            docs = self.__cut_docs(docs)

        class_methods = PreStr.__dict__  # Get all class methods in PreStr class
        methods = []
        for option in options:
            if options[option]:
                methods.append(class_methods[option])
        for i, doc in enumerate(docs):
            docs[i] = PreStr(doc).pipeline(methods)

        return docs

    def __cut_docs(self, docs):
        for i, doc in enumerate(docs):
            docs[i] = [word for word in self.tokenizer.cut(doc)]
        return docs

    def __preprocess_docs(self, docs):
        methods = [
            PreStr.sub_url,
            PreStr.sub_punc,
            PreStr.agg_sub_symbol
        ]

        for i, doc in enumerate(docs):
            docs[i] = PreStr(doc).pipeline(methods)

        return docs