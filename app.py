from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)
db = mysql.connector.connect(user='root', db='thesis')
cursor = db.cursor()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/news')
def data():
    query = request.args.get('query')
    limit = 10
    if query:
        sql = f'SELECT title,content,datetime_pub FROM articles WHERE title LIKE "%{query}%" LIMIT {limit}'
        cursor.execute(sql)
        column_names = cursor.column_names
        results = cursor.fetchall()
    else:
        query = ''
        column_names = []
        results = []

    return render_template('news.html', query=query, column_names=column_names, results=results)


@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html')


if __name__ == '__main__':
    app.run()
