# Profanity in Top Hip Hop Albums

### Author: Nicholas Hunt-Walker
### Published: [blog post](http://rationalwhimsy.com/a-brief-study-in-hip-hop-profanity/)

This repository contains code and files pertaining to my analysis of Hip Hop lyrics between 1985 and 2013.

## The Breakdown

- **getalbumsongs.py**: main script for downloading and saving data to be used in analysis

- **funcs.py**: utility functions used in getalbumsongs.py. Includes everything from obtaining and cleaning data from Wikipedia to obtaining and cleaning data from songlyrics, as well as accumulating and saving word totals. Most of the heavy lifting is performed by this file.

- **parsewiki.py**: an older version of getalbumsongs.py. Does more or less the same things. Is no longer useful though.

- **get_all_top_albums.py**: older utility functions for when I was grabbing track listings from Wikipedia instead of songlyrics.com. Also no longer useful.

- **list_of_rappers.txt, lyrics_links.txt, wikitext.txt**: text files produced during the process for easy access to necessary web pages and data from those pages.

- **new_tracksearches/**: lyric text files for each track

- **new_albumsearch/**: text files for each album searched

- **all_top_albums/**: Old; top hip hop albums from each year between 1985 and 2013 from Wikipedia

- **tracksearches/**: Old; lyric text files for each track before I revamped my search

- **albums/**: Old; text files containing album pages from Wikipedia. The idea was to get track listings but it was too inconsistent for use.

- **albumsearches1/**: Old album searches from songlyrics.com

- **albumsearches2/**: More old album searches from songlyrics.com

