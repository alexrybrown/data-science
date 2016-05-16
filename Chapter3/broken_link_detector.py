"""
This program takes a url as an argument and determines if there are any broken links on the given page.
A link is considered broken if urllib.request.urlopen returns an error.

Usage: python broken_link_detector.py [url]
"""
import sys
from urllib.request import urlopen

from bs4 import BeautifulSoup


def main(url):
    with urlopen(url) as page:
        soup = BeautifulSoup(page, 'html.parser')
    links = [(link.string, link['href']) for link in soup.find_all('a') if link.has_attr('href')]
    broken_links = []
    for link in links:
        try:
            page = urlopen(link[1])
            page.close()
        except:
            broken_links.append(link)
    print('\n'.join(["{}, {}".format(name, link) for name, link in broken_links]))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Usage: python broken_link_detector.py [url]", file=sys.stderr)
