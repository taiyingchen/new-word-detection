from .utils import get_absolute_path, check_docs, get_dict, get_sistring
from .tokenizer import Jieba
from .trie import BTrie
from .preprocessing import PreStr, get_sents_from_doc, SUB_SYMBOL, RE_PREP, RE_STOPWORDS
from .formula import pmi, npmi, entropy
from .config import config
from nltk import everygrams
from marisa_trie import Trie
from collections import defaultdict
from tqdm import tqdm
import re
import pickle
import os


class NWD(object):
    """New Word Detection

    Main class in this package

    Parameters
    ----------
    max_len : int
        max length of ngram
    min_freq : int
        min frequency threshold
    min_pmi : float
        min pmi threshold
    min_entropy : float
        min entropy threshold
    cut : bool, optional (default=True)
        Whether cut sequence to word or not
    tokenizer : str, optional (default='jieba')
        Indicate which tokenizer to use
    norm_pmi : bool, optional (default=False)
        Whether normalize pmi or not
    """

    def __init__(self, max_len, min_freq, min_pmi, min_entropy, cut=True, tokenizer='jieba', norm_pmi=False):
        self.max_len = max_len
        self.min_freq = min_freq
        self.min_pmi = min_pmi
        self.min_entropy = min_entropy
        self.cut = cut
        self.norm_pmi = norm_pmi

        # Initialize dictionary to build trie
        self.trie = defaultdict(int)
        self.rev_trie = defaultdict(int)
        self.len = 0

        # Build existing dictionary based on trie structure
        sistring = set()
        if 'jieba_dict_path' in config['DEFAULT'] and os.path.isfile(config['DEFAULT']['jieba_dict_path']) :
            sistring = get_sistring(config['DEFAULT']['jieba_dict_path'])
        if 'user_dict_path' in config['DEFAULT'] and os.path.isfile(config['DEFAULT']['user_dict_path']) :
            sistring = get_sistring(
                config['DEFAULT']['user_dict_path'], sistring)
        self.dict = Trie(sistring)
        # Get blacklist
        self.blacklist = set()
        if 'blacklist_path' in config['DEFAULT'] and os.path.isfile(config['DEFAULT']['blacklist_path']):
            self.blacklist = get_dict(config['DEFAULT']['blacklist_path'])

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
        new_words : list
        """
        cand_words, word2doc = self.get_candidate_words(docs)
        new_words = []
        for cand_word in tqdm(cand_words):
            # `cand_word` is tuple
            freq = self.get_freq(cand_word)
            if freq > self.min_freq:
                pmi_score = self.get_pmi(cand_word)
                if pmi_score > self.min_pmi:
                    entropy_score = self.get_entropy(cand_word)
                    if entropy_score > self.min_entropy:
                        new_word = (cand_word, freq, pmi_score, entropy_score, word2doc[cand_word])
                        new_words.append(new_word)

        return new_words

    def fit_detect(self, docs):
        self.fit(docs)
        return self.detect(docs)

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
            docs[i] = PreStr(doc).sub_url().sub_punc().agg_sub_symbol()

        return docs

    def build_tree(self, docs):
        """Build trie tree and reverse trie tree
        """
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

    def get_candidate_words(self, docs):
        if self.cut:
            # Cut doc to a list of words
            docs = self.cut_docs(docs)

        cand_words = set()
        word2doc = defaultdict(list)  # Store word appear in which documents
        for i, doc in enumerate(docs):
            doc_set = set()
            for sent in get_sents_from_doc(doc):
                doc_set |= set([ngram for ngram in everygrams(
                    sent, min_len=2, max_len=self.max_len)])
            cand_words |= doc_set
            for ngram in doc_set:
                word2doc[ngram].append(i)

        # Filter candidiate words based on rules
        cand_words = filter(self.filter_word, cand_words)  # `filter` function returns a generator
        cand_words = list(cand_words)

        return cand_words, word2doc

    def get_freq(self, word):
        """Get word frequency

        Parameters
        ----------
        word : str

        Returns
        -------
        freq : int
        """
        return sum(self.trie.items(''.join(word)).values())

    def get_pmi(self, word):
        """Get word pmi

        Parameters
        ----------
        word : tuple of str

        Returns
        -------
        pmi : float
        """
        # Get probability of xy, x and y
        word_x = ''.join(word[:-1])
        word_y = ''.join(word[1:])
        word = ''.join(word)

        xy = sum(self.trie.items(word).values()) / self.len
        x = sum(self.trie.items(word_x).values()) / self.len
        y = sum(self.trie.items(word_y).values()) / self.len
        if self.norm_pmi:
            pmi_score = npmi(xy, x, y)
        else:
            pmi_score = pmi(xy, x, y)

        return pmi_score

    def get_entropy(self, word):
        """Get word entropy

        Parameters
        ----------
        word : str

        Returns
        -------
        entropy : float
        """
        right_neighbors = defaultdict(int)
        left_neighbors = defaultdict(int)
        word = ''.join(word)
        rev_word = word[::-1]

        # Get sentence with word prefix and find neighbors besides the word
        # If sentence is word itself, use `SUB_SYMBOL` to represent its neighbor
        for sent, tf in self.trie.items(word).items():
            neighbor = SUB_SYMBOL if sent == word else sent[len(word)]
            right_neighbors[neighbor] += tf

        for sent, tf in self.rev_trie.items(rev_word).items():
            neighbor = SUB_SYMBOL if sent == rev_word else sent[len(rev_word)]
            left_neighbors[neighbor] += tf

        # Transform dict to list and differentiate `SUB_SYMBOL` neighbor
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

        return min(right_entropy_score, left_entropy_score)

    def get_word_score(self, word):
        """Get score of word

        Parameters
        ----------
        word : tuple of str

        Returns
        -------
        freq : int
        pmi_score : float
        entropy : float
        """
        freq = self.get_freq(word)
        pmi_score = self.get_pmi(word)
        entropy_score = self.get_entropy(word)

        return freq, pmi_score, entropy_score

    def filter_word(self, word):
        word = ''.join(word)
        if re.match(r'^(.)\1*$', word):  # Remove word with all same character
            return False
        elif re.match(rf'^({RE_PREP}).*|.*({RE_PREP})$', word):  # Remove word start or end with preposition
            return False
        elif re.match(rf'^({RE_STOPWORDS}).*|.*({RE_STOPWORDS})$', word):  # Remove word start or end with stopwords
            return False
        elif re.match(r'.*年?\d*月\d*日?', word):  # Remove date
            return False
        elif self.dict.keys(word):  # Remove word in existing dictionary
            return False
        elif word in self.blacklist:  # Remove word in blacklist
            return False
        elif re.match(r'^[\u4E00-\u9FD5a-zA-Z]+$', word):
            return True

    def merge(self, nwd):
        if type(nwd) != type(self):
            raise TypeError(f'Type {type(nwd)} not equal to {type(self)}')
        
        self.trie.merge(nwd.trie)
        self.rev_trie.merge(nwd.rev_trie)
        self.len += nwd.len

        return self

    def save(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)
