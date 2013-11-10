#!/usr/bin/python
import argparse
import json
import requests
from bs4 import BeautifulSoup
from urllib import quote_plus
from sys import exit
from os import mkdir, path

# python getbandcamp.py --url http://usroyalty.bandcamp.com --output destdir

parser = argparse.ArgumentParser()
parser.add_argument("--url", help="URL to bandpage on bandcamp", type=str, required=1)
parser.add_argument("--output", help="destination directory to write files in (default: download)", default="download")
args = parser.parse_args()

if not path.exists(args.output):
    print "Creating output directory"
    try:
        mkdir(args.output)
    except OSError, e:
        print "Error creating directory:" + e.strerror

# <meta property="og:site_name"  = band name
# = band_id : http://api.bandcamp.com/api/band/3/search?key=vatnajokull&name=U.S.%20Royalty
# = discography : http://api.bandcamp.com/api/band/3/discography?key=vatnajokull&band_id=203035041
# = record + download URL: http://api.bandcamp.com/api/album/2/info?key=vatnajokull&album_id=4101846944
# track= http://api.bandcamp.com/api/track/3/info?key=vatnajokull&track_id=1269403107&

# fetch stuff, turn into funcation/class later
try:
    resp = requests.get(url=args.url)

    if resp.status_code == requests.codes.ok:
        data = resp.content
    else:
        print "Error fetching page, error:" + str(resp.status_code)
        exit(1)

except requests.ConnectionError, e:
    print "Error fetching page:" + str(e)
    exit(1)
except requests.HTTPError, e:
    print "Error reading HTTP response:" + str(e)

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
