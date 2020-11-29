#Austin Cari
#scraper.py

#This scraper goes alongside the web-app Retro Sounding, and is used to scrape raw data from Wikipedia (and maybe other sites)

#This script specifically scrapes all the games at THIS wikipedia article: List of Macintosh games

from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup as soup
from lxml import etree
import wikipedia
import time
import csv 

outputformat = "{id},{name},{release_year},[{developers}],[{publisher}],{img_url},{src_url},[{genres}],\"{description}\"\n"	#the format string for the output file writes
starter = "https://en.wikipedia.org/w/api.php?action=parse&page="	#used for all queries
URLstarter = "https://en.wikipedia.org"	#used only for the file output
HUBpage = 'https://en.wikipedia.org/wiki/List_of_Macintosh_games'
checkedPages = []

#There is a table of games for each letter of the alphabet. Parse all 27 tables and grab each row
def getAllRows():
	rows = []
	#Make a request to Wikipedia and store the HTML
	client = urlopen(HUBpage)
	page_html = client.read()
	client.close()

	#Make some soup and grab every row from the main table in the body
	page_soup = soup(page_html, "html.parser")
	tables = page_soup.find_all('tbody')
	#Cut out extra tables that are just in the page
	tables = tables[2:29]

	for table in tables:
		rows.extend(table.findAll('tr')[1:])

	return rows

#Check to make sure title was released before or on 2000.
def validateRows(rows):
	valRows = []

	for row in rows:
		try:
			if(int(row.findAll('td')[1].get_text()) < 2003):
				if(row.find('th').find('i').find('a') != None):
					valRows.append(row)
		except IndexError:
			continue
		except ValueError:
			continue
		except AttributeError:
			continue
	return valRows

def extractData(rows):
	data = []
	id = 1000 #Must increment ID, but dont fuck with Steven's existing data
	for row in rows:
		name = str(row.find('th').get_text().replace('\n', ''))
		release_year = row.findAll('td')[1].get_text().replace('\n', '')
		genres = row.findAll('td')[2].get_text().replace('\n', '')
		if (len(genres) == 0):
			genres = 'n/a'
		developer = ('[' + row.findAll('td')[0].get_text().replace('\n', '') + ']').replace('\"', '')
		if (len(developer) <= 2):
			developer = 'n/a'
		publisher = ('[' + row.findAll('td')[0].get_text().replace('\n', '') + ']').replace('\"', '')
		if (len(publisher) <= 2):
			publisher = 'n/a'

		#Grab the link to each title and visit that page, grabbing these attrs at that page
		href = row.find('th').find('i').find('a')['href']
		link = URLstarter + href
		src_url = link
		img_url = visitPage(link)

		print(str((id, name, release_year, developer, publisher, img_url, src_url, genres)))
		data.append([id, name, release_year, developer, publisher, img_url, src_url, genres, 'description'])
		id += 1
	return data

def visitPage(link):
	img_src = 'n/a'
	description = 'description'

	req = requests.get(link)
	page_soup = soup(req.text, "html.parser")

	#Get the infobox
	try:
		infobox = page_soup.find('table', {'class': 'infobox hproduct'})
		rows = infobox.find('tbody').findAll('tr')
	except AttributeError:
		#Some links just redirect to irrelevant pages, so there is no infobox to grab
		return

	#Get image from infobox
	try:
		image = infobox.find('a', {'class': 'image'})['href']
		img_src = URLstarter + image
		if len(img_src) == 0:
			img_src = 'n/a'
	except TypeError:
		#no image is avaliable
		pass

	return img_src

def main():

	rows = getAllRows()
	
	#Not all the rows in this article are 'retro'. Weed out anything after 2000
	#or that doesnt have a link
	valRows = validateRows(rows)
	
	data = extractData(valRows)
	with open('macontish_results.csv', 'w', newline = '') as f:
		writer = csv.writer(f)

		writer.writerow(['id, name, release year, developer, publisher, img_url, src_url, genres, description'])

		for row in data:
			print(row)
			writer.writerow(row)

if __name__ == '__main__':
	main()