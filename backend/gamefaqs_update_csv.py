#for managing the wikipedia requests
import requests
import json
#for managing the html
from lxml import etree
from io import StringIO
import lxml.html 
#for managing command line arguments
from sys import argv
# for the waiting
import time
#for the format fixing
import re

#Steven A
#This program will go through the gamefaqs pages and add the gamefaqs link to available games
#if a game is not already on the DB it will not be recorded
#if a game is recorded but is missing a description or a picture this program will attempt to fix that
#the reference csv (sourceName) is refered to in order to access whether a game exists, and what GID to use for that game

starter = "https://gamefaqs.gamespot.com"	#used for all queries
customHeaders = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"}

def manageArgs():
	if (len(argv)!=4):
		print("wiki_to_csv.py [URL] [section #] [FILE]\n")
		return -1
	else:
		global sectionName
		sectionName = argv[1]
		global sourceName
		sourceName = argv[2]
		global outputName
		outputName = argv[3]
		return 0

		
def investigate_further(Target, needPic, needDesc):
	if (Target == None):
		return "n/a","n/a","[]","n/a"#return junk
	prompt = starter+Target
	time.sleep(0.5)
	req = requests.get(prompt, headers=customHeaders)#the HTML request to gamefaqs
	if not req:
		print("page error")
		return "n/a","n/a","[]","n/a"#return junk
	URL = prompt
	store = lxml.html.fromstring(req.text)
	Genres = '['+store.xpath("//b[contains(text(),'Genre:')]/../a")[0].text_content()+']'
	if needDesc:	
		Discription = store.xpath("//h2[contains(text(),'Description')]/../../div")[1].text_content().strip().replace("\n","</n>")
	else:
		Discription="n/a"
	if needPic:
		time.sleep(0.5)
		req = requests.get(prompt+"/images", headers=customHeaders)
		store = lxml.html.fromstring(req.text)
		Picture = store.xpath("//img[@class='imgboxart']/@src")
		if Picture:
			Picture = Picture[0]
		else:
			Picture = "n/a"
	else:
		Picture = "n/a"
	return URL, Picture, Genres, Discription


def getAssociations():#this will get and return a dictionary of name:id pairs ; this is used for checking if a game exists
	otherCsv = open(sourceName, 'r', encoding = "utf_16")
	global gameIDs
	global needPics
	global needDescriptions
	needPics = {}
	gameIDs = {}
	needDescriptions = {}
	for line in otherCsv.readlines()[1:]:
		data = re.match(r'([^,]*),"(.*)",([^,]*),\[(.*)\],\[(.*)\],"(.*)",\[(.*)\],\[(.*)\],\[(.*)\],"(.*)"',line)
		gameIDs[data.group(2)]=data.group(1)
		needPics[data.group(2)]=(data[6]=='n/a')
		needDescriptions[data.group(2)]=(data[10]=='n/a')
	otherCsv.close()
	#print(gameIDs)
	#print(needPics)
	#print(needDescriptions)
	
def Scrape(file):
	outputformat = "{id},\"{name}\",{release_year},[{developers}],[{publishers}],\"{img_url}\",[{src_url}],{genres},[{console}],\"{description}\"\n"	#the format string for the output file writes
	prompt = starter+sectionName
	print(prompt)
	parser = etree.XMLParser(encoding='utf-8', recover=True)
	req = requests.get(prompt, headers=customHeaders)#the HTML request to gamefaqs
	if req == None:
		print(mainPage+" is not on gamefaqs")
		# return
	MainText = req.text
#	print(MainText)
#	MainText = "<table class='wikitable'>Hello my name is <a>Pedro</a>, and I like crayons</table>"
	store = lxml.html.fromstring(MainText)#turning the HTML text into a lxml etree
	tableData = store.xpath("//table[@class='results']//tr")
	print(len(tableData))
	for row in tableData:
		time.sleep(2)#gamespot has a system for blocking scrapers that go to fast so I must be sloow
		data = row.findall(".//td")
		name = data[0].text_content()
		if name.endswith(", The"):
			name = name.replace(", The","")#take out ending
			name = "The "+name#add new begining
		if name in gameIDs:#ie: if already recorded
			#print("need disc?", needDescriptions[name])
			Link = data[0].find(".//a")
			if Link!=None:
				Link = Link.attrib['href']
				print(Link)
			else:
				print("no link found")
				continue;#if game has no link there there is no point to being here
			print(name,"\td",needDescriptions[name],"\tp", needPics[name])
			Devs = 'n/a'
			Pubs = 'n/a'
			year = 'n/a'
			URL, Picture, Genres, Discription = investigate_further(Link, needPics[name], needDescriptions[name])	#get image, genres, and descriptions
			outputString = outputformat.format(id = gameIDs[name],name = name,release_year = year,developers = Devs,publishers = Pubs,img_url = Picture,genres = Genres, description = Discription, src_url=URL, console = "A2600")
			file.write(outputString)
		
#The main function
if (manageArgs()==0):
	OutputFile = open(outputName,'a', encoding = "utf_16")
	#OutputFile.write("id,name,release_year,developers,publishers,image,src,genres,console,description\n")
	getAssociations()
	for x in range(1,28):
		sectionName = "/appleii/alpha/"+str(x)+"-"+chr(97+(x-1))
		Scrape(OutputFile)
		time.sleep(20)
	OutputFile.close()
	#URL, Picture, Genres, Description = investigate_further("/atari2600/926728-tetris", True, True)
	#print(URL)
	#print(Picture)
	#print(Genres)
	#print(Description)