#!/usr/bin/python
import json
import requests
from bs4 import BeautifulSoup
from urllib import quote_plus

# <meta property="og:site_name"  = band name
# = band_id : http://api.bandcamp.com/api/band/3/search?key=vatnajokull&name=U.S.%20Royalty
# = discography : http://api.bandcamp.com/api/band/3/discography?key=vatnajokull&band_id=203035041
# = record + download URL: http://api.bandcamp.com/api/album/2/info?key=vatnajokull&album_id=4101846944
# track= http://api.bandcamp.com/api/track/3/info?key=vatnajokull&track_id=1269403107&

resp = requests.get(url="http://usroyalty.bandcamp.com")
data = resp.content

soup = BeautifulSoup(data)

proplist = soup.find('meta', {"property":'og:site_name', 'content':True})
if proplist:
    band = quote_plus(proplist['content'])

print "Band: " + band
resp = requests.get(url="http://api.bandcamp.com/api/band/3/search?key=vatnajokull&name="+ band)
js = json.loads(resp.content)

if js['results']:
    for result in js['results']:
        band_id=result['band_id']

print "BandID:" + str(band_id)

resp = requests.get(url="http://api.bandcamp.com/api/band/3/discography?key=vatnajokull&band_id=" + str(band_id))
js = json.loads(resp.content)

records=[]
if js['discography']:
    for disc in js['discography']:
        try:
            records.append(disc['album_id'])
            print "Found record:" + str(disc['album_id']) + "title:" + str(disc['title'])
        except KeyError:
            print "single:"
            print disc['title']
            if disc['track_id']:
                resp = requests.get(url="http://api.bandcamp.com/api/track/3/info?key=vatnajokull&track_id=" + str(disc['track_id']))
                js = json.loads(resp.content)
                print js['streaming_url']
            

if len(records) > 0:
    print "download tracks:"
    for disc_id in records:
        resp = requests.get(url="http://api.bandcamp.com/api/album/2/info?key=vatnajokull&album_id=" + str(disc_id))
        js = json.loads(resp.content)
        if js['tracks']:
            for track in js['tracks']:
                print track['title']
                print track['streaming_url']
else:
    print "found no records to get"
