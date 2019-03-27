from nltk import bigrams, trigrams
from collections import Counter, defaultdict
from .preprocessing import PreStr, SUB_SYMBOL

class Ngram(object):
    def __init__(self):
        self.bigram = Counter()
        self.trigram = Counter()

    def fit(self, docs):
        docs = self.__preprocess_docs(docs)
        for doc in docs:
            for sent in doc.split(SUB_SYMBOL):
                self.bigram += Counter(bigrams(sent))
                self.trigram += Counter(trigrams(sent))
        
    def __preprocess_docs(self, docs):
        methods = [
            PreStr.sub_url,
            PreStr.sub_punc,
            PreStr.agg_sub_symbol
        ]

        for i, doc in enumerate(docs):
            docs[i] = PreStr(doc).pipeline(methods)

        return docs
