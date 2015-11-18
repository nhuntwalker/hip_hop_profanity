"""
Author: Nicholas Hunt-Walker
Date: 5/31/2014

Purpose: Download information from wikipedia, parse the text, and 
	select information regarding hip hop albums

Rewriting: Screw the wiki pages for each album. Let's just go
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


alldata['Album URL'] = albumURLs


musicinfo = DataFrame(alldata)

musicinfo.Year = musicinfo.Year.astype(float)
musicinfo['Sales (millions)'] = musicinfo['Sales (millions)'].astype(float)

# plt.hist(musicinfo.Year, bins=range(1988,2014))
# # plt.scatter(musicinfo.Year, musicinfo['Sales (millions)'])
# plt.title("Number of Albums on RIAA\nList of Top Hip Hop Albums")
# plt.ylabel('# Albums')
# plt.xlabel("Year")
# plt.minorticks_on()
# plt.show()


#################################################################
## Now, we have our Album URLs.  Let's get the album pages...
#################################################################
fout = open('./albums/albumlist.txt','w')
fmt = "%s\n"

all_albums = []
for (album,url) in zip(musicinfo.Album, musicinfo['Album URL']):
	album = album.replace('?','')
	album = album.replace("'",'')
	album = album.replace('.','')
	album = album.replace(',','')
	album = album.replace(':','')
	album = album.replace('&','')
	album = album.replace('(','')
	album = album.replace(')','')
	album = album.replace('/','_')
	album = album.replace(' ','_')
	all_albums.append(album)

	url = url.replace('(','\(')
	url = url.replace(')','\)')

	# funcs.get_albumpage(url,album)


#################################################################
## And now the tracklist for each Album
## A couple notes:
## 	The album "Curtis" is linked to the wrong page
## 	The album "Friday OST" doesn't have "#track_listing" or 
## 		"#tracks_listing" or really any identifiable HTML code
##		for the track list
##  The album Loc-ed_After_Dark has the same problem as Friday
#################################################################


albums = ['albums/'+f+'.txt' for f in all_albums]
bigdict = {}

#################################################################
## Putting all the basic track info into a big dictionary
## Note, if the tracklisting format is a list, it got ignored
#################################################################
for jj in range(len(albums)):
	lines, inds = funcs.find_tracklist(albums[jj])
	if lines != []:
		tblines, tbhead = funcs.isolate_table(lines, inds)
		colheads = funcs.get_colheads(tblines, tbhead)
		if colheads != []:
			trackinfo = funcs.get_track_titletime(tblines, tbhead, colheads)
			# bigdict[albums[jj]] = {'artist':musicinfo.Artist[jj], 'year':musicinfo.Year[jj],'label':musicinfo.Label[jj],'tracks':trackinfo}
			bigdict[musicinfo.Album[jj]] = {'artist':musicinfo.Artist[jj], 'year':musicinfo.Year[jj],'label':musicinfo.Label[jj],'tracks':trackinfo,'albumfile':albums[jj]}


#################################################################
## Now we need to search for lyrics for all the songs on a given
## album.  Let's use songlyrics.com
#################################################################


notfound = []
for jj in range(len(bigdict)):
	album = bigdict.keys()[jj]
	albumdict = bigdict[bigdict.keys()[jj]]
	artist = bigdict[bigdict.keys()[jj]]['artist']
	label = bigdict[bigdict.keys()[jj]]['label']
	year = bigdict[bigdict.keys()[jj]]['year']
	tracks = bigdict[bigdict.keys()[jj]]['tracks']

	album_sanitized = funcs.sanitize_album_name(album)

	####################################################
	## This bit is solely for retrieving data
	####################################################
	# instring = ' '.join((artist,album)).lower()
	# instring = instring.replace('(','')
	# instring = instring.replace(')','')
	# instring = instring.replace(' ','+')
	# instring = instring.replace('.','')

	# search_string = "http://www.songlyrics.com/index.php?section=search&searchW="
	# search_string += instring

	# htmlSource = retrieve_html(search_string)


	# outfile = open('albumsearches1/%s.txt' % album_sanitized,'w')
	# outfile.write('%s' % htmlSource)
	# outfile.close()

	htmlSource = open('albumsearches/%s.txt' % album_sanitized).readlines()

	if album == 'Curtain Call: The Hits':
		album_alt = "Curtain Call"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == '...And Then There Was X':
		album_alt = "And Then There Was X"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == 'Graduation (album)':
		album_alt = "Graduation"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == "I Am...":
		album_alt = "I Am"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == "Licensed to Ill":
		album_alt = "Licensed to III"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == "Flesh of My Flesh, Blood of My Blood":
		album_alt = "Flesh of My Flesh-Blood of My Blood"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == "The Art of War":
		album_alt = "Art of War"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == "The Blueprint2: The Gift & the Curse":
		album_alt = "The Blueprint 2: The Gift & The Curse"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == "Chicken-n-Beer":
		album_alt = "Chicken N Beer"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == "Mr. Smith":
		album_alt = "Mr Smith"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	elif album == "2001":
		album_alt = "Chronic"
		albumurl = funcs.find_the_album(htmlSource, album_alt) # with songlyrics.com

	else:
		albumurl = funcs.find_the_album(htmlSource, album) # with songlyrics.com

	if albumurl == []:
		notfound.append(jj)
	else: 
		bigdict[album]['url'] = albumurl		

#############################################
## Sincerely not found:
## jj	:	Album Name
## 0	:	To The Extreme
## 9	:	Me Against the World
## 28	:	Please Hammer, Don't Hurt 'Em
## 34	:	Kings of Crunk
## 41	:	Friday OST
## 63	:	Murda Muzik
#############################################


# #####################################################
# ## Let's get the track urls from songlyrics.com...
# ## Note: They don't have all tracks for each album!
# ## Going to have to do some string matching here...
# #####################################################

# for ii in range(len(bigdict.keys())):
# 	album = bigdict.keys()[ii]
# 	artist = bigdict[bigdict.keys()[ii]]['artist']
# 	wikitracks = bigdict[bigdict.keys()[ii]]['tracks']
# 	if 'url' in bigdict[album].keys():
# 		albumurl = bigdict[album]['url']
# 		htmlSource = funcs.retrieve_html(albumurl)
# 		htmlLines = htmlSource.split('\n')

# 		# albumfile = bigdict[bigdict.keys()[jj]]['albumfile']
# 		# htmlSource = funcs.retrieve_htmlcode_from_file(albumfile)
# 		# htmlLines = htmlSource.split('\n')

# 		tableLines = []
# 		for jj in range(len(htmlLines)):
# 			if htmlLines[jj].find('<table class="tracklist">') != -1:
# 				tableLines.append(jj)

# 		jj = tableLines[0]
# 		songlines = []
# 		while htmlLines[jj].endswith('</table>') == False:
# 			if htmlLines[jj].split('\t')[-1].endswith('</a></td>'):
# 				songlines.append(htmlLines[jj].split('\t')[-1])
# 			jj += 1

# 		#################################################################
# 		## Splitting the song lines and collecting song names and URLs
# 		## 
# 		## Let's compare the songnames list with
# 		## the list from wikipedia.  We might have to do some
# 		## string manipulations though...
# 		#################################################################
# 		songnames = []
# 		songurls = []
# 		for kk in range(len(songlines)):
# 			dum1 = songlines[kk].split('<')[2]
# 			dum2 = dum1.split('>')
# 			dum3 = dum2[1].split(' (')[0]
# 			songnames.append(funcs.sanitize_track(dum3))

# 			dum3 = dum2[0].split('"')[1]
# 			songurls.append(dum3)

# 		songurls = np.array(songurls)

# 		wikilist = []
# 		for kk in range(len(wikitracks)):
# 			dum1 = wikitracks.Titles[kk].split(' (')[0]
# 			dum2 = funcs.sanitize_track(dum1)
# 			wikilist.append(dum2)

# 		matchinds_songlyrics, matchinds_wiki = funcs.match_tracknames(songnames, wikilist)

# 		addurls = np.zeros(len(wikitracks), dtype='S150')
# 		for i in range(len(matchinds_wiki)):
# 		    addurls[matchinds_wiki[i]] = songurls[matchinds_songlyrics[i]]

# 		wikitracks['urls'] = addurls

# 		lyrics = []
# 		if matchinds_wiki != []:
# 			for mm in range(len(wikitracks['urls'])):
# 				url = wikitracks['urls'][mm]
# 				trackname = wikitracks['Titles'][mm]

# 				lyrics.append(funcs.get_lyrics(url, album, trackname))

# 		if lyrics != []:
# 			lyrics = np.array(lyrics, dtype='S200')
# 			wikitracks['lyrics'] = lyrics

# 			bigdict[bigdict.keys()[ii]]['tracks'] = wikitracks


#################################################################
## At this point, every song that has lyrics that are easily 
## found will have a downloaded page from songlyrics.com.  
## Let's start the next phase so that we can get some useful 
## data out.
#################################################################

all_lyrics = ['tracksearches/'+f for f in os.listdir('./tracksearches')]

the_albums = pickle.load(open('all_the_data.p'))

# #################################################################
# ## This is code doing a word analysis of Nas's I Am.
# ## Info is then plotted as a histogram
# #################################################################
# ii = 24 # I Am - Nas
# ii = 60 # Crunk Juice - Lil Jon
# album_name = the_albums.keys()[ii]
# album = the_albums[the_albums.keys()[ii]]
# year = int(the_albums[the_albums.keys()[ii]]['year'])
# artist = album['artist']

# words = funcs.word_counts_in_album(album)
# word_number_association = np.arange(0,len(words))
# word_counts = words.values()
# fig = plt.figure(figsize=(10,6))
# fig.subplots_adjust(top=0.85)
# plt.suptitle('Word Counts for\n%s - %s (%i)\n%s' % (album_name,artist,year,funcs.album_length(album)))
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

for ii in range(len(the_albums.keys())):
	album = the_albums[the_albums.keys()[ii]]
	year = int(the_albums[the_albums.keys()[ii]]['year'])
	artist = album['artist']

	if 'lyrics' in album['tracks']:
		word_count = funcs.word_counts_in_album(album, 'nigga')
		time = funcs.album_length(album, strout=False)
		over_time.append((word_count, time, year))

over_time = np.array(over_time)

counts_df = DataFrame(over_time, columns=['Count', 'Time', 'Year'])
over_time_cumulative = []
over_time_normed = []
years = []
for year in set(counts_df.Year):
	years.append(year)
	num_in_year = sum(counts_df.Year == year)
	over_time_cumulative.append(counts_df[counts_df.Year == year].Count.sum())
	over_time_normed.append(counts_df[counts_df.Year == year].Count.sum()/float(num_in_year))







