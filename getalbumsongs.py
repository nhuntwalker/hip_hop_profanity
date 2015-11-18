"""
Author: Nicholas Hunt-Walker
Date: 6/7/2014

Purpose:  Screw the wiki pages for each album. Let's just go
	straight to songlyrics.com after we get the info from the top page
"""
import numpy as np
import os
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
import re
import urllib
import mechanize
br = mechanize.Browser()

from bs4 import BeautifulSoup
import time
import datetime
import funcs
import pickle
from scipy import misc

#################################################################
## Let's start by getting the top information
#################################################################
# os.system('curl http://en.wikipedia.org/wiki/List_of_best-selling_hip_hop_albums_in_the_United_States > wikitext.txt')
data = open('wikitext.txt').readlines()

keepthis = []
for line in data:
	if (line.startswith('<t') == True) & (line.startswith('<title>') == False):
		keepthis.append(line.replace('&amp;','&'))

keepthis = keepthis[3:]

#################################################################
## Let's get our column headers
#################################################################
colheads = []
for line in keepthis:
	if line.startswith('<th>'):
		clean1 = line.split('b>')
		clean2 = clean1[1].split('<')
		colheads.append(clean2[0])

#################################################################
## Now let's parse our actual data
#################################################################
tdata = keepthis[9:]
alldata = {}
for tit in colheads:
	alldata[tit] = []


#################################################################
## Get the data!
#################################################################
albumURLs = []
labcnt = 0
salescnt = 0
for i in range(len(tdata)):
	if tdata[i].startswith('<tr>'):
		for jj in range(len(colheads)):
			alldata[colheads[jj]].append(funcs.clean_off_html(tdata[i+jj+1]))
			if colheads[jj] == 'Label':
				line = tdata[i+jj+1]
				dum1 = line.split('">')

				if dum1[1].find('<a') != -1:
					labelstr = []
					for dum2 in dum1:
						if '</a>' in dum2:
							labelstr.append(dum2.split('</a>')[0])
					alldata[colheads[jj]][labcnt] = '/'.join(labelstr)

				else:
					alldata[colheads[jj]][labcnt]=funcs.clean_off_html(tdata[i+jj+1])
				labcnt += 1

			if colheads[jj] == 'Sales (millions)':
				line = tdata[i+jj+1].split()
				if len(line) > 1:
					dum1 = line[0].split('<td>')[1]
					alldata[colheads[jj]][salescnt] = dum1
				elif (len(line) == 1) & (line[0].endswith('</td>') == False):
					dum1 = line[0].split('<td>')[1]
					alldata[colheads[jj]][salescnt] = dum1


				salescnt += 1

			if colheads[jj] == 'Album':
				albumURLs.append(tdata[i+jj+1].split()[1][6:-1])


musicinfo = DataFrame(alldata)

musicinfo.Year = musicinfo.Year.astype(float)
musicinfo['Sales (millions)'] = musicinfo['Sales (millions)'].astype(float)


# # #################################################################
# # ## Let's get the album URLs from songlyrics.com 
# # #################################################################

# notfound = []
# all_urls = []
# for jj in range(len(musicinfo)):
# 	album = musicinfo.Album[jj]
# 	artist = musicinfo.Artist[jj]
# 	label = musicinfo.Artist[jj]
# 	year = musicinfo.Artist[jj]

# 	album_sanitized = funcs.sanitize_album_name(album)

# 	# ####################################################
# 	# ## This bit is solely for searching for albums
# 	# ## Once have data, comment out
# 	# ####################################################
# 	# instring = ' '.join((artist,album)).lower()
# 	# instring = instring.replace('(','')
# 	# instring = instring.replace(')','')
# 	# instring = instring.replace('.','')
# 	# instring = instring.replace(' ','+')

# 	# search_string = "http://www.songlyrics.com/index.php?section=search&searchW="
# 	# search_string += instring

# 	# htmlSource = funcs.retrieve_html(search_string)

# 	# outfile = open('new_albumsearch/%s.txt' % album_sanitized,'w')
# 	# outfile.write('%s' % htmlSource)
# 	# outfile.close()
# 	# ####################################################


# 	htmlSource = open('new_albumsearch/%s.txt' % album_sanitized).readlines()

# 	if album == 'Curtain Call: The Hits':
# 		album_alt = "Curtain Call"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == '...And Then There Was X':
# 		album_alt = "And Then There Was X"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == 'Graduation (album)':
# 		album_alt = "Graduation"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "I Am...":
# 		album_alt = "I Am"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "Licensed to Ill":
# 		album_alt = "Licensed to III"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "Flesh of My Flesh, Blood of My Blood":
# 		album_alt = "Flesh of My Flesh-Blood of My Blood"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "The Art of War":
# 		album_alt = "Art of War"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "The Blueprint2: The Gift & the Curse":
# 		album_alt = "The Blueprint 2: The Gift & The Curse"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "Chicken-n-Beer":
# 		album_alt = "Chicken N Beer"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "Mr. Smith":
# 		album_alt = "Mr Smith"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "2001":
# 		album_alt = "Chronic"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "Regulate...G Funk Era":
# 		album_alt = "Regulate G Funk Era"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "Creepin on ah Come Up":
# 		album_alt = "Creepin' On Ah Come Up"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	elif album == "Life Is... Too Short":
# 		album_alt = "Life Is...Too Short"
# 		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

# 	else:
# 		albumurl = funcs.find_the_album(htmlSource, album) # with songlyrics.com

# 	if albumurl == []:
# 		notfound.append(jj)
# 		all_urls.append('None')
# 	else: 
# 		all_urls.append(albumurl)	

# musicinfo['albumURLs'] = all_urls

#############################################
## Sincerely not found:
# 0 :	Friday OST
# 2 :	Kings of Crunk
# 12 :	Let's Get It Started
# 18 :	Me Against The World
# 28 :	Lōc-ed After Dark
# 34 :	Please Hammer, Don't Hurt 'Em
# 43 :	To the Extreme
# 103 :	Murda Muzik
#############################################


#####################################################
## Let's get the track urls from songlyrics.com...
## Note: They don't have all tracks for each album!
## Going to have to do some string matching here...
#####################################################

lyricsfiles = []

for ii in range(len(musicinfo.Album)):
	album = musicinfo.Album[ii]
	artist = musicinfo.Artist[ii]
	albumurl = musicinfo.albumURLs[ii]

	if albumurl != 'None':
		htmlSource = funcs.retrieve_html(albumurl)
		htmlLines = htmlSource.split('\n')

		# albumfile = bigdict[bigdict.keys()[jj]]['albumfile']
		# htmlSource = funcs.retrieve_htmlcode_from_file(albumfile)
		# htmlLines = htmlSource.split('\n')

		tableLines = []
		for jj in range(len(htmlLines)):
			if htmlLines[jj].find('<table class="tracklist">') != -1:
				tableLines.append(jj)

		jj = tableLines[0]
		songlines = []
		while htmlLines[jj].endswith('</table>') == False:
			if htmlLines[jj].split('\t')[-1].endswith('</a></td>'):
				songlines.append(htmlLines[jj].split('\t')[-1])
			jj += 1

		#################################################################
		## Splitting the song lines and collecting song names and URLs
		#################################################################
		songnames = []
		songurls = []
		lyrics = []

		for kk in range(len(songlines)):
			dum1 = songlines[kk].split('<')[2]
			dum2 = dum1.split('>')
			dum3 = dum2[1].split(' (')[0]
			songnames.append(dum3)

			dum3 = dum2[0].split('"')[1]
			songurls.append(dum3)

			lyrics.append(funcs.get_new_lyrics(songurls[kk], album, songnames[kk]))

		songurls = np.array(songurls)

		if lyrics != []:
			lyrics = np.array(lyrics, dtype='S200')
			lyricsfiles.append(lyrics)

nonemask = musicinfo.albumURLs != 'None'

#################################################################
## I screwed up, so I need to rewrite "musicinfo" data frame
#################################################################

musicinfo = musicinfo[nonemask]
musicinfo['Lyrics Files'] = lyricsfiles
pickle.dump(musicinfo, open('musicinfo.p','w'))

# #################################################################
# ## At this point, every song that has lyrics that are easily 
# ## found will have a downloaded page from songlyrics.com.  
# ## Let's start the next phase so that we can get some useful 
# ## data out.
# #################################################################

musicinfo = pickle.load(open('musicinfo.p'))

# #################################################################
# ## This is code doing a word analysis of Nas's I Am.
# ## Info is then plotted as a histogram
# #################################################################
# album_name = musicinfo.Album[ii]
# year = int(musicinfo.Year[ii])
# artist = musicinfo.Artist[ii]
# lyrics_list = musicinfo['Lyrics Files'][ii]

# words = funcs.word_counts_in_album(musicinfo.ix[ii])
# word_number_association = np.arange(0,len(words))
# word_counts = words.values()
# fig = plt.figure(figsize=(10,6))
# fig.subplots_adjust(top=0.9)
# plt.suptitle('Word Counts for\n%s - %s (%i)\n' % (album_name,artist,year))
# ax = plt.subplot(111)
# ax.bar(word_number_association, word_counts, width=1, alpha=0.5)
# ax.set_xticks(word_number_association+0.5)
# ax.set_ylabel('Counts')
# ax.set_xlim(-0.25,max(word_number_association)+1.25)
# ax.set_xticklabels(words.keys(), rotation=45)
# ax.minorticks_on()
# plt.show()
# #################################################################

over_time = []
badwords = ['nigga','bitch','fuck','shit']

for ii in musicinfo.index:
	album = musicinfo.Album[ii]
	year = int(musicinfo.Year[ii])
	artist = musicinfo.Artist[ii]

	word_count = funcs.word_counts_in_album(musicinfo.ix[ii], badwords, nigga_fold=True)
	word_count_list = word_count.values()
	word_count_list.append(year)
	over_time.append(word_count_list)

over_time = np.array(over_time)

colheads = [word[0].upper()+'*'*(len(word)-1) for word in badwords]
colheads.append('Year')

counts_df = DataFrame(over_time, columns=colheads)

over_time_cumulative = []
over_time_normed = []
years = []

for year in set(counts_df.Year):
	years.append(year)
	num_in_year = sum(counts_df.Year == year)
	cumulative_all = counts_df.ix[counts_df.Year == year].sum()
	normed_all = counts_df.ix[counts_df.Year == year].sum()/float(num_in_year)

	over_time_cumulative.append(list(cumulative_all[:-1]))
	over_time_normed.append(list(normed_all[:-1]))

over_time_cumulative = np.array(over_time_cumulative).T
over_time_normed = np.array(over_time_normed).T


plt.figure(figsize=(7,8))
plt.suptitle('Word Usage in \nTop Selling Hip Hop Albums')
ax = plt.subplot(211)
for i in range(len(badwords)):
	ax.plot(years, over_time_cumulative[i], marker='o')
ax.legend(colheads[:-1])
ax.minorticks_on()
ax.set_xlabel('Years')
ax.set_ylabel('Counts Per Year')

ax = plt.subplot(212)
for i in range(len(badwords)):
	ax.plot(years, over_time_normed[i], marker='o')
ax.minorticks_on()
ax.set_xlabel('Years')
ax.set_ylabel('Counts Per Year Per Album')

plt.savefig('money_plot.jpg')


covers = ['album_covers/'+f for f in os.listdir('./album_covers') if f.endswith('.jpg')]

imsize = 160
rows = 9
columns = 11

fig = plt.figure()
fig.subplots_adjust(bottom=0, top=1, left=0, right=1)
for ii in range(len(covers)):
	img = misc.imread(covers[ii])
	extent = [imsize*np.mod(ii,columns), imsize*(np.mod(ii,columns)+1), imsize*(np.mod(ii,rows)+1), imsize*np.mod(ii,rows)]
	plt.imshow(img, extent=extent)

plt.xlim(0,imsize*(np.mod(ii, columns)+1))
plt.ylim(imsize*(np.mod(ii, rows)+1), 0)
plt.axis('off')
plt.show()

