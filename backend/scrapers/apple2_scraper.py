#!/bin/python

#Austin Cari
#apple2_scraper.py

#This scraper goes alongside the web-app Retro Sounding, and is used to scrape raw data from Wikipedia (and maybe other sites)

#This script specifically scrapes all the games at THIS wikipedia article: List of Apple II games

from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup as soup
import wikipedia
import time
import csv 
import json
import re

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
HUBpage = 'https://en.wikipedia.org/wiki/List_of_Apple_II_games'

def getAllRows(url):
	rows = []
	#Make a request to Wikipedia and store the HTML
	client = urlopen(url)
	page_html = client.read()
	client.close()

	#Make some soup and grab every row from the main table in the body
	page_soup = soup(page_html, "html.parser")
	table = page_soup.find('table', {'class': 'wikitable sortable'})
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
			if (int(cells[1].get_text()) < 2003):
				if(cells[0].find('i').find('a') != None):
					valRows.append(row)
		except (ValueError, AttributeError):
			pass

	return valRows

def extractData(rows):

	global nameRead
	global release_yearRead
	global developerRead 
	global publisherRead 
	global src_urlRead 
	global genresRead

	data = []
	id = 7000

	for row in rows:
		cells = row.findAll('td')

		# name
		name = (cells[0].find('i').find('a').get_text()).replace('\n', '')
		nameRead += 1
		
		# release year
		release_year = (cells[1].get_text()).replace('\n', '')
		release_yearRead += 1

		# developer
		developer = ('[' + cells[2].get_text() + ']').replace('\n', '')
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


		# src
		href = row.find('td').find('i').find('a')['href']
		link = URLstarter + href
		src = ('[' + link + ']').replace('\n', '')
		src_urlRead += 1

		# img & desc & genres
		img = getImage(href, name, link)
		description = getDesc(href[6:]) 
		if(re.search('Jeopardy!', name) != None):
			genres = 'Trivia'
		elif(re.search('Space', name) != None):
			genres = 'Space'
		else:
			genres = getGenre(link)

		if(developer != 'n/a') and (publisher == 'n/a'):
			publisher = developer
		elif(developer == 'n/a') and (publisher != 'n/a'):
			developer = publisher

		#print(str((id, name, release_year, developer, publisher, img_url, src_url, genres, description[:50])))
		print(str((name, genres)))
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

def getGenre(link):
	global genresRead
	default = 'n/a'
	result = ''
	req = requests.get(link)
	page_soup = soup(req.text, "html.parser")
	try:
		infobox = page_soup.find('table', {'class': 'infobox vevent'})
		if(infobox == None):
			infobox = page_soup.find('table', {'class': 'infobox hproduct'})
	except AttributeError:
		print('no infobox')
		return default

	genres = ['Action Game', 'Fighting game', 'Platform game', 'Shooter game', 'Beat \'em up', 'Shoot \'em up', 'Stealth game', 'Survival game', 'Battle royale game', 'Rhythm game', 'Action-adventure game', 'Survival horror', 'Adventure game', 'Role-playing video game', 'Action role-playing game', 'Massively multiplayer online role-playing game', 'Roguelike', 'Tactical role-playing game', 'Sandbox game', 'Simulation video game', 'Life simulation game', 'Vehicle simulation game', 'Strategy video game', '4X game', 'Artillery game', 'Auto battler', 'Real-time strategy', 'Real-time tactics', 'Tower defense', 'Turn-based tactics', 'Sports game', 'Massively multiplayer online game', 'Digital collectible card game', 'Horror game', 'Incremental game', 'Open world', 'Survival mode', 'God game', 'Interactive film', 'Puzzle adventure game', 'Racing video game', 'Train simulator', 'Run and gun', 'Educational game', 'Puzzle', 'Puzzle video game', 'Chess', 'Simulation video game', 'Interactive fiction', 'First-person shooter', 'Strategy game', 'Point-and-click adventure', 'Adventure game', 'Business simulation game', 'Graphic adventure', 'Text adventure', 'Racing video game', 'Simulation', 'Combat flight simulation game', 'Sports video game', 'Combat flight simulator', 'Flight simulator', 'Point-and-click adventure game', 'Space trading and combat simulator', 'Role-playing game', 'Action game', 'Puzzle game', 'First-person adventure', 'Educational video game', 'Tile-matching video game', 'Space combat sim', 'Platformer', 'Turn-based strategy game', 'Fantasy', 'Animation', 'Tactical shooter', 'MOBA', 'Sim racing', 'Graphic adventure game', 'Edutainment', 'Sports', 'Multidirectional shooter', 'Video puzzle game', 'Amateur flight simulator', 'Survival horror', 'Light gun shooter', 'Adventure Game', 'Arcade', 'Construction and management simulation', 'Party game', 'Vehicular combat game', 'Simulation video games', 'Massively multiplayer online first-person shooter', 'Construction and management simulation games', 'Rail shooter', 'Third-person shooter', 'Gambling', 'City-building game', 'Construction and management simulation games', 'Educational', 'Top-down shooter', 'Third person shooter', 'Science fiction', 'Multidirectional shooter', 'action', 'action game', 'Wargame (video games)', 'Arcade game', 'Turn-based strategy', 'Scrolling shooter', 'Kart racing game', 'Simulation game', 'Computer strategy game', 'Strategy game', 'Combat', 'Naval warfare', 'Pinball', 'List of maze video games', 'Computer wargame', 'Racing', 'Action video game', 'action video game', 'Submarine simulator', 'Board game', 'Game creation system', 'Fixed shooter','Snake (video game)', 'Shoot &#39;em up', 'Metroidvania', 'Text-based game']
	#Get the infobox
	try:
		for genre in genres:
			gen = infobox.find('tbody').find('a', {'title': genre})
			if (gen != None):
				if(re.search(gen.get_text(), result) == None):
					result += (gen.get_text() + '/')
		if(len(result) > 0):
			genresRead += 1
			return result.strip('/')
		else:
			return default
	except AttributeError:
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

	initRows = getAllRows(HUBpage)
	
	valRows = validateRows(initRows)

	data = extractData(valRows)

	with open('../csvs/apple2_results.csv', 'w', newline = '') as f:
		writer = csv.writer(f)

		writer.writerow(['id, name, release year, developer, publisher, img_url, src_url, genres, description'])

		for row in data:
			try:
				writer.writerow(row)
			except UnicodeError:
				pass

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