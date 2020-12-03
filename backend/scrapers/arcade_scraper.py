#!/bin/python

#Austin Cari
#arcade_scraper.py

#This scraper goes alongside the web-app Retro Sounding, and is used to scrape raw data from Wikipedia (and maybe other sites)

#This script specifically scrapes all the games at THIS wikipedia article: List of Arcade games

from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup as soup
import wikipedia
import time
import csv 
import json

start_time = time.time()

nameRead = 0
release_yearRead = 0
developerRead = 0
publisherRead = 0
img_urlRead = 0
src_urlRead = 0
genresRead = 0
descriptionRead = 0

URLstarter = "https://en.wikipedia.org"	#used only for the file output
HUBpage = 'https://en.wikipedia.org/wiki/List_of_arcade_video_games:_'
alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
pages_to_visit = []
for letter in alphabet:
	pages_to_visit.append(HUBpage + letter)

def getAllRows(url):
	rows = []
	#Make a request to Wikipedia and store the HTML
	client = urlopen(url)
	page_html = client.read()
	client.close()

	#Make some soup and grab every row from the main table in the body
	page_soup = soup(page_html, "html.parser")
	table = page_soup.find('tbody')
	allRows = table.findAll('tr')
	#Grab the single table form this page

	return allRows[1:]

def validateRows(rows):
	date = 0
	link = 0
	valRows = []

	for row in rows:
		try:
			cells = row.findAll('td')
			if (int(cells[2].get_text()) < 2003):
				if(cells[0].find('i').find('a') != None):
					valRows.append(row)
		except ValueError:
			pass

	return valRows

#This function is going to return the name, release year, developer, publisher, genre(s), src_urls, img_url and a description of the game
def extractData(rows):

	global nameRead
	global release_yearRead
	global developerRead 
	global publisherRead 
	global src_urlRead 
	global genresRead

	data = []
	id = 5000

	for row in rows:
		cells = row.findAll('td')

		# name
		name = (cells[0].find('i').find('a').get_text()).replace('\n', '')
		nameRead += 1
		
		# release year
		release_year = (cells[2].get_text()).replace('\n', '')
		release_yearRead += 1

		# developer
		developer = ('[' + cells[3].get_text() + ']').replace('\n', '')
		developerRead += 1
		if (len(developer) <= 2):
			developer = 'n/a'
			developerRead -= 1

		# publisher
		publisher = ('[' + cells[3].get_text() + ']').replace('\n', '')
		publisherRead += 1
		if (len(publisher) <= 2):
			publisher = 'n/a'
			publisherRead -= 1

		# genres
		genres = (cells[4].get_text()).replace('\n', '')
		genresRead += 1
		if (len(genres) == 0):
			genres = 'n/a'
			genresRead -= 1

		# src
		href = row.find('td').find('i').find('a')['href']
		link = URLstarter + href
		src = ('[' + link + ']').replace('\n', '')
		src_urlRead += 1

		# img & desc
		img = getImage(href, name, link)
		description = getDesc(href[6:]) 

		print(str((id, name, release_year, developer, publisher, img, src, genres, description)))
		data.append([id, name, release_year, developer, publisher, img, src, genres, description])
		id += 1
	return data

def getImage(href, name, link):
	global img_urlRead
	#Method #1: Grab the picture in the infobox using bs
	default = 'n/a'
	req = requests.get(link)
	page_soup = soup(req.text, "html.parser")

	#Get the infobox
	try:
		infobox = page_soup.find('table', {'class': 'infobox hproduct'})
		rows = infobox.find('tbody').findAll('tr')
	except AttributeError:
		pass

	#Get image from infobox
	try:
		image = infobox.find('a', {'class': 'image'})['href']
		img_src = URLstarter + image 
		if len(img_src) == 0:
			img_src = 'n/a'
		else:
			img_urlRead += 1
			return img_src
	except (TypeError, AttributeError):
		#no image is avaliable
		pass

	#Method 2: Search an array of images using Wikimedia API
	query = 'https://en.wikipedia.org/w/api.php?action=query&prop=images&format=json&titles=' + href
	print(query)

	images = []
	try:
		client = urlopen(query)
		data = json.loads(client.read())
		pids = data['query']['pages']
		pid = 0
		for page in pids:
			pid = page
		images = pids[pid]['images']
	except KeyError:
		pass

	# Search for the first image that matches the title or 'box art' or 'cover art'
    # Use regular expressions for this
	for image in images:
		title = image['title']
		if ((re.search('box art', title) != None) or 
		(re.search('box-art', title) != None) or 
		(re.search('box_art', title) != None) or 
		(re.search('boxart', title) != None) or
		(re.search('cover_art', title) != None) or
		(re.search('cover art', title) != None) or
		(re.search('cover-art', title) != None) or
		(re.search('coverart', title) != None) or
		(re.search(name, title) != None) or
		(re.search(name.replace(' ', '-'), title) != None) or
		(re.search(name.replace(' ', '_'), title) != None) or
		(re.search(name.replace(' ', ''), title) != None)):
			parameters = urlencode({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url", 'format': 'json'})
			newQ = 'https://en.wikipedia.org/w/api.php?' + parameters
			client = urlopen(newQ) #This is where I'm getting the error
			data = json.loads(client.read())['query']['pages']
			pid = 0
			for page in data:
				pid = page
			img_url = data[pid]['imageinfo'][0]['url']
			img_urlRead += 1
			return img_url
	return default

def getDesc(href):
	global descriptionRead
	default = 'No description for this title'
	query = 'https://en.wikipedia.org/w/api.php?action=query&format=json&titles=' + href
	client = urlopen(query)
	res = json.loads(client.read())
	try:
		for page in res['query']['pages']:
			pid = page
		try:
			mypage = wikipedia.page(pageid=pid)
			descriptionRead += 1
			return mypage.summary.replace('\n', ' ')
		except AttributeError:
			pass
	except KeyError:
		return default

	try:
		descriptionRead += 1
		return wikipedia.summary(wikipedia.search(href + ' video game)')[0], sentences = 3).replace('\n', ' ')
	except IndexError:
		try:
			descriptionRead += 1
			return wikipedia.summary(href[6:], sentences = 3).replace('\n', ' ')
		except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
			pass
	except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
		pass
	return default

def main():
	global nameRead
	global release_yearRead
	global developerRead 
	global publisherRead 
	global src_urlRead 
	global genresRead
	global img_urlRead
	global descriptionRead
	global pages_to_visit

	initRows = []

	for page in pages_to_visit:
		initRows.extend(getAllRows(page))
	
	valRows = validateRows(initRows)
	
	data = extractData(valRows)

	with open('arcade_results.csv', 'w', newline = '') as f:
		writer = csv.writer(f)

		writer.writerow(['id, name, release year, developer, publisher, img_url, src_url, genres, description'])

		for row in data:
			try:
				writer.writerow(row)
			except UnicodeError:
				nameRead -= 1
				release_yearRead -= 1
				developerRead -= 1
				publisherRead -= 1
				img_urlRead -= 1
				src_urlRead -= 1
				genresRead -= 1
				descriptionRead -= 1

	total = nameRead
	print('Analytics:')
	print("--- %s seconds ---" % (time.time() - start_time))
	print('Total titles scraped: ' + str(total))
	print('% total with release years: ' + str(round(release_yearRead/total, 3) * 100) + '%')
	print('% total with genres: ' + str(round(genresRead/total, 3) * 100) + '%')
	print('% total with developer: ' + str(round(developerRead/total, 3) * 100) + '%')
	print('% total with publisher: ' + str(round(publisherRead/total, 3) * 100) + '%')
	print('% total with src_url: ' + str(round(src_urlRead/total, 3) * 100) + '%')
	print('% total with img_url: ' + str(round(img_urlRead/total, 3) * 100) + '%')
	print('% total with description: ' + str(round(descriptionRead/total, 3) * 100) + '%')

if __name__ == '__main__':
	main()