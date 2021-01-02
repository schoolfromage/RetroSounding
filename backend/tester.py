from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED, NUMERIC	#for creating the schema
from whoosh.query import Query, And, Not, Term, Phrase, Every	#for searching the database for douplicates
from whoosh.qparser import QueryParser
from whoosh.analysis import SimpleAnalyzer


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
QP = QueryParser("name",schema=schema)

q = Term('name','abm')
results = searcher.search(q)
print(results)
for result in results:
	print(result['GID'],'\t',result['name'],'\t',result['consoles'],'\t',result['genres'],'\t',result['images'])

#numdocs = searcher.doc_count_all()
#print(numdocs)
searcher.close()
