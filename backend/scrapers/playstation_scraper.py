#!/bin/python

#Austin Cari
#DOS_scraper.py

#This scraper goes alongside the web-app Retro Sounding, and is used to scrape raw data from Wikipedia (and maybe other sites)

#This script specifically scrapes all the games at THIS wikipedia article: Index of DOS games 

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
HUBpage = 'https://en.wikipedia.org/wiki/Index_of_DOS_games_('
pages_to_visit = ['https://en.wikipedia.org/wiki/List_of_PlayStation_games_(A%E2%80%93L)', 'https://en.wikipedia.org/wiki/List_of_PlayStation_games_(M%E2%80%93Z)']

references = []
for i in range(1, 100):
	references.append('[' + str(i) + ']')

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
			dates = []
			for date in cells[3:6]:
				dates.append(date.get_text().strip('\n'))
			for date in dates:
				print(date)
				if (date == 'Unreleased'):
					continue
				if(len(date.split(',')) == 2):
					print('true' + date.get_text().split(',')[1])
					if (int(date.get_text().split(',')[1]) < 2003):
						print('truer')
						if(re.search('redlink', cells[0].find('i').find('a')['href']) == None):
							valRows.append(row)
							break
				if(len(date.split(' ') == 2)):
					if (int(date.get_text().split(',')[1]) < 2003):
						if(re.search('redlink', cells[0].find('i').find('a')['href']) == None):
							valRows.append(row)
							break
				else:
					continue
		except (ValueError, TypeError, AttributeError):
			pass

	return valRows

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
	
	valRows = validateRows(initRows[:2])
	print(len(initRows))
	print(len(valRows))
	# data = extractData(valRows)

	# OutputFile = open('../csvs/dos.csv','a', encoding = "utf_16")
	# OutputFile.write("id,name,release_year,developers,publishers,image,src,genres,console,description\n")
	# outputformat = "{id},\"{name}\",{release_year},[{developers}],[{publishers}],\"{img_url}\",[{src_url}],[{genres}],[{console}],\"{description}\"\n"	#the format string for the output file writes

	# for entry in data:
	# 	outputString = outputformat.format(id = entry[0],name = entry[1],release_year = entry[2],developers = entry[3],publishers = entry[4],img_url = entry[5],genres = entry[7], description = entry[8], src_url=entry[6], console = "Microsoft DOS")
	# 	OutputFile.write(outputString)

	# total = nameRead
	# print('Analytics:')
	# print("--- %s seconds ---" % (time.time() - start_time))
	# print('Total titles scraped: ' + str(total))
	# print('% total with release years: ' + str(round(release_yearRead/total, 3) * 100) + '%')
	# print('% total with genres: ' + str(round(genresRead/total, 3) * 100) + '%')
	# print('% total with developer: ' + str(round(developerRead/total, 3) * 100) + '%')
	# print('% total with publisher: ' + str(round(publisherRead/total, 3) * 100) + '%')
	# print('% total with src_url: ' + str(round(src_urlRead/total, 3) * 100) + '%')
	# print('% total with img_url: ' + str(round(img_urlRead/total, 3) * 100) + '%')
	# print('% total with description: ' + str(round(descriptionRead/total, 3) * 100) + '%')

if __name__ == '__main__':
	main()