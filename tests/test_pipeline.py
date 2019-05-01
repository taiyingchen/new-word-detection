import mysql.connector
from nwd.new_word_detection import NWD
from nwd.domain_classifier import Classifier
from nwd.preprocessing import SUB_SYMBOL
from datetime import date, timedelta, datetime
import sys
import numpy as np

db = mysql.connector.connect(user='root', db='thesis')
cursor = db.cursor()

print('Enter text type: ', end='')
text_type = input()
print('Enter min frequency: ', end='')
min_freq = int(input())
print('Enter threshold: ', end='')
threshold = int(input())
start_date = date(2018, 1, 1)
end_date = date(2019, 1, 1)
date_range = timedelta(days=1)

all_words = set()
target_mapping = {
    'ETtoday星光雲': '時尚流行',
    'ETtoday運動雲': '體育運動',
    '社會': '社會議題',
    '生活': '生活消費',
    '國際': '國內外政治',
    '政治': '國內外政治',
    '地方': '社會議題',
    'ETtoday寵物雲': '休閒娛樂',
    '財經': '金融經濟',
    'ETtoday健康雲': '健康醫療',
    'ETfashion': '時尚流行',
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
target_names = sorted(list(set(target_mapping.values())))
model_path = 'model/text_clf_svm_log.pkl'
text_clf = Classifier(model_path)

while start_date < end_date:
    if text_type == 'ptt':
        sql = f'SELECT uniID,content FROM articles_ptt WHERE datetime_pub>="{start_date.isoformat()}" AND datetime_pub<"{(start_date+date_range).isoformat()}"'
    elif text_type == 'news':
        # sql = f'SELECT content FROM articles limit {limit}'
        sql = f'SELECT uniID,content FROM articles WHERE datetime_pub>="{start_date.isoformat()}" AND datetime_pub<"{(start_date+date_range).isoformat()}"'
        # sql = f'SELECT content FROM articles limit {offset},{limit}'
    else:
        print('Unknown text type')
        sys.exit()
    cursor.execute(sql)

    docs = []
    docs_id = []
    length = 0
    for post in cursor.fetchall():
        length += 1
        if text_type == 'ptt':
            parentID, content = post
            doc = [content]
            sql = f'SELECT content FROM articles_comment WHERE parentID="{parentID}"'
            cursor.execute(sql)
            doc += [comment[0] for comment in cursor.fetchall()]
            docs_id.append(post[0])
            docs.append(SUB_SYMBOL.join(doc))
        elif text_type == 'news':
            docs_id.append(post[0])
            docs.append(post[1])
    print('length of docs:', len(docs))

    nwd = NWD(max_len=3, min_freq=min_freq, min_pmi=threshold, min_entropy=threshold)
    new_words = nwd.fit_detect(docs)

    for i, doc in enumerate(docs):
        docs[i] = ' '.join(doc)

    domains = []
    for new_word in new_words:
        indices = new_word[4]
        pred_docs = [docs[i] for i in indices]
        proba = text_clf.predict(pred_docs)
        domains.append(proba)

    vals = []
    for i, prob in enumerate(domains):
        new_word = ''.join(new_words[i][0])
        articles_id = map(lambda k: docs_id[k], new_words[i][4])
        articles_id = list(articles_id)
        if new_word not in all_words:
            vals.append((new_word, new_words[i][1], new_words[i][2], new_words[i][3], 2, str(articles_id), target_names[np.argmax(prob)], str(prob.tolist()), text_type, start_date))
            all_words.add(new_word)

    sql = f'INSERT INTO new_words (word,freq,pmi,entropy,dict_type,articles_id,domain,domain_prob,origin,detect_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cursor.executemany(sql, vals)
    db.commit()

    start_date += date_range
    