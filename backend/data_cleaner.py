from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED, NUMERIC	#for creating the schema
from whoosh.query import Query, And, Not, Term, Phrase	#for searching the database for douplicates
from whoosh.analysis import SimpleAnalyzer

#this code is for fixing genre errors in the woosh database
#-steven A

schema = Schema(GID=ID(stored=True, unique=True),#GID = Game ID
	name=TEXT(stored=True, analyzer=SimpleAnalyzer()),#standard analizer cuts out words that simpleanalyzer keeps; words like "the" and "3-d" or "8"
	release_year=NUMERIC(stored=True),
	developers=KEYWORD(stored=True, commas=True, lowercase=True),
	publishers=KEYWORD(stored=True, commas=True, lowercase=True),
	images=KEYWORD(stored=True, commas=True),
	consoles=KEYWORD(stored=True, commas=True, lowercase=True),
	sources=KEYWORD(stored=True, commas=True),
	genres=KEYWORD(stored=True, commas=True, lowercase=True),
	description=TEXT(stored=True)
	)
	
if not index.exists_in('GamesIndex'):
	idx = index.create_in('GamesIndex',schema = schema)
else:
	idx = index.open_dir('GamesIndex')	
searcher = idx.searcher()

idxwriter= idx.writer()

q = And([Term('consoles', "game boy color")])
results = searcher.search(q, limit=None)
print(results)
for result in results:
	print(result['GID'],result['name'],result['consoles'],result['genres'])
	Consoles = result['consoles']
	Consoles = Consoles.split(',')
	newConsoles=""
	for item in Consoles:
		if item not in newConsoles:
			newConsoles+=','+item
	newConsoles = newConsoles[1:]
	print(newConsoles)
	idxwriter.update_document(GID=result['GID'],name=result['name'],release_year=result['release_year'],developers=result['developers'],publishers=result['publishers'],images=result['images'],sources=result['sources'],genres=result['genres'], consoles = newConsoles, description=result['description'])
	
idxwriter.commit(optimize=True)
numdocs = searcher.doc_count_all()
print(numdocs)
searcher.close()
