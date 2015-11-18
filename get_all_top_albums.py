"""
Author: Nicholas Hunt-Walker
Date: 6/22/2014

Initial Purpose: collect a list of the top hip hop albums from each year
	using Wikipedia. An example site is...

	http://en.wikipedia.org/wiki/1985_in_hip_hop_music
"""

import numpy as np 
import os
from pandas import DataFrame, Series
import mechanize
br = mechanize.Browser()

from bs4 import BeautifulSoup

def set_the_url(the_year):
	url = 'http://en.wikipedia.org/wiki/'
	url += the_year
	url += '_in_hip_hop_music'
	return url

def get_the_page(the_url, the_year, saveit=False):
	if the_url.startswith('http:'):
		htmlSource = br.open(the_url).get_data()

		if saveit == True:
			outdir = '/Users/Nick/Documents/data_science/hip_hop_history/all_top_albums/'
			fout = open(outdir+'hiphop_'+the_year+'.txt','w')
			fmt = '%s'
			fout.write(fmt % htmlSource)

			fout.close()
			return htmlSource

		else:
			return htmlSource
	else:
		return None

def get_the_table(the_page, upload=None):
	if upload != None:
		os.chdir('/Users/Nick/Documents/data_science/hip_hop_history/all_top_albums/')
		the_page = open(upload).read()

	soup = BeautifulSoup(the_page)
	findit = soup.find('table','wikitable').text
	# return findit
	return soup

def get_the_albums(the_table):
	rows = the_table.find('table','wikitable').findAll('tr')
	heads = rows[0].findAll('th')
	columns = [d.contents[0] for d in heads]

	n = len(rows)
	ncols = len(columns)

	dates = np.zeros(n, dtype='S100')
	artists = np.zeros(n, dtype='S100')
	albums = np.zeros(n, dtype='S100')

	for ii in range(1,len(rows)):
		rowdata = rows[ii].findAll('td')
		tags = str(rowdata[0].unwrap())
		rowcols = [d.text for d in rowdata]



	rows = the_table.split('\n\n')
	theads = rows[1].split('\n')
	tdata = rows[2:-1]
	valid = [row for row in tdata if row != u'']

	n = len(valid)
	ncols = len(theads)

	dates = np.zeros(n, dtype='S100')
	artists = np.zeros(n, dtype='S100')
	albums = np.zeros(n, dtype='S100')

	for ii in range(n):
		step1 = valid[ii].split('\n')
		if len(step1) < ncols+1:
			if len(step1) == 2:
				dates[ii] = dates[ii-1]
				artists[ii] = artists[ii-1]
				albums[ii] = step1[1]

			else:
				dates[ii] = dates[ii-1]
				artists[ii] = step1[1]
				albums[ii] = step1[2]
		else:
			dates[ii] = step1[1]
			artists[ii] = step1[2]
			albums[ii] = step1[3]

	the_year_results = DataFrame({'Release':dates, 'Artist':artists, 'Albums':albums})
	return the_year_results

# years = np.arange(1985, 2014, 1)
# for ii in range(len(years)):
# 	yr = str(years[ii])
# 	# the_url = set_the_url(yr)
# 	# the_page = get_the_page(the_url, yr)
# 	the_table = get_the_table(the_page, upload='hiphop_'+yr+'.txt')
# 	the_albums = get_the_albums(the_table)

os.chdir('/Users/Nick/Documents/data_science/hip_hop_history/')





