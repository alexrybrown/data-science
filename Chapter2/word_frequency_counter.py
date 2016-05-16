"""
This program will download a web page specified by a user and return the 10 most frequently used words.
All words will be treated case insensitive. A word is described by the regular expression r"\w+"

Usage: python word_frequency_counter.py [web page]
"""
from collections import Counter
import re
import sys
import urllib.request


def main(web_page):
    pattern = re.compile(r'\w+', re.IGNORECASE)
    try:
        with urllib.request.urlopen(web_page) as page:
            # Read, decode, and ignore case of the page
            html = page.read().decode().lower()
            # Get a list of all the words
            words = pattern.findall(html)
            # Grab only the most common ten words used
            word_counts = Counter(words).most_common(10)
            print(word_counts)
    except:
        print("Could not open {}".format(web_page), file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Usage: python word_frequency_counter.py [web page]", file=sys.stderr)
