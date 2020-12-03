# __init__.py
# Create a flask app

from flask import Flask, render_template, url_for, request
import whoosh
from whoosh.fields import *
from whoosh.qparser import MultifieldParser

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

	name, release_year, publishers, gids = mysearch.search(keywordquery)
	return render_template('results.html', query=keywordquery, results=zip(name, release_year, publishers, gids))

@app.route('/entry/', methods=['GET', 'POST'])
def entry():
	global mysearch
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args
	
	gid = data.get('gid')

	name, release_year, developers, publishers, images, sources, genres, description, consoles = mysearch.retrieve(gid)
	#print(name)
	#print(release_year)
	#print(developers)
	#print(publishers)
	#print(images)
	#print(sources)
	#print(genres)
	#print(description)
	return render_template('entry.html', gid=gid, name=name, release_year=release_year, developers=developers, publishers=publishers, images=images, sources=sources, genres=genres, description=description, consoles=consoles)

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
		gids = list()
		consoles = list()
		searchFields = ['name', 'release_year', 'developers', 'publishers', 'genres', 'description', 'consoles']
		# start of if related

		if(queryEntered.split(':')[0] == "related"):
			rname, rrelease_year, rdevelopers, rpublishers, rimages, rsources, rgenres, rdescription, rconsoles = self.retrieve(queryEntered.split(':')[1])
			# from here you can add the actual search and change the "queryEntered" value before it actually goes into the search stuff below
			
		with self.indexer.searcher() as search:
			parser = MultifieldParser(searchFields, schema=self.indexer.schema)
			query = parser.parse(queryEntered)
			results = search.search(query, limit=None)

			for x in results:
				name.append(x['name'])
				release_year.append(x['release_year'])
				developers.append(x['developers'])
				publishers.append(x['publishers'])
				images.append(x['images'])
				sources.append(x['sources'])
				genres.append(x['genres'])
				description.append(x['description'])
				consoles.append(x['consoles'])
				gids.append(x['GID'])

		return name, release_year, publishers, gids

	def retrieve(self, gid):
		with self.indexer.searcher() as search:
			parser = MultifieldParser(['GID'], schema=self.indexer.schema)
			query = parser.parse(str(gid))
			result = search.search(query, limit=None)

			name = result[0]['name']
			release_year = result[0]['release_year']
			developers = result[0]['developers']
			publishers = result[0]['publishers']
			images = result[0]['images']
			sources = result[0]['sources']
			genres = result[0]['genres']
			description = result[0]['description']
			consoles = result[0]['consoles']

		return name, release_year, developers, publishers, images, sources, genres, description, consoles

	def index(self):
		if whoosh.index.exists_in("./backend/GamesIndex"):
			self.indexer = whoosh.index.open_dir('./backend/GamesIndex')
		else: 
			sys.exit(-1)

# Create and run the app on http://127.0.0.1:5000/
if __name__ == '__main__':
	global mysearch
	mysearch = MyWhooshSearch()
	mysearch.index()
	app.run(debug=True)
	