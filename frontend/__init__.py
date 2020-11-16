# __init__.py
# Create a flask app

from flask import Flask, render_template, url_for, request
import whoosh
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('welcome_page.html')

@app.route('/results/', methods=['GET', 'POST'])
def results():
	#TODO whoosh stuff

	return render_template('results.html')

@app.route('/entry/', methods=['GET', 'POST'])
def entry():
	#TODO whoosh stuff

	return render_template('entry.html')

# Create and run the app on http://127.0.0.1:5000/
if __name__ == '__main__':
	app.run(debug=True)