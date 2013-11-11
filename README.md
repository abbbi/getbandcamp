getbandcamp
===========

Download mp3 streams vom bandcamp.com to a specified directory and mp3 TAG
accordingly

USAGE
------------
<pre>
usage: getbandcamp.py [-h] --url URL [--output OUTPUT] [--download {yes,no}]
                      [--album ALBUM] [--singles {yes,no}]
                      [--delimeter DELIMETER]

optional arguments:
  -h, --help            show this help message and exit
  --url URL             URL to bandpage on bandcamp
  --output OUTPUT       destination directory to write files in (default:
                        download)
  --download {yes,no}   download stuff, default is only to show records and
                        singles
  --album ALBUM         download only specified album, default: all
  --singles {yes,no}    download only singles
  --delimeter DELIMETER
                        replace space in filename with specified string,
                        default: '_'
</pre>


EXAMPLES
------------
List available singles and records for band URL:

 python getbandcamp.py --url http://myband.bandcamp.com/

Download only a specified record from band URL:

 python getbandcamp.py --url http://myband.bandcamp.com/ --output destdir --album "Record Name" --download yes

Download all records and singles from a band URL:
 
 python getbandcamp.py --url http://myband.bandcamp.com/ --output destdir --download yes

Download only singles from a band URL:

 python getbandcamp.py --url http://myband.bandcamp.com/ --output destdir --singles yes


DEPENDENCIES
------------
additional packages may have to be installed (debian):

<pre>
 pyhont-id3
 python-bs4
 python-requests
</pre>
