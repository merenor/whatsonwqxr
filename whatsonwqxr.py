#!/usr/bin/env python

"""
whatsonwqxr.py
Webscraping a Classical Radio Station
2017/10/13
Felix Werthschulte
"""

import time

from bs4 import BeautifulSoup
import parse
import requests


class Record:
    """A Struct for all needed data. Better to read than a dict"""

    def __init__(self, uhrzeit_h, uhrzeit_m, composer, title, musicians, duration_min, duration_sec):
        self.uhrzeit_h = uhrzeit_h
        self.uhrzeit_m = uhrzeit_m
        self.composer = composer
        self.title = title
        self.musicians = musicians
        self.duration_min = duration_min
        self.duration_sec = duration_sec


    def __repr__(self):
        return 'Seit {}:{} Uhr läuft:\n{} - {}\n{}\nDauer: {}:{} Min.\n'.format(
            self.uhrzeit_h,
            self.uhrzeit_m,
            self.composer,
            self.title,
            str(self.musicians),
            self.duration_min,
            self.duration_sec
        )


def create_url(datum):
    """Creates a URL containing today's date"""

    return 'http://www.wqxr.org/playlist-daily/{y}/{m}/{d}/?scheduleStation=wqxr'.format(
        y = time.strftime('%Y', datum),
        m = time.strftime('%b', datum).lower(),
        d = time.strftime('%d', datum)
    )


def scrape_me(url):
    """Does all of the scraping, of course"""

    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # Get the starting time of the current piece's broadcast.
    # Very complex, as it is a) the timezone of New York and
    # and b) the tag is outside of <div class='piece-info'>
    zeit = parse.parse('{:d}:{:d} {:w}', soup.find('div', attrs={'class': 'time'}).get_text().strip())
    if zeit.fixed[2] == 'AM':
        uhrzeit_h = int(zeit.fixed[0]) + 6
    else:
        uhrzeit_h = int(zeit.fixed[0]) + 18
    uhrzeit_m = int(zeit.fixed[1])

    # get the rest of the info
    piece = soup.find('div', attrs={'class': 'piece-info'})

    composer = piece.find('a', attrs={'class': 'playlist-item__composer'}).get_text().strip()
    title = piece.find('li', attrs={'class': 'playlist-item__title'}).get_text().strip()
    mus = piece.find_all('li', attrs={'class': 'playlist-item__musicians'})
    musicians = [m.get_text().strip() for m in mus]

    # Parsing the duration of the song:
    # - getting the text of the last <li>-tag (has no class)
    # - parse it by the given pattern, i.e. '29 min 16 s'
    duration = parse.parse('{:d} min {:d} s', piece.find_all('li')[-1].get_text().strip())
    duration_min = duration.fixed[0]
    duration_sec = duration.fixed[1]

    return Record(
        uhrzeit_h,
        uhrzeit_m,
        composer,
        title,
        # get the list as string and fix some odd spacing, by the way
        str(musicians)[2:-2].replace('\'', '').replace('        ', ''),
        duration_min,
        duration_sec
    )


def main():
    now = time.localtime()
    url = create_url(now)
    print(scrape_me(url))


if __name__ == '__main__':
    main()
