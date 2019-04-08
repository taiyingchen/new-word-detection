from .utils import get_absolute_path, get_dict, check_docs, get_list
from .tokenizer import Jieba
from .trie import Trie, BTrie
from .preprocessing import PreStr, get_sents_from_doc, SUB_SYMBOL
from .formula import pmi, npmi, entropy
from nltk import everygrams
from collections import defaultdict
import logging


RE_CUSTOM = '|'.join(get_list('dict/stopwords.txt'))

# Log Setting
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_console = logging.StreamHandler()
logger.addHandler(log_console)


class NWD(object):
    """New Word Detection

    Main class in this package

    Parameters
    ----------
    max_len : int
        max length of ngram
    cut : bool, optional (default=True)
        Whether cut sequence to word or not
    tokenizer : str, optional (default='jieba')
        Indicate which tokenizer to use
    norm_pmi : bool, optional (default=False)
        Whether normalize pmi or not
    """

    def __init__(self, max_len, cut=True, tokenizer='jieba', norm_pmi=False):
        self.max_len = max_len
        self.cut = cut
        self.norm_pmi = norm_pmi
        
        self.trie = Trie()
        self.rev_trie = Trie()
        self.len = 0

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

        # Text preprocessing
        docs = self.preprocess_docs(docs)

        # Build trie tree
        self.build_tree(docs)

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
        docs : list of str
        options : list of PreStr class methods
        """
        check_docs(docs)
        if self.cut:
            # Cut doc to a list of words
            docs = self.cut_docs(docs)

        class_methods = PreStr.__dict__  # Get all class methods in PreStr class
        methods = []
        for option in options:
            if options[option]:
                methods.append(class_methods[option])
        for i, doc in enumerate(docs):
            docs[i] = PreStr(doc).pipeline(methods)

        return docs

    def cut_docs(self, docs):
        for i, doc in enumerate(docs):
            docs[i] = [word for word in self.tokenizer.cut(doc)]
        return docs

    def preprocess_docs(self, docs):
        for i, doc in enumerate(docs):
            docs[i] = PreStr(doc).sub_url().sub_custom(RE_CUSTOM).sub_punc().agg_sub_symbol()

        return docs

    def build_tree(self, docs):
        """Build trie tree and reverse trie tree
        """

        for doc in docs:
            for sent in get_sents_from_doc(doc):
                # PAT tree build on semi-infinite string
                rev_sent = sent[::-1]
                for j in range(len(sent)):
                    self.trie.build(sent[j:])
                    self.rev_trie.build(rev_sent[j:])
                self.len += len(sent)

    def detect_new_words(self, min_depth, max_depth):
        for node in self.trie.bfs(min_depth, max_depth):
            node = self.trie.get(node['value'])
            node_x = self.trie.get(node['value'][:-1])
            node_y = self.trie.get(node['value'][1:])
            xy = node['freq']
            x = node_x['freq']
            y = node_y['freq']
            # xy /= self.len
            # x /= self.len
            # y /= self.len
            _pmi = pmi(xy/self.len, x/self.len, y/self.len)
            _npmi = npmi(xy/self.len, x/self.len, y/self.len)
            if _npmi > 0.6:
                for char in '柯文哲':
                    if char in node['value']:
                        print(node['value'], xy)
                        print(node_x['value'], x)
                        print(node_y['value'], y)
                        print('pmi', _pmi)
                        print('npmi', _npmi)
                        print('-------')

    def get_score(self, word):
        """Get score of the word by its pmi and boundary entropy

        Parameters
        ----------
        word : str


        Returns
        -------
        score : float
        """
        # Calculate pmi
        # Get probability of xy, x and y
        word_x = ''.join(word[:-1])
        word_y = ''.join(word[1:])
        word = ''.join(word)
        freq = sum(self.trie.items(word).values())
        xy = freq / self.len
        x = sum(self.trie.items(word_x).values()) / self.len
        y = sum(self.trie.items(word_y).values()) / self.len
        if self.norm_pmi:
            pmi_score = npmi(xy, x, y)
        else:
            pmi_score = pmi(xy, x, y)

        # Calculate boundary entropy
        right_neighbors = defaultdict(int)
        left_neighbors = defaultdict(int)
        rev_word = word[::-1]

        # Get sentence with word prefix
        for sent, tf in self.trie.items(word).items():
            neighbor = SUB_SYMBOL if sent == word else sent[len(word)]
            right_neighbors[neighbor] += tf

        for sent, tf in self.rev_trie.items(rev_word).items():
            neighbor = SUB_SYMBOL if sent == rev_word else sent[len(rev_word)]
            left_neighbors[neighbor] += tf

        # Transform dict to list and differentiate SUB_SYMBOL
        right_tf = []
        left_tf = []
        
        for neighbor, tf in right_neighbors.items():
            if neighbor == SUB_SYMBOL:
                right_tf += [1] * tf
            else:
                right_tf.append(tf)

        for neighbor, tf in left_neighbors.items():
            if neighbor == SUB_SYMBOL:
                left_tf += [1] * tf
            else:
                left_tf.append(tf)

        right_entropy_score = entropy(right_tf)
        left_entropy_score = entropy(left_tf)

        score = pmi_score + min(right_entropy_score, left_entropy_score)

        return score, pmi_score, right_entropy_score, left_entropy_score, freq

    def get_candidate_words(self, docs):
        if self.cut:
            # Cut doc to a list of words
            docs = self.cut_docs(docs)
            # Set cut to false after tokenization
            self.cut = False
        
        candidate_words = set()
        for doc in docs:
            for sent in get_sents_from_doc(doc):
                candidate_words |= set([ngram for ngram in everygrams(sent, min_len=2, max_len=self.max_len)])

        return candidate_words


    def fit_dev(self, docs):
        """Fit model according to documents

        Returns
        -------
        None
        """
        check_docs(docs)

        # Text preprocessing
        docs = self.preprocess_docs(docs)

        # Build trie tree
        self.build_tree_dev(docs)

    def build_tree_dev(self, docs):
        """Build trie tree and reverse trie tree
        """
        self.trie = defaultdict(int)
        self.rev_trie = defaultdict(int)

        for doc in docs:
            for sent in get_sents_from_doc(doc):
                rev_sent = sent[::-1]

                # PAT tree build on semi-infinite string
                for i in range(len(sent)):
                    self.trie[sent[i:]] += 1
                    self.rev_trie[rev_sent[i:]] += 1
                self.len += len(sent)

        # Build real trie tree
        self.trie = BTrie().build(self.trie)
        self.rev_trie = BTrie().build(self.rev_trie)

    def detect_new_words_dev(self, docs, min_freq, threshold, query):
        cand_words = self.get_candidate_words(docs)
        for cand_word in cand_words:
            score, pmi_score, right_entropy_score, left_entropy_score, freq = self.get_score(cand_word)
            if freq > min_freq and score > threshold:
                print(cand_word, score)
                print('pmi:', pmi_score)
                print('right ent:', right_entropy_score)
                print('left ent:', left_entropy_score)
                print('freq:', freq)
                print('------')
