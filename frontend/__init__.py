# __init__.py
# Create a flask app

from flask import Flask, render_template, url_for, request, session
from flask_session import Session
import whoosh
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.qparser import OrGroup
from random import randint #used for the random page button
from urllib.request import urlopen
from urllib.parse import urlparse
from math import ceil

from whoosh.query import And, Or, Not, Term #used for the relevent result custom query
import re #used for the query management

app = Flask(__name__)
#settup the flask session as per the docs
#the session should hold a 'mysearch' index containing the mysearch class object
SESSION_TYPE='filesystem'
app.config.from_object(__name__)
Session(app)

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('welcome_page.html')

@app.route('/results/', methods=['GET', 'POST'])
def results():
	if not 'mysearch' in session:
		session['mysearch'] = MyWhooshSearch()
	mysearch = session['mysearch']
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args
	
	keywordquery = data.get('searchterm')
	
	minyear = data.get('minyear')
	maxyear = data.get('maxyear')
	if minyear == None:
		minyear = ''
	if maxyear == None:
		maxyear = ''
	if (minyear!=''):#if minyear still has stuff:
		minyear = minyear+' ';#the formating for this command is difficult for me to code cleanly
	if (maxyear!=''):#if maxyear still has stuff:
		maxyear = ' '+maxyear;
	if (minyear!='' or maxyear!=''):
		yearText='release_year:['+str(minyear)+'TO'+str(maxyear)+'] '
		keywordquery = yearText + keywordquery

		
	rang = 15000
	if not keywordquery:
		gid = randint(0,rang)
		name, release_year, developers, publishers, images, sources, genres, description, consoles = mysearch.retrieve(gid)
		while not name:
			name, release_year, developers, publishers, images, sources, genres, description, consoles = mysearch.retrieve(randint(0,rang))
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
	if not ppage:
		ppage = data.get('hpp')
	npage = data.get('np')
	if not npage:
		npage = data.get('hnp')

	lpage = data.get('lp')
	if not lpage:
		lpage = data.get('hlp')

	page = 1
	pages = 1
	if ppage:
		page = int(ppage)
	if npage:
		page = int(npage)
	if lpage:
		pages = int(lpage)
		page = int(lpage)

	print(page)
	name, release_year, publishers, gids, consoles, images, page, pages = mysearch.search(keywordquery, fields, page)
	d=list(zip(name, release_year, publishers, gids, consoles, images))
	return render_template('results.html', data=d, p=page, ps=pages, query=keywordquery, results=zip(name, release_year, publishers, gids, images))

@app.route('/entry/', methods=['GET', 'POST'])
def entry():
	if not 'mysearch' in session:
		session['mysearch'] = MyWhooshSearch()
	mysearch = session['mysearch']
	if request.method == 'POST':
		data = request.form
	else:
		data = request.args
	
	gid = data.get('gid')

	name, release_year, developers, publishers, images, sources, genres, description, consoles = mysearch.retrieve(gid)
	validSources = list()

	# for s in sources:
		# try:
			# urlparse(s)
			# if urlopen(s).getcode() == 200:
				# validSources.append(s)
		# except:
			# print("invalid url")

	# l = '/error/'
	# if not validSources:
		# validSources.append(l)

	return render_template('entry.html', gid=gid, name=name, release_year=release_year, developers=developers, publishers=publishers, images=images, sources=sources, genres=genres, description=description, consoles=consoles)

@app.route('/error/', methods=['GET', 'POST'])
def error():
	return render_template('error.html')

class MyWhooshSearch(object):
	"""docstring for MyWhooshSearch"""
	def __init__(self):
		super(MyWhooshSearch, self).__init__()
		self.index()
		
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
			results = search.search_page(query, page, pagelen=10)

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

		pages = 0
		with self.indexer.searcher() as search:
			results = search.search(query, limit=None)
			pages = ceil(len(results) / 10)

		return name, release_year, publishers, gids, consoles, images, page, pages

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
			sources = result[0]['sources'].split(',')
			genres = result[0]['genres'].split(',')
			description = result[0]['description']
			consoles = result[0]['consoles'].split(',')
			print(sources)
		return name, release_year, developers, publishers, images, sources, genres, description, consoles

	def index(self):
		if whoosh.index.exists_in("./backend/GamesIndex"):
			self.indexer = whoosh.index.open_dir('./backend/GamesIndex')
		else: 
			sys.exit(-1)


# Create and run the app on http://127.0.0.1:5000/
if __name__ == '__main__':
	app.run(debug=True)
