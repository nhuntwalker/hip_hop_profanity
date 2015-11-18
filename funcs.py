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

def clean_off_html(line):
	clean1 = line.split('>')
	n = len(clean1)
	mydata = clean1[(n-1)/2].split('<')[0]
	return mydata

def find_tracklist(fname):
	pageinfo = open(fname).readlines()
	all_lines = []
	tableinds = []

	for i in range(len(pageinfo)):
		all_lines.append(pageinfo[i])

		if (pageinfo[i].lower().find('id="track_listing"') != -1):
			tableinds.append(i)
		elif (pageinfo[i].lower().find('id="tracks_listing"') != -1):
			tableinds.append(i)
		elif (pageinfo[i].lower().find('id="track_listings"') != -1):
			tableinds.append(i)

	if tableinds == []:
		print "The track list from %s is not available.\n" % fname
		return [],[]

	else:
		return all_lines, tableinds

def isolate_table(lines, inds_start):
	## Only want the page starting after "Track Listing"
	## So we want our first line to be lines[inds_start[0]]
	## And we only want to go until we see </table>
	lines = lines[inds_start[0]:]
	keeps = []
	ii = 0
	while lines[ii].startswith('</table>') == False:
		keeps.append(lines[ii])
		if lines[ii].startswith('<table'):
			tbhead = ii
		ii += 1

	return keeps, tbhead

def get_albumpage_from_wiki(url, album):
	os.system("curl --globoff http://en.wikipedia.org%s > ./albums/%s.txt" % (url,album))

def get_colheads(tablelines, tbhead):
	## Want to isolate the column heads to populate our 
	## dict's keys.  Some tables have the <th>
	## tag for the column headers, and some just have
	## the first row as the column headers without the
	## <th> tags.  Let's try to account for both.
	tbinfo = tablelines[tbhead+1:]
	keeps = []
	ii = 0
	while tbinfo[ii].startswith('</tr>') == False:
		keeps.append(tbinfo[ii])
		ii += 1

	if keeps != []:
		if ii < 5:
			keeps = []
			kk = ii + 1
			while tbinfo[kk].startswith('</tr>') == False:
				keeps.append(tbinfo[kk])
				kk +=1

			if keeps[1].split(">")[1] not in "No.</th #</th":
				keeps = []
				mm = kk + 1
				while tbinfo[kk].startswith('</tr>') == False:
					keeps.append(tbinfo[kk])
					kk +=1

	colheads = []

	if keeps != []:
		if keeps[1].startswith('<th'):
			for jj in range(len(keeps)):		
				dum1 = keeps[jj].split('>')
				dum2 = dum1[1].split('<')[0]
				colheads.append(dum2)

	if colheads != []:
		colheads = colheads [1:]
		if colheads[-1] == '':
			colheads = colheads[:-1]

		if colheads[0].lower() not in 'no. #':
			colheads = []

	for mm in range(len(colheads)):
		if colheads[mm] == "#":
			colheads[mm] = "No."
		if colheads[mm] == "Name":
			colheads[mm] = "Title"
		if colheads[mm] == "Time":
			colheads[mm] = "Length"


	return colheads

def cleanhtml(raw_html):
	## Workhorse for cleaning my html
	cleanr =re.compile('<.*?>')
	cleantext = re.sub(cleanr,'', raw_html)
	return cleantext

def get_track_titletime(tblines, tbhead, colheads):
	## I only care about track title and length
	tbinfo = tblines[tbhead+1:]
	tbinfo.append('</table>')
	tbinfo = np.array(tbinfo)
	rows = np.array([jj for jj in range(len(tbinfo)) if tbinfo[jj].startswith('<tr')])

	colheads = np.array(colheads)
	titleind = np.where(colheads == 'Title')[0]
	timeind = np.where(colheads == 'Length')[0]

	allsongs = []
	for ii in rows[1:]:
		dum = []
		if tbinfo[ii + 1].startswith('<th') != True:
			while tbinfo[ii].startswith('</tr>') != True:
				dum.append(tbinfo[ii])
				ii += 1
			allsongs.append('|'.join(dum))

	titles = []
	times = []

	for ii in range(len(allsongs)):
		song = [cleanhtml(info).split('\n')[0] for info in allsongs[ii].split('|') if info.startswith('<td')]
		if len(song) > np.maximum(titleind,timeind):
			titles.append(song[titleind])
			times.append(song[timeind])

	for i in range(len(titles)):
		if titles[i].find('&amp;') != -1:
			titles[i] = titles[i].replace('&amp;','&')
		if titles[i].find(' &#160;'):
			titles[i] = titles[i].replace(' &#160;','')
		if times[i].find('&#160;') != -1:
			times[i] = times[i].replace('&#160;','0:00')

	album = DataFrame({'Titles':titles, 'Times':times})
	return album

def find_the_album(htmlSource, album):
	parse = [line for line in htmlSource]
	wantlines = []
	for ii in range(len(parse)):
		if parse[ii].find('on album') != -1:
			wantlines.append(parse[ii])

	albumlines = []
	for ii in range(len(wantlines)):
		if wantlines[ii].lower().find('>'+album.lower()) != -1:
			albumlines.append(wantlines[ii])

	if albumlines != []:
		albumurl1 = albumlines[0].split('on album ')[1]
		albumurl2 = albumurl1.split('">')[0]
		albumurl3 = albumurl2.split('a href="')[1]

		return albumurl3
	else:
		# print 'Could not find album'
		return []

def sanitize_album_name(album):
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

	return album


def retrieve_html(instring):
	sock = urllib.urlopen(instring)
	htmlSource = sock.read()
	sock.close()

	return htmlSource

def retrieve_htmlcode_from_file(instring):
	htmlSource = open(instring).read()
	return htmlSource


def sanitize_track(track):
	track = track.lower()
	track = track.replace('?','')
	track = track.replace("'",'')
	track = track.replace('"','')
	track = track.replace("-",'')
	track = track.replace('.','')
	track = track.replace(',','')
	track = track.replace(':','')
	track = track.replace('&','')
	track = track.replace('the','')
	track = track.replace('/','')
	track = track.replace(' ','')

	return track

def match_tracknames(songlyrics_list, wikilist):
	sl_inds = []
	wl_inds = []

	for i in range(len(songlyrics_list)):
		for j in range(len(wikilist)):
			if songlyrics_list[i] == wikilist[j]:
				sl_inds.append(i)
				wl_inds.append(j)

	if sl_inds == []:
		return [],[]
	else:
		return np.array(sl_inds), np.array(wl_inds)

def get_lyrics(url, album, trackname):
	## Check to make sure the URL is formatted proper
	if url.startswith('http:'):
		trackname = sanitize_track(trackname)
		album = sanitize_track(album)
		fname = 'tracksearches/'+album+'_'+trackname+'.txt'

		# rtnm = album+'_'+trackname+'.txt'
		# if rtnm not in os.listdir('./tracksearches'):
		htmlSource = br.open(url).get_data()

		outfile = open('%s' % fname,'w')
		outfile.write('%s' % htmlSource)
		outfile.close()

		return fname

	else:
		return None

def get_new_lyrics(url, album, trackname):
	## Check to make sure the URL is formatted proper
	if url.startswith('http:'):
		trackname = sanitize_track(trackname)
		album = sanitize_track(album)
		fname = 'new_tracksearches/'+album+'_'+trackname+'.txt'

		# rtnm = album+'_'+trackname+'.txt'
		# if rtnm not in os.listdir('./tracksearches'):
		htmlSource = br.open(url).get_data()

		outfile = open('%s' % fname,'w')
		outfile.write('%s' % htmlSource)
		outfile.close()

		return fname

	else:
		return None

def distill_lyrics(lyricsfile):
	soup = BeautifulSoup(open(lyricsfile).read())
	## Find the actual lyrics
	## Look for <p id="songLyricsDiv class=songLyrics"
	findit = soup.find(attrs={'id':'songLyricsDiv'}) or 'None'

	if findit != 'None':
		lyrics = soup.find(attrs={'id':'songLyricsDiv'}).text
		lyrics.replace('<br/>',' ')
		return lyrics
	else:
		return 'None'

def word_clean(text):
	dum1 = text.lower()
	regex = [',','.',',','\n','\r','(',')',
		'?','!',';',':','/','\\']
	for ex in regex:
		dum1 = dum1.replace(ex,' ')

	# dum1 = dum1.replace("'",'')
	text = np.array(dum1.split())
	return text

def word_search(text, word):
	count = len(np.where(text == word)[0])
	return count

def word_dict(lyricsfile):
	data = distill_lyrics(lyricsfile)
	if data != 'None':
		cleaned = word_clean(data)
		uniques = list(set(cleaned))

		allwords = {}
		for i in range(len(uniques)):
			if (len(uniques[i]) > 1) & (word_search(cleaned, uniques[i]) > 1):
				allwords[uniques[i]] = word_search(cleaned, uniques[i])

		return allwords
	else:
		return {}


def word_counts_in_album(album,the_words=None,nigga_fold=True):
	lyrics_list = album['Lyrics Files']

	all_lyrics = []
	common = ['a','an','and','at','of','on',
	'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
	'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
	'll','re', 'in','is','it','for','the','to']

	for jj in range(len(lyrics_list)):
		if lyrics_list[jj] != 'None':
			all_lyrics.append(word_dict(lyrics_list[jj]))

	all_words = {}
	for jj in range(len(all_lyrics)):
		words_and_counts = all_lyrics[jj]
		for key in words_and_counts.keys():
			if key not in all_words.keys():
				all_words[key] = words_and_counts[key]
			else:
				all_words[key] += words_and_counts[key]

	for key in common:
		if key in all_words:
			trash_it = all_words.pop(key)


	if nigga_fold == True:
		if 'nigga' not in all_words.keys():
			all_words['nigga'] = 0

		if 'niggas' in all_words.keys():
			all_words['nigga'] += all_words['niggas']
		if 'niggaz' in all_words.keys():
			all_words['nigga'] += all_words['niggaz']
		if "nigga's" in all_words.keys():
			all_words['nigga'] += all_words["nigga's"]

		if 'bitch' not in all_words.keys():
			all_words['bitch'] = 0

		if 'bitches' in all_words.keys():
			all_words['bitch'] += all_words['bitches']


	words_and_counts = all_words.items()
	topwords = {}
	for item in words_and_counts:
		if item[1] > 50:
			topwords[item[0]] = item[1]

	if the_words != None:
		if hasattr(the_words, '__iter__'):
			allcounts = {}
			for word in the_words:
				if word in all_words.keys():
					allcounts[word] = all_words[word]

				else:
					allcounts[word] = 0
			return allcounts

		else:
			if the_words in all_words.keys():
				return all_words[the_words]
			else:
				return 0

	else:
		return topwords

def convert_time(tracktime):
	## Convert the Minutes:Seconds string to seconds
	x = time.strptime(tracktime, "%M:%S")
	timeout = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
	return timeout

def album_length(album, strout=True):
	times = album['tracks'].Times
	time_arr = []

	for time in times:
		time_arr.append(convert_time(time))

	if strout == True:
		return str(datetime.timedelta(seconds=sum(time_arr)))
	else:
		return sum(time_arr)


def get_album_covers(dframe):
	for ii in dframe.index:
		raw_html = br.open(dframe.albumURLs[ii]).get_data()
		soup = BeautifulSoup(raw_html)
		img_want = soup.find('img')
		data = br.open(img_want['src']).read()
		covers_dir = 'album_covers/'
		album = sanitize_track(dframe.Album[ii])
		file_out = covers_dir+album+"_cover.jpg"
		savefile = open(file_out, 'wb')
		savefile.write(data)
		savefile.close()

	print "Job's Done"
	# return album+"_cover.jpg"











