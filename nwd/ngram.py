from nltk import bigrams, trigrams, everygrams, ngrams
from collections import Counter, defaultdict
from .preprocessing import PreStr, SUB_SYMBOL
from .utils import get_list


RE_CUSTOM = '|'.join(get_list('dict/stopwords.txt')+get_list('dict/persons.txt')+get_list('dict/custom.txt'))


def preprocess_docs(docs, query):
    re_custom = rf'{RE_CUSTOM}|{query}'  # Substitute custom words and query
    for i, doc in enumerate(docs):
        docs[i] = PreStr(doc.lower()).sub_url().sub_custom(re_custom).sub_punc().agg_sub_symbol()

    return docs


def long_gram_first(ngram):
    for token in ngram:
        tf = ngram[token]
        for short in [''.join(short) for short in everygrams(token, len(token)-1, len(token)-1)]:
            ngram[short] -= tf
    return ngram


def get_ngram_in_query(docs, query, min_n, max_n):
    docs = preprocess_docs(docs, query)
    ngram = []
    for doc in docs:
        for sent in doc.split_sent():
            ngram += [''.join(token) for token in everygrams(sent, min_n, max_n) for char in query if char in token]
    return ngram
