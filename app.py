from flask import Flask, render_template, request, g, flash
from package.new_word_detection import NWD
from package.ngram import Ngram
from utils import *
import mysql.connector
import json


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
        sql = f'SELECT title,content,author,datetime_pub,uniID FROM articles_ptt WHERE title LIKE "%{query}%" LIMIT {limit} OFFSET {(page-1)*limit}'
        cursor.execute(sql)
        results = cursor.fetchall()

        comment_results = []
        ngram_results = []
        total_ngram = Ngram()

        for row in results:
            uniID = row[4]
            sql = f'SELECT tag,author,content FROM articles_comment WHERE parentID="{uniID}"'
            cursor.execute(sql)
            comment_result = cursor.fetchall()
            comment_results.append(comment_result)

            ngram = Ngram()
            ngram.fit([row[2] for row in comment_result])
            ngram_results.append((ngram.bigram, ngram.trigram))

        # Remove ngrams not in query
        remove_set = set()
        for bigram, trigram in ngram_results:
            for chars in bigram:
                remove = True
                for c in chars:
                    if c in query:
                        remove = False
                if remove:
                    remove_set.add(chars)
            for chars in trigram:
                remove = True
                for c in chars:
                    if c in query:
                        remove = False
                if remove:
                    remove_set.add(chars)
        for chars in remove_set:
            for bigram, trigram in ngram_results:
                del bigram[chars]
                del trigram[chars]

        # Sum total ngram
        for bigram, trigram in ngram_results:
            total_ngram.bigram += bigram
            total_ngram.trigram += trigram

        ngram_len = 10
        for i, (bigram, trigram) in enumerate(ngram_results):
            ngram_results[i] = (bigram.most_common(ngram_len), trigram.most_common(ngram_len))
        total_ngram.bigram = total_ngram.bigram.most_common(ngram_len)
        total_ngram.trigram = total_ngram.trigram.most_common(ngram_len)
    else:
        results = []
        comment_results = []
        ngram_results = []
        total_ngram = None
    
    return render_template('ptt.html', query=query, page=page, results=results, comment_results=comment_results, ngram_results=ngram_results, total_ngram=total_ngram)


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


if __name__ == '__main__':
    app.run()
