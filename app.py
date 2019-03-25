from flask import Flask, render_template, request, g
from package.new_word_detection import NWD
from utils import *
import mysql.connector
import json


app = Flask(__name__)
nwd = NWD()


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
    query = parse_args(query, str, '')
    page = parse_args(page, int, 1)
    limit = 10
    if query:
        cursor = get_db().cursor()
        sql = f'SELECT title,content,author,datetime_pub,uniID FROM articles_ptt WHERE title LIKE "%{query}%" LIMIT {limit} OFFSET {(page-1)*limit}'
        print(sql)
        cursor.execute(sql)
        results = cursor.fetchall()
        comment_results = []
        for row in results:
            uniID = row[4]
            sql = f'SELECT tag,author,content,commentTime FROM articles_comment WHERE parentID="{uniID}"'
            cursor.execute(sql)
            comment_results.append(cursor.fetchall())
    else:
        results = []
        comment_results = []

    return render_template('ptt.html', query=query, page=page, results=results, comment_results=comment_results)


@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html')


@app.route('/system')
def system():
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
            results = nwd.test(docs, options)
        except Exception as e:
            error_message = str(e)

    return render_template('system.html', query=query, results=results, options=options, error_message=error_message)


if __name__ == '__main__':
    app.run()
