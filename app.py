from flask import Flask, render_template, request, g, flash
from package.new_word_detection import NWD
from utils import *
import mysql.connector
import json
import datetime
from functools import lru_cache
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(user='root', db='thesis')
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/news')
def news():
    query = request.args.get('query')
    page = request.args.get('page')
    query = parse_args(query, str, '')
    page = parse_args(page, int, 1)
    limit = 10
    if query:
        cursor = get_db().cursor()
        sql = f'SELECT title,content,datetime_pub FROM articles WHERE title LIKE "%{query}%" LIMIT {limit} OFFSET {(page-1)*limit}'
        cursor.execute(sql)
        results = cursor.fetchall()
    else:
        results = []

    return render_template('news.html', query=query, page=page, results=results)


@app.route('/ptt')
def ptt():
    query = request.args.get('query')
    page = request.args.get('page')
    limit = request.args.get('limit')
    query = parse_args(query, str, '')
    page = parse_args(page, int, 1)
    limit = parse_args(limit, int, 10)

    if query:
        cursor = get_db().cursor()
        sql = f'SELECT title,content,author,datetime_pub,uniID FROM articles_ptt WHERE content LIKE "%{query}%" LIMIT {limit} OFFSET {(page-1)*limit}'
        cursor.execute(sql)
        results = cursor.fetchall()
        comment_results = []

        for row in results:
            uniID = row[4]
            sql = f'SELECT tag,author,content FROM articles_comment WHERE parentID="{uniID}"'
            cursor.execute(sql)
            comment_result = cursor.fetchall()
            comment_results.append(comment_result)
    else:
        results = []
        comment_results = []

    return render_template('ptt.html', query=query, page=page, results=results, comment_results=comment_results)


@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html')


@app.route('/system')
def system():
    return render_template('system/list.html')


@app.route('/system/<int:test_id>')
def test(test_id):
    if test_id == 1:  # Text interface
        query = request.args.get('query')
        query = parse_args(query, str, '')
        options = {
            'sub_url': request.args.get('sub_url'),
            'sub_punc': request.args.get('sub_punc'),
            'agg_sub_symbol': request.args.get('agg_sub_symbol'),
            'split_sent': request.args.get('split_sent')
        }

        error_message = None
        results = []

        if query:
            try:
                docs = json.loads(query)
                nwd = NWD()
                results = nwd.test(docs, options)
            except Exception as e:
                error_message = str(e)

        return render_template('system/text.html', query=query, results=results, options=options, error_message=error_message)
    elif test_id == 2:  # Construct PAT tree
        query = request.args.get('query')
        query = parse_args(query, str, '')
        cut = request.args.get('cut')
        cut = True if cut else False

        error_message = None
        result = ''

        if query:
            try:
                nwd = NWD(cut=cut)
                nwd.fit([query])
                result = nwd.trie.test()
            except Exception as e:
                error_message = str(e)

        return render_template('system/tree.html', query=query, cut=cut, result=result, error_message=error_message)


@app.route('/pronoun')
# @lru_cache(maxsize=None)
def pronoun():
    limit = 20
    chart_limit = 7

    cursor = get_db().cursor()
    sql = f'SELECT * FROM queries'
    cursor.execute(sql)
    queries = [q for q in cursor.fetchall()][-2:]

    results = []
    records = []

    for query in queries:
        sql = f'SELECT token,SUM(tf) FROM ngram WHERE query_id="{query[0]}" GROUP BY token ORDER BY SUM(tf) DESC LIMIT {limit}'
        cursor.execute(sql)
        result = [(token, tf) for token, tf in cursor.fetchall()]
        results.append(result)

        record = []

        for i in range(chart_limit):
            token = result[i][0]
            data = []
            lookup_table = defaultdict(int)

            sql = f'SELECT MONTH(appear_time),SUM(tf) FROM ngram WHERE query_id="{query[0]}" AND token="{token}" GROUP BY MONTH(appear_time) ORDER BY MONTH(appear_time)'
            cursor.execute(sql)
            for month, tf in cursor.fetchall():
                lookup_table[month-1] = int(tf)
            data = [lookup_table[j] for j in range(12)]
            record.append((token, data))
        records.append(record)

    return render_template('pronoun.html', queries=queries, results=results, records=records)


if __name__ == '__main__':
    app.run()
