from flask import Flask, render_template, request
from package.new_word_detection import NWD
import mysql.connector
import json


app = Flask(__name__)

db = mysql.connector.connect(user='root', db='thesis')
cursor = db.cursor()

nwd = NWD()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/news')
def news():
    query = request.args.get('query')
    query = '' if query == None else query
    limit = 10
    if query:
        sql = f'SELECT title,content,datetime_pub FROM articles WHERE title LIKE "%{query}%" LIMIT {limit}'
        cursor.execute(sql)
        column_names = cursor.column_names
        results = cursor.fetchall()
    else:
        column_names = []
        results = []

    return render_template('news.html', query=query, column_names=column_names, results=results)


@app.route('/ptt')
def ptt():
    query = request.args.get('query')
    query = '' if query == None else query
    limit = 10
    if query:
        sql = f'SELECT title,content,datetime_pub FROM articles WHERE title LIKE "%{query}%" LIMIT {limit}'
        cursor.execute(sql)
        column_names = cursor.column_names
        results = cursor.fetchall()
    else:
        column_names = []
        results = []

    return render_template('ptt.html', query=query, column_names=column_names, results=results)


@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html')


@app.route('/system')
def system():
    query = request.args.get('query')
    query = '' if query == None else query
    error_message = None
    results = []

    if query:
        try:
            docs = json.loads(query)
            results = nwd.test(docs)
        except Exception as e:
            error_message = str(e)

    return render_template('system.html', query=query, results=results, error_message=error_message)


if __name__ == '__main__':
    app.run()
