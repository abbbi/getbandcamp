getbandcamp
===========

Download mp3 streams vom bandcamp.com to a specified directory and mp3 TAG
accordingly

You need at least a bandcamp API KEY to be set in the source, the key from
the documentation does not help anymore, however, google may probably
help you to find a key ;))


USAGE
------------
<pre>
usage: getbandcamp.py [-h] --url URL [--output OUTPUT] [--download]
                      [--singles] [--album ALBUM] [--delimeter DELIMETER]

optional arguments:
  -h, --help            show this help message and exit
  --url URL             URL to bandpage on bandcamp
  --output OUTPUT       destination directory to write files in (default:
                        download)
  --download            download stuff, default is only to show records and
                        singles
  --singles             download only singles
  --album ALBUM         download only specified album, default: all
  --delimeter DELIMETER
                        replace space in filename with specified string,
                        default: '_'
</pre>


EXAMPLES
------------
List available singles and records for band URL:

 python getbandcamp.py --url http://myband.bandcamp.com/

Download only a specified record from band URL:

 python getbandcamp.py --url http://myband.bandcamp.com/ --output destdir --album "Record Name" --download

Download all records and singles from a band URL:
 
 python getbandcamp.py --url http://myband.bandcamp.com/ --output destdir --download

Download only singles from a band URL:

 python getbandcamp.py --url http://myband.bandcamp.com/ --output destdir --singles


DEPENDENCIES
------------
additional packages may have to be installed (debian):

<pre>
 pyhont-id3
 python-bs4
 python-requests
</pre>
