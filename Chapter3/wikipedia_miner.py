"""
This program uses the data science page on wikipedia and return the ten most frequently used stems on that page.
Instead of using titles in the query dict I first get the page id and then use that instead to maintain a direct
copy to the given page.

Usages: python wikipedia_miner.py
"""
import json
import sys
from collections import Counter
from urllib.parse import urlencode, urljoin
from urllib.request import urlopen

import nltk


def main():
    # Query structure required by MediaWiki. Reference can be found here: https://www.mediawiki.org/wiki/API:Main_page
    query = {
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'rvprop': 'content',
        'pageids': '35458904',
    }
    # Endpoint required by MediaWiki.
    base_url = 'https://en.wikipedia.org/w/api.php'
    url = urljoin(base_url, '?{}'.format(urlencode(query)))
    # Using chosen stemmer
    ls = nltk.LancasterStemmer()
    with urlopen(url) as page:
        content = json.loads(page.read().decode().lower())
        text = content['query']['pages']['35458904']['revisions'][0]['*']
        # extracts and tokenizes the text
        words = nltk.word_tokenize(text)
        # Remove all stop words and make sure each word is alphanumeric and then retrieve then stems
        words = [
            ls.stem(word) for word in words if word not in nltk.corpus.stopwords.words("english") and word.isalnum()]
        freqs = Counter(words)
        print(freqs.most_common(10))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        print("Usages: python wikipedia_miner.py", file=sys.stderr)
