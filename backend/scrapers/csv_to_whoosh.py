from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED, NUMERIC	#for creating the schema
from whoosh.query import Query, And, Term	#for searching the database for douplicates
from whoosh.qparser import QueryParser
from whoosh.analysis import SimpleAnalyzer

import re	#for the regular expressions used to read the csv
from sys import argv	#for getting the input arguments

#Steven A
#this program does not make the directory by itself
#this program expects the following format from the csvs:
#id,"name",release_year,[developer(s)],[publisher(s)],"image(s)",[src(s)],[genre(s)],[console(s)],"description"

# by default we want the output to be GamesIndex in the backend file
inputFile = argv[1]
outputDir = argv[2]

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

if not index.exists_in(outputDir):
	idx = index.create_in(outputDir,schema = schema)
else:
	idx = index.open_dir(outputDir)	
searcher = idx.searcher()
QP = QueryParser("name",schema=schema)
FileInput = open(inputFile, 'r', encoding = "utf_16")

if not FileInput:
	print("error file not read")
List = FileInput.readlines()
idxwriter= idx.writer()
for line in List[1:]:
	LM = re.match(r'([^,]*),"(.*)",([^,]*),\[(.*)\],\[(.*)\],"(.*)",\[(.*)\],\[(.*)\],\[(.*)\],(".*")',line) #LM stands for LineMatch
	if not LM:
		print("error line not read\n", line)
		break
	print (LM.group(1)+"\t"+LM.group(2))
	q = And([QP.parse(LM.group(2)), Term('publishers', LM.group(5).lower()), Term('developers',LM.group(4).lower())])
	results = searcher.search(q, limit = 2)		
	if (LM.group(3)>'2003'):#skip games after 2002
		print("game skiped")
		continue;
	if len(results)==0:
		print("Adding as new tuple")
		idxwriter.update_document(GID=LM.group(1),name=LM.group(2),release_year=LM.group(3),developers=LM.group(4),publishers=LM.group(5),images=LM.group(6),sources=LM.group(7).replace('n/a',''),genres=LM.group(8).replace('n/a','').replace(',,',','),consoles = LM.group(9), description=LM.group(10))
	else:
		print("merging with:",results[0]['GID'],results[0]['name'])
		if results[0]['release_year']>LM.group(3) and LM.group(3)!='n\a':#if they have different years take the smaller one
			year = LM.group(3)
		else:
			year = results[0]['release_year']
		if results[0]['images']=='n/a':#if an image doesn't already exist then try this new one
			picture = LM.group(6)
		else:
			picture = results[0]['images']
		if results[0]['description']=='n/a':#if a description doesn't already exist then try this new one
			desc = LM.group(10)
		else:
			desc = results[0]['description']
		oldSources = results[0]['sources'].split(',')#add any new sources to the sources list
		newSources = LM.group(7).replace('/',',').split(',')
		for item in newSources:
			if item not in oldSources:
				oldSources.append(item)
		Sources = ','.join(oldSources)
		oldGenres = results[0]['genres'].replace('n/a','').split(',')#add any new genres to the genres list
		newGenres = LM.group(8).replace('n/a','').replace('/',',').replace(',,',',').split(',')
		for item in newGenres:
			if item not in oldGenres:
				oldGenres.append(item)
		Genres = ','.join(oldGenres)
		consoles = results[0]['consoles']+','+ LM.group(9) #add the new console onto the list
		idxwriter.update_document(GID=results[0]['GID'],name=LM.group(2),release_year=year,developers=LM.group(4),publishers=LM.group(5),images=picture,sources=Sources,genres=Genres, consoles = consoles, description=desc)
searcher.close()
idxwriter.commit(optimize=True)