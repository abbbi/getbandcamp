#!/usr/bin/python
import argparse
import json
import requests
from bs4 import BeautifulSoup
from urllib import quote_plus
from sys import exit
from os import mkdir, path

# python getbandcamp.py --url http://usroyalty.bandcamp.com --output destdir

BC_API_BANDID="http://api.bandcamp.com/api/band/3/search?key=vatnajokull&name="
BC_API_RECORDS="http://api.bandcamp.com/api/band/3/discography?key=vatnajokull&band_id="
BC_API_ALBUM="http://api.bandcamp.com/api/album/2/info?key=vatnajokull&album_id="
BC_API_TRACKS="http://api.bandcamp.com/api/track/3/info?key=vatnajokull&track_id="

def get_url(url):
    try:
            resp = requests.get(url=url)
            if resp.status_code == requests.codes.ok:
                data = resp.content
                return data
            else:
                print "Error fetching page, error:" + str(resp.status_code)
                exit(1)
    except requests.ConnectionError, e:
        print "Error fetching page:" + str(e)
        exit(1)
    except requests.HTTPError, e:
        print "Error reading HTTP response:" + str(e)

def get_json(url, id):
    get = url + id
    data = get_url(get)
    return json.loads(data)

def get_bandname(url):
    data = get_url(url)
    soup = BeautifulSoup(data)
    proplist = soup.find('meta', {"property":'og:site_name', 'content':True})
    if proplist:
        return quote_plus(proplist['content'])

# me this sucks, make it the other way
# get_records -> return album_discs
# for each records -
#  -> get tracks
# get singles -> return only singles
def get_singles(band_id):
    data = get_json(BC_API_RECORDS, band_id)
    singles = []
    if data['discography']:
        for disc in data['discography']:
            if not disc.has_key('album_id'):
                if disc['track_id']:
                     trackinfo = get_json(BC_API_TRACKS, str(disc['track_id']))
                     singles.append(trackinfo['streaming_url'])

        return singles

def get_record_tracks(band_id):
    data = get_json(BC_API_RECORDS, str(band_id))
    records=[]
    if data['discography']:
        for disc in data['discography']:
            if disc.has_key('album_id'):
                records.append(disc['album_id'])

    tracks=[]
    for disc_id in records:
        disc = get_json(BC_API_ALBUM, str(disc_id))
        if disc['tracks']:
            for track in disc['tracks']:
                tracks.append(track['streaming_url'])

    return tracks

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to bandpage on bandcamp", type=str, required=1)
    parser.add_argument("--output", help="destination directory to write files in (default: download)", default="download")
    parser.add_argument("--delimeter", help="replace space in filename with specified string, default: '_'", default="_")
    args = parser.parse_args()

    if not path.exists(args.output):
        print "Creating output directory"
        try:
            mkdir(args.output)
        except OSError, e:
            print "Error creating directory:" + e.strerror

    band_name = get_bandname(args.url)
    print "Band name" + band_name

    band_data = get_json(BC_API_BANDID, band_name)
    if band_data['results']:
        for result in band_data['results']:
            band_id = result['band_id']

    print "Band ID" + str(band_id)
    singles = get_singles(str(band_id))
    print singles
    record_tracks = get_record_tracks(str(band_id))
    print record_tracks
