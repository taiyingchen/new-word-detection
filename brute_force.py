from collections import Counter, defaultdict
from package.ngram import get_ngram_in_query
from package.preprocessing import SUB_SYMBOL
import mysql.connector
from datetime import date, timedelta, datetime
import re

db = mysql.connector.connect(user='root', db='thesis')
cursor = db.cursor()

print('輸入檢索詞: ', end='')
# query = '柯文哲'
query = input()
edition = 1
min_n = 2
max_n = 5

start_date = date(2018, 1, 1)
end_date = date(2019, 1, 1)
date_range = timedelta(days=1)

cursor.execute('INSERT INTO queries (query,edition) VALUES (%s,%s)', (query, edition))
db.commit()
cursor.execute('SELECT LAST_INSERT_ID()')
query_id = cursor.fetchone()[0]

total_post = 0
total_comment = 0

while start_date < end_date:
    print(start_date)
    
    sql = f'SELECT uniID FROM articles_ptt WHERE content LIKE "%{query}%" AND datetime_pub>="{start_date.isoformat()}" AND datetime_pub<"{(start_date+date_range).isoformat()}"'
    cursor.execute(sql)

    docs = []
    for post in cursor.fetchall():
        parentID = post[0]
        sql = f'SELECT content FROM articles_comment WHERE parentID="{parentID}"'
        cursor.execute(sql)
        comments = [post[0] for post in cursor.fetchall()]
        doc = SUB_SYMBOL.join(comments)
        docs.append(doc)

        total_post += 1
        total_comment += len(comments)

    ngram = get_ngram_in_query(docs, query, min_n, max_n)
    counter = Counter(ngram)

    vals = []
    for token, tf in counter.items():
        vals.append((query_id, token, tf, len(token), start_date))
    sql = f'INSERT INTO ngram (query_id,token,tf,length,appear_time) VALUES (%s,%s,%s,%s,%s)'
    cursor.executemany(sql, vals)
    db.commit()
    
    start_date += date_range

cursor.execute('UPDATE queries SET total_post=%s,total_comment=%s WHERE id=%s', (total_post, total_comment, query_id))
db.commit()