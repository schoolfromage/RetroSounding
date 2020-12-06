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
starter = "https://en.wikipedia.org/w/api.php?action=parse&page="	#used for all queries
URLstarter = "https://en.wikipedia.org/wiki/"	#used for the investigate_further and the URL

def manageArgs():
	if (len(argv)!=4):
		print("wiki_to_csv.py [URL] [section #] [FILE]\n")
		return -1
	else:
		global mainPage
		mainPage = argv[1]
		global sectionNumb
		sectionNumb = argv[2]
		global outputName
		outputName = argv[3]
		return 0

		
def investigate_further(Target):
	if (Target == None):
		return "n/a","n/a","[n/a]","n/a"#return junk
	#split the section name (#) from the target
	Split = Target.split('#')
	Name = Split[0].replace('/wiki/',''	)
	if (len(Split)>1):
		SectionNumb = get_section_number(Name, Split[1])
	else:
		SectionNumb = None
	if (SectionNumb == None):
		prompt = starter+Name+"&prop=text&format=json&redirects"
	else:
		prompt = starter+Name+"&section="+SectionNumb+"&prop=text&format=json&redirects"
	time.sleep(0.5)
	req = requests.get(prompt)
	Listfile = json.loads(req.text)
	if "error" in Listfile:
		(Name+" is not on wikipedia")
		return "n/a","n/a","[n/a]","n/a"
	Text = Listfile["parse"]["text"]["*"]
	store = lxml.html.fromstring(Text)
	URL = URLstarter+Listfile["parse"]["title"].replace('_',',')
	TempList = store.xpath("//table[contains(@class,'infobox')]//a[@class='image']/img/@src")
	if len(TempList)>=1:
		Picture = TempList[0]
	else:
		Picture = "n/a"
	Genres = store.xpath("//th/a[text()='Genre(s)']/../following::td[1]//text()")
	Genres = [item for item in Genres if item != ' ']
	if Genres == "[]":
		Genres = "n/a"
	Paragraphs = store.xpath("//h2/span[@id='Gameplay']/../following::p[position()<=2]")
	if len(Paragraphs)==0:#if no "gameplay" section just default to front
		Paragraphs = store.xpath("//div[@class='mw-parser-output']/p[position()<=2]")
	if len(Paragraphs)==1:#if only one paragraph, just use that
		Discription = Paragraphs[0].text_content().replace("\n", "")#no newlines!
	else:#default behavior
		if (len(Paragraphs)>=2):
			Discription = Paragraphs[0].text_content().replace("\n", "")+" <br /> "+Paragraphs[1].text_content().replace("\n", "")
			Discription = re.sub(r'\[[^\[]*\]','',Discription)
		else:
			Discription = "n/a"
	return URL, Picture, Genres, Discription

def get_section_number(Name, Section):
	prompt = starter+Name+"&prop=sections&format=json&redirects"
	time.sleep(0.5)
	req = requests.get(prompt)#the HTML request to wikipedia
	Listfile = json.loads(req.text)#turning the JSON into a dictionary
	if "error" in Listfile:
		return None#the other function will print error codes
	for item in Listfile["parse"]["sections"]:
		if item["anchor"] == Section:
			return item["number"]
	return None
	
def cleanup_year(year):#finds the first sequence of 4 numbers for a year
	if (year != None):
		match = re.findall(r'[0-9]{4}',year)
		if match!=[]:
			return min(match)#find and only save the 4 sequencial numbers
		else:
			return "n/a"
	else:
		return "n/a"
	
def Scrape(file):
	outputformat = "{id},\"{name}\",{release_year},[{developers}],[{publishers}],\"{img_url}\",[{src_url}],{genres},[{console}],\"{description}\"\n"	#the format string for the output file writes
	prompt = starter+mainPage+"&section="+sectionNumb+"&prop=text&format=json&redirects"
	parser = etree.XMLParser(encoding='utf-8', recover=True)
	req = requests.get(prompt)#the HTML request to wikipedia
	Listfile = json.loads(req.text)#turning the JSON into a dictionary
	if "error" in Listfile:
		print(mainPage+" is not on wikipedia")
		return
	MainText = Listfile["parse"]["text"]['*']#turning the dictionary into HTML text
#	MainText = "<table class='wikitable'>Hello my name is <a>Pedro</a>, and I like crayons</table>"
	store = lxml.html.fromstring(MainText)#turning the HTML text into a lxml etree
	tableData = store.xpath("//table//tr")
	print(len(tableData))
	i = 2999
	for row in tableData:
		data = row.findall(".//td")
		if (len(data)>9):
			Link = data[0].find(".//a[1]")
			if Link!=None:
				Name = Link.text_content().replace("(video game)","")
				Link = Link.attrib['href']
			else:
				Name = data[0].text_content().replace("\n", "").replace("(video game)","")#some wiki pages need the extra tag; we don't
			print(Name)
			Devs = data[3].text_content().replace("\n", "")
			if Devs == "":
				Devs = 'n/a'
			Pubs = data[4].text_content().replace("\n", "")
			if Pubs == "":
				Pubs = 'n/a'
			year = cleanup_year(data[5].text_content())
			i+=1
			URL, Picture, Genres, Discription = investigate_further(Link)	#get image, genres, and descriptions
			outputString = outputformat.format(id = i,name = Name,release_year = year,developers = Devs,publishers = Pubs,img_url = Picture,genres = Genres, description = Discription, src_url=URL, console = "GBC")
			file.write(outputString)
		else:
			print("this row does not have enough data?")
			result = etree.tostring(row,pretty_print=True, method="html")
			print(result)

#The main function
if (manageArgs()==0):
	OutputFile = open(outputName,'a', encoding = "utf_16")
	OutputFile.write("id,name,release_year,developers,publishers,image,src,genres,console,description\n")
	Scrape(OutputFile)
	OutputFile.close()
	#Picture, Genres, Description = investigate_further("The_3-D_Battles_of_WorldRunner")
	#print(Picture)
	#print(Genres)
	#print(Description)
	#test = get_section_number("apple","Cultivars")
	#print(test)