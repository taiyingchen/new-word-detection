from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    # return "I want to graduate!"
    return render_template('index.html')

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html')