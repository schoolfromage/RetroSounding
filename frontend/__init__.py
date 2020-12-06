# __init__.py
# Create a flask app

from flask import Flask, render_template, url_for, request
import whoosh
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.qparser import OrGroup
from random import randint #used for the random page button
import json

from whoosh.query import And, Or, Not, Term #used for the relevent result custom query
import re #used for the query management

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
	if not keywordquery:
		gid = randint(0,5000)
		name, release_year, developers, publishers, images, sources, genres, description, consoles = mysearch.retrieve(gid)
		while not name:
			name, release_year, developers, publishers, images, sources, genres, description, consoles = mysearch.retrieve(randint(0,5000))
		return render_template('entry.html', gid=gid, name=name, release_year=release_year, developers=developers, publishers=publishers, images=images, sources=sources, genres=genres, description=description, consoles=consoles)
	print('Keyword Query is: ' + keywordquery)
	
	fields = list()
	if data.get('name'):
		fields.append('name')
	if data.get('release_year'):
		fields.append('release_year')
	if data.get('developers'):
		fields.append('developers')
	if data.get('publishers'):
		fields.append('publishers')
	if data.get('genres'):
		fields.append('genres')
	if data.get('description'):
		fields.append('description')
	if data.get('consoles'):
		fields.append('consoles')
	
	ppage = data.get('pp')
	npage = data.get('np')
	page = 1
	if ppage:
		page = int(ppage)
	if npage:
		page = int(npage)
	print(page)
	name, release_year, publishers, gids, consoles, images, page = mysearch.search(keywordquery, fields, page)
	d=list(zip(name, release_year, publishers, gids, consoles, images))
	return render_template('results.html', data=d, p=page, query=keywordquery, results=zip(name, release_year, publishers, gids, images))

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

	def search(self, queryEntered, fields, page):
		if not fields or fields == '_':
			fields = ['name', 'release_year', 'developers', 'publishers', 'genres', 'description', 'consoles']
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

		myGroup = OrGroup.factory(0.5)#the OrGroup allows optional or on the default search alowing complex queries, but slowing the searcher down
		parser = MultifieldParser(fields, schema=self.indexer.schema, group = myGroup) #this is used for both related queries and reqular ones
		query = None #temp value - this value is alwayse changed before the search

		relatedMatch =re.match(r'(.*)related:(\w*)(.*)',queryEntered)#0=whole match, 1=before, 2=data, 3=after for match.group(#)
		if relatedMatch:
			with self.indexer.searcher() as search:
				relatedDoc = search.document(GID = relatedMatch.group(2))#looks for the gid of the thing after the collon
				if relatedDoc: #document will return None if the gid is invalid
					print(relatedDoc['name'])
					relatedTerms = Or([
						Term('consoles',relatedDoc['consoles'].lower(),boost=0.7),
						Term('genres',relatedDoc['genres'].lower(), boost=1.3),
						Term('developers',relatedDoc['developers'].lower(), boost=1),
						Term('publishers',relatedDoc['publishers'].lower(), boost=0.9)], scale=0.5) #defines how well a doc is boosted for having many different qualities
					query = And([relatedTerms, Not(Term('GID', relatedDoc['GID']))])
		if query == None: #ie: if the query was not already overwritten
			query = parser.parse(queryEntered)
			print(query)

		with self.indexer.searcher() as search:
			results = search.search_page(query, page, pagelen=20)

			for x in results:
				name.append(x['name'])
				release_year.append(x['release_year'])
				developers.append(x['developers'])
				publishers.append(x['publishers'])
				if x['images'] != 'n/a':
					images.append(x['images'])
				else:
					images.append("/static/images/missing_image.png")#the default no image image
				sources.append(x['sources'])
				genres.append(x['genres'])
				description.append(x['description'])
				consoles.append(x['consoles'])
				gids.append(x['GID'])

		return name, release_year, publishers, gids, consoles, images, page

	def retrieve(self, gid):
		with self.indexer.searcher() as search:
			parser = MultifieldParser(['GID'], schema=self.indexer.schema)
			query = parser.parse(str(gid))
			result = search.search(query, limit=None)
			if len(result) == 0:
				return None, None, None, None, None, None, None, None, None

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
