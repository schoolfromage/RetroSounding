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
	global mysearch
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args

	keywordquery = data.get('searchterm')
	print('Keyword Query is: ' + keywordquery)

	titles, description = mysearch.search(keywordquery)
	#TODO whoosh stuff
	return render_template('results.html', query=keywordquery, results=zip(titles, description))

@app.route('/entry/', methods=['GET', 'POST'])
def entry():
	#TODO whoosh stuff

	return render_template('entry.html')

class MyWhooshSearch(object):
	"""docstring for MyWhooshSearch"""
	def __init__(self):
		super(MyWhooshSearch, self).__init__()
	
	def search(self, queryEntered):
		title = list()
		description = list()
		with self.indexer.searcher() as search:
			query = MultifieldParser(['title', 'description'], schema=self.indexer.schema)
			query = query.parse(queryEntered)
			results = search.search(query, limit=None)

			for x in results:
				title.append(x['title'])
				description.append(x['description'])

		return title, description
	
	def index(self):
		schema = Schema(id=ID(stored=True), title=TEXT(stored=True), description=TEXT(stored=True))
		indexer = create_in('exampleIndex', schema)
		writer = indexer.writer()

		writer.add_document(id=u'1', title=u'hello there', description=u'cs hello, how are you')
		writer.add_document(id=u'2', title=u'hello bye', description=u'nice to meetcha')
		writer.commit()

		self.indexer = indexer

# Create and run the app on http://127.0.0.1:5000/
if __name__ == '__main__':
	global mysearch
	mysearch = MyWhooshSearch()
	mysearch.index()
	app.run(debug=True)