from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED, NUMERIC

import re
from sys import argv

#this program does not make the directory by itself
#this program expects the following format from the csvs:
#id,[name],release_year,[developer(s)],[publisher(s)],[image(s)],[src(s)],[genre(s)],"description"

inputFile = argv[1]
outputDir = argv[2]

schema = Schema(GID=ID(stored=True, unique=True),#GID = Game ID
	name=KEYWORD(stored=True),
	release_year=NUMERIC(stored=True),
	developers=KEYWORD(stored=True, commas=True),
	publishers=KEYWORD(stored=True, commas=True),
	images=KEYWORD(stored=True, commas=True),
	sources=KEYWORD(stored=True, commas=True),
	genres=KEYWORD(stored=True, commas=True),
	description=TEXT(stored=True)
	)

if not index.exists_in(outputDir):
	idx = index.create_in(outputDir,schema = schema)
else:
	idx = index.open_dir(outputDir)	

FileInput = open(inputFile, 'r', encoding = "utf_16")
if not FileInput:
	print("error file not read")
List = FileInput.readlines()
idxwriter= idx.writer()
for line in List[1:]:
	LM = re.match(r'([^,]*),\[(.*)\],([^,]*),\[(.*)\],\[(.*)\],\[(.*)\],\[(.*)\],\[(.*)\],(".*")',line) #LM stands for LineMatch
	if not LM:
		print("error line not read", line)
		break
	print (LM.group(1)+"\t"+LM.group(2))
	idxwriter.update_document(GID=LM.group(1),name=LM.group(2),release_year=LM.group(3),developers=LM.group(4),publishers=LM.group(5),images=LM.group(6),sources=LM.group(7),genres=LM.group(8),description=LM.group(9))

