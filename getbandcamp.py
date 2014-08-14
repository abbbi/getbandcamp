#!/usr/bin/env python
import argparse
import json
import requests
from bs4 import BeautifulSoup
from urllib import quote_plus,unquote
from sys import exit
from os import mkdir, path, makedirs
from ID3 import *


# dont ask, google will help you
BC_API_KEY=""

# see: http://bandcamp.com/developer
BC_API_BANDID="http://api.bandcamp.com/api/band/3/search?key=" + BC_API_KEY + "&name="
BC_API_RECORDS="http://api.bandcamp.com/api/band/3/discography?key=" + BC_API_KEY + "&band_id="
BC_API_ALBUM="http://api.bandcamp.com/api/album/2/info?key=" + BC_API_KEY + "&album_id="
BC_API_TRACKS="http://api.bandcamp.com/api/track/3/info?key=" + BC_API_KEY + "&track_id="

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
        return proplist['content']
    else:
        return False

def get_record_tracks(band_id):
    data = get_json(BC_API_RECORDS, str(band_id))
    record = { 'singles' : {} }
    records = []
    if data['discography']:
        for disc in data['discography']:
            if disc.has_key('album_id'):
                records.append(disc['album_id'])
            elif disc['track_id']:
                trackinfo = get_json(BC_API_TRACKS, str(disc['track_id']))
                record['singles'][trackinfo['title']] = {}
                record['singles'][trackinfo['title']] = { 'url' : trackinfo['streaming_url'] }

    #record = {}
    for disc_id in records:
        disc = get_json(BC_API_ALBUM, str(disc_id))
        record[disc['title']] = {}
        for track in disc['tracks']:
            record[disc['title']][track['title']] = { 'number': track['number'] }
            if 'streaming_url' in track:
                record[disc['title']][track['title']]['url'] = track['streaming_url']
            else:
                record[disc['title']][track['title']]['url'] = False

    return record

def trackinfo(record_tracks):
    print "Found following singles:\n"

    if len(record_tracks['singles']) > 0:
        for single in record_tracks['singles']:
            print single
    else:
        print "No singles found"

    print "\nFound following records:\n"

    if len(record_tracks) > 0:
        for record in record_tracks:
            if record != "singles":
                print record
                for track in record_tracks[record]:
                    if record_tracks[record][track]['url'] == False:
                        print " + " + track + " (not available for download)"
                    else:
                        print " + " + track

    print "\n"

def download_tracks(tracklist, delimeter, directory, album, band_name):
    fixed_album_name = album.replace(" ", delimeter)
    fixed_band_name = band_name.replace(" ", delimeter)
    count=0
    for track in tracklist:
        if tracklist[track]['url'] == False:
            print "Track: " + track + " is not downloadable through stream, skipping"
            continue

        if tracklist[track].has_key('number'):
            track_id = str(tracklist[track]['number']).zfill(2)
        else:
            count=count+1
            track_id=str(count).zfill(2)

        fixed_name = track.replace(" ", delimeter)

        target_dir = directory + "/" + fixed_band_name + "/" + fixed_album_name
        target_file = target_dir + "/" +track_id + delimeter + fixed_name + ".mp3"

        print "Downloading: " + track + " URL: " + tracklist[track]['url'] + " To: " + target_file

        if not path.exists(target_dir):
            try:
                makedirs(target_dir)
            except OSError, e:
                print "Error creating directory:" + e.strerror
                exit(1)

        if path.exists(target_file):
            print "Skipping, file already exists"
            continue


        user_agent = {'User-agent': 'Mozilla/5.0'}
        try:
            r = requests.get(url=tracklist[track]['url'], headers = user_agent)
        except requests.ConnectionError, e:
            print "Error fetching page:" + str(e)
            exit(1)
        except requests.HTTPError, e:
            print "Error reading HTTP response:" + str(e)

        if r.status_code == requests.codes.ok:
            try:
                with open(target_file, "wb") as fh:
                    try:
                        for block in r.iter_content(1024):
                            try:
                                fh.write(block)
                            except IOError,e:
                                print "Unable to write output data" + str(e.strerror)
                                exit(1)
                    except KeyboardInterrupt:
                        print "aborted"
                        exit(0)

                fh.close

                id = ID3(target_file)
                id['ARTIST'] = band_name
                id['TITLE'] = track
                id["ALBUM"] = album
                id.write
            except IOError, e:
                print "Unable to open output file" + str(e.strerror)
        else:
            print "Error downloading track, http code: " + resp.status_code

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to bandpage on bandcamp", type=str, required=1)
    parser.add_argument("--output", help="destination directory to write files in (default: download)", default="download")
    parser.add_argument("--download", help="download stuff, default is only to show records and singles", action="store_true")
    parser.add_argument("--singles", help="download only singles", action="store_true")
    parser.add_argument("--album", help="download only specified album, default: all", default="all", type=str)
    parser.add_argument("--delimeter", help="replace space in filename with specified string, default: '_'", default="_", type=str)
    args = parser.parse_args()


    if not BC_API_KEY:
        print "Error: please set API key"
        exit(1)

    if not path.exists(args.output):
        print "Creating output directory"
        try:
            mkdir(args.output)
        except OSError, e:
            print "Error creating directory:" + e.strerror

    band_name = get_bandname(args.url)
    if band_name != False:
        print "Band name: " + band_name
    else:
        print "Unable to fetch band name from page"
        exit(1)

    band_data = get_json(BC_API_BANDID, quote_plus(band_name))
    if 'error' in band_data:
        print "Error fetching band data: " + band_data['error_message']
        exit(1)

    if len(band_data['results']) > 0:
        print "found multiple bands with the same name:"
        cnt = 0;
        for result in band_data['results']:
            print result['url'] + " id: " + str(cnt)
            cnt = cnt+1
        try:
            id = int(raw_input('please enter which band ID to use:'))
            print "ID: " + str(id)
        except ValueError:
            print "Given ID is not an integer"
            exit(1)

        try:
            band_id = band_data['results'][id]['band_id']
        except IndexError:
            print "error: cannot find band with given ID"
            exit(1)
    else:
        print "Unable to get band id, site changed?"
        exit(1)

    print "Band API ID " + str(band_id)
    record_tracks = get_record_tracks(str(band_id))
    if len(record_tracks) > 0:
        trackinfo(record_tracks)
    else:
        print "Bandcamp API did not respond with any records or band has no open records"
        exit(1)

    if args.download == False and args.singles == False:
        exit(1)

    if args.singles == True:
        if len(record_tracks['singles']) > 0:
            download_tracks(record_tracks['singles'], args.delimeter, args.output,"singles", band_name)
            exit(0)
        else:
            print "no singles found for downloading"
            exit(1)

    if args.album != "all":
        if record_tracks.has_key(args.album):
            print "\nDownloading album:\n" + args.album
            download_tracks(record_tracks[args.album], args.delimeter, args.output,args.album, band_name)
        else:
            print "Specified album not found in recordlist"
    else:
        for record in record_tracks:
            download_tracks(record_tracks[record], args.delimeter, args.output,record, band_name)
