# __init__.py
# Create a flask app

from flask import Flask, render_template, url_for, request
import whoosh
import whoosh.index as index
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

	name, release_year, developers, publishers, images, sources, genres, description = mysearch.search(keywordquery)
	print("name:" + str(name[0]))
	return render_template('results.html', query=keywordquery, results=zip(name, release_year, developers, publishers, images, sources, genres, description))

@app.route('/entry/', methods=['GET', 'POST'])
def entry():
	#TODO whoosh stuff

	return render_template('entry.html')

class MyWhooshSearch(object):
	"""docstring for MyWhooshSearch"""
	def __init__(self):
		super(MyWhooshSearch, self).__init__()
	
	def search(self, queryEntered):
		name = list()
		release_year = list()
		developers = list()
		publishers = list()
		images = list()
		sources = list()
		genres = list()
		description = list()
		searchFields = ['name', 'release_year', 'developers', 'publishers', 'genres', 'description']
		with self.indexer.searcher() as search:
			query = MultifieldParser(searchFields, schema=self.indexer.schema)
			query = query.parse(queryEntered)
			results = search.search(query, limit=2)

			for x in results:
				name.append(x['name'])
				release_year.append(x['release_year'])
				developers.append(x['developers'])
				publishers.append(x['publishers'])
				images.append(x['images'])
				sources.append(x['sources'])
				genres.append(x['genres'])
				description.append(x['description'])

		return name, release_year, developers, publishers, images, sources, genres, description
	
	def index(self):
		# schema = Schema(GID=ID(stored=True, unique=True),name=KEYWORD(stored=True),release_year=NUMERIC(stored=True),developers=KEYWORD(stored=True, commas=True),publishers=KEYWORD(stored=True, commas=True),images=KEYWORD(stored=True, commas=True),sources=KEYWORD(stored=True, commas=True),genres=KEYWORD(stored=True, commas=True),description=TEXT(stored=True))
		idx = open_dir('../backend/GamesIndex')
		self.indexer = idx
# Create and run the app on http://127.0.0.1:5000/
if __name__ == '__main__':
	global mysearch
	mysearch = MyWhooshSearch()
	mysearch.index()
	app.run(debug=True)