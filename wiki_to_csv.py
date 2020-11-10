#for managing the wikipedia requests
import requests
import json
#for parsing html tags
from lxml import etree
from io import StringIO
import lxml.html 
# for the waiting
import time
#for managing command line arguments
from sys import argv


outputformat = "{id},{name},{release_year},[{developers}],[{publisher}],{img_url},{src_url},[{genres}],\"{description}\"\n"	#the format string for the output file writes
starter = "https://en.wikipedia.org/w/api.php?action=parse&page="	#used for all queries
URLstarter = "https://en.wikipedia.org/wiki/"	#used only for the file output
checkedPages = []

#inputManagement
#args = argv
def manageArgs():
	if (len(argv)!=4):
		print("wiki_to_csv.py [URL] [section #] [FILE]\n")
		return -1;
	else:
		global mainPage
		mainPage = argv[1]
		global sectionNumb
		sectionNumb = argv[2]
		global outputName
		outputName = argv[3]
		return 0;

def investigate_further(Name):
	prompt = starter+Name+"&prop=text&format=json&redirects"
	time.sleep(0.5)
	print("looking at ", Name)
	req = requests.get(prompt)
	Listfile = json.loads(req.text)
	if "error" in Listfile:
		print(Name+" is not on wikipedia")
		return "n/a","n/a","n/a","n/a"
	Text = Listfile["parse"]["text"]["*"]
	store = lxml.html.fromstring(Text)
	URL = URLstarter+Listfile["parse"]["title"]
	TempList = store.xpath("//a[@class='image']/@href")
	if len(TempList)>=1:
		Picture =  URLstarter+TempList[0]
	else:
		Picture = "n/a"
	Genres = store.xpath("//th/a[text()='Genre(s)']/../following::td[1]//text()")
	Genres = [item for item in Genres if item != ' ']
	Paragraphs = store.xpath("//h2/span[@id='Gameplay']/../following::p[position()<=2]")
	if len(Paragraphs)==0:#if no "gameplay" section just default to front
		Paragraphs = store.xpath("//div[@class='mw-parser-output']/p[position()<=2]")
	if len(Paragraphs)==1:#if only one paragraph, just use that
		Discription = Paragraphs[0].text_content().replace("\n", "")#no newlines!
	else:#default behavior
		Discription = Paragraphs[0].text_content().replace("\n", "")+" \\n "+Paragraphs[1].text_content().replace("\n", "")
	
	return URL, Picture, Genres, Discription
	
def Scrape(file):
	prompt = starter+mainPage+"&section="+sectionNumb+"&prop=text&format=json&redirects"
	print("asking "+prompt)
	#parser = etree.XMLParser(encoding='utf-8', recover=True)
	req = requests.get(prompt)
	Listfile = json.loads(req.text)
	if "error" in Listfile:
		print(mainPage+" is not on wikipedia")
		return
	MainText = Listfile["parse"]["text"]['*']
#	MainText = "<table class='wikitable' id='softwarelist'>testing testing testing</table>"
#	MainText = "<table class='wikitable'>Hello my name is <a>Pedro</a>, and I like crayons</table>"
	#store = etree.parse(StringIO(MainText), parser)
	store = lxml.html.fromstring(MainText)
	tableData = store.xpath("//table[@id='softwarelist']//td")
	# for item in tableData:
		# print(item.text_content())
	i=0
	j=0
	while (i<len(tableData)):
	#while (i<12):
		Name = tableData[i].text_content().replace("\n", "")
		#print("name:",tableData[i].text_content())
		Devs = tableData[i+1].text_content().replace("\n", "")
		#print("devs:",tableData[i+1].text_content())
		Publisher = tableData[i+2].text_content().replace("\n", "")
		#print("NApubs:",tableData[i+2].text_content())
		#print("EUpubs:",tableData[i+3].text_content())
		year = tableData[i+4].text_content().replace("\n", "")
		#print("NAdate",tableData[i+4].text_content())
		#print("EUdate",tableData[i+5].text_content())
		#print("rowend\n")
		URL, Picture, Genres, Discription = investigate_further(Name.replace(" ","_"))	#get image, genres, and descriptions
		i+=6;
		j+=1;
		outputString = outputformat.format(id = j,name = Name,release_year = year,developers = Devs,publisher = Publisher,img_url = Picture,genres = Genres, description = Discription, src_url=URL)
		file.write(outputString)
	
#the main function
if (manageArgs()==0):
	OutputFile = open(outputName,'a', encoding = "utf_16")
	OutputFile.write("id,name,release_year,publisher,image,src,genres,description\n")
	Scrape(OutputFile);
	OutputFile.close()
	#Picture, Genres, Description = investigate_further("The_3-D_Battles_of_WorldRunner")
	#print(Picture)
	#print(Genres)
	#print(Description)