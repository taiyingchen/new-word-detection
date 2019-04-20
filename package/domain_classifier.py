from sklearn.externals import joblib
from .preprocessing import PreStr, get_sents_from_doc
from .utils import check_docs
import numpy as np


TARGET_MAP = {
    'ETtoday星光雲': '時尚名人',
    'ETtoday運動雲': '體育運動',
    '社會': '社會議題',
    '生活': '生活消費',
    '國際': '國內外政治',
    '政治': '國內外政治',
    '地方': '社會議題',
    'ETtoday寵物雲': '休閒娛樂',
    '財經': '金融經濟',
    'ETtoday健康雲': '健康醫療',
    'ETfashion': '時尚名人',
    '民生消費': '生活消費',
    '軍武': '國內外政治',
    'ETtoday車雲': '生活消費',
    'ETtoday遊戲雲': '休閒娛樂',
    '3C家電': '生活消費',
    '新奇': '休閒娛樂',
    '保險': '金融經濟',
    '法律': '社會議題',
    '雲論': '社會議題'
}


def preprocess_docs(docs):
    """Preprocess documents as training data for text classifier
    """
    for i, doc in enumerate(docs):
        docs[i] = PreStr(doc).sub_url().sub_punc().agg_sub_symbol()
    return docs


def tokenize_docs(docs, tokenizer):
    """Tokenize documents as training data for text classifier

    Tokenize document to words seperated by space as training data
    
    Parameters
    ---------
    docs : list of str
        list of document
    tokenizer : Tokenizer
        instance of Tokenizer
    """
    for i, doc in enumerate(docs):
        words = []
        for sent in get_sents_from_doc(doc):
            words += [w for w in tokenizer.cut(sent)]
        docs[i] = ' '.join(words)
    return docs


class Classifier(object):
    def __init__(self, model_path):
        self.target_names = sorted(list(set(TARGET_MAP.values())))
        self.model = joblib.load(model_path)

    def predict(self, docs):
        """Predict word probability distribution on domain

        Parameters
        ---------
        docs : list of str
            list of document contains the word
        """
        check_docs(docs)

        # Average probability of each document
        proba = np.mean(self.model.predict_proba(docs), axis=0)
        return proba
