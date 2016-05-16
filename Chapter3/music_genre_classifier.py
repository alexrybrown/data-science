# TODO: Add pickling of final object for later use and add Jaccard similarity index to measure closeness of genres
# TODO: Add sleep procedure to __update function so as to not overload the web server for wikipedia
# TODO: Continue to improve parsing of data and genres
import json
import re
from urllib.parse import urlencode, urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup

ROCK_EXTENSION = "/wiki/Category:Rock music groups by genre"
POP_EXTENSION = "/wiki/Category:Pop music groups by genre"
EXTENSIONS = [ROCK_EXTENSION, POP_EXTENSION]


class MusicGenreClassifier:
    """
    This class traverses the different pop/rock groups on wikipedia and finds the most similar genre paris of those
    groups. Similarity is based on the Jaccard similarity index.
    """
    _results = {}
    _counter = 0

    def __init__(self, update_results=False, verbose=False):
        """
        The first time an instance of MusicGenreClassifier is made it will update the results dict. If you are creating
        multiple instances or don't want more up to date results you can set the specified parameter.
        :param update_results: False by default. Used to decide if the results dict should be updated if this is not
        the first instance of the class.
        :param verbose: False by default. Writes debugging info to a log file when true.
        :return: None
        """
        self.verbose = verbose
        if not self._counter or update_results:
            self.__update()
        self._counter += 1

    def __del__(self):
        """
        Reduces the counter for instances on delete
        :return: None
        """
        self._counter -= 1

    def __update(self):
        """
        Updates the results by traversing the genres in wikipedia.
        Future revisions would check whether a revision was made to the page before replacing the already found genres
        for a particular group.
        :return: None
        """
        for extension in EXTENSIONS:
            self.__traverse_wiki(extension, self.get_wiki_url)

    def __traverse_wiki(self, data, url_method):
        """
        Recursively traverses url subcategories until genres are found and then updates _results dict.
        :param data: title or extension used to create url
        :param url_method: Either MediaWiki url or general url function
        :return:
        """
        url = url_method(data)
        with urlopen(url) as page:
            # If the method used was the MediaWiki specific one. Use a json object to read in the data
            if url_method == self.get_wiki_url:
                soup = BeautifulSoup(page, 'html5lib')
                sub_categories = soup.find('div', {'id': 'mw-subcategories'})
                pages = soup.find('div', {'id': 'mw-pages'})
                link_pattern = re.compile(r'^/wiki/\b')
                # Get sub_categories and keep traversing
                if sub_categories:
                    sc_links = [(link.string, link['href']) for link in sub_categories.find_all('a') if
                                link.has_attr('href') and link_pattern.match(link['href'])]
                    for name, extension in sc_links:
                        if self._results.get(name):
                            self._results[name].append(self.__traverse_wiki(extension, self.get_wiki_url))
                        else:
                            self._results.update(**{name: [self.__traverse_wiki(extension, self.get_wiki_url)]})
                # Get group pages and prepare for final traversal
                if pages:
                    p_links = [(link.string, link['title']) for link in pages.find_all('a') if
                               link.has_attr('href') and link_pattern.match(link['href']) and
                               link.string != 'learn more']
                    for name, title in p_links:
                        if self._results.get(name):
                            self._results[name].append(self.__traverse_wiki(title, self.get_media_wiki_url))
                        else:
                            self._results.update(**{name: [self.__traverse_wiki(title, self.get_media_wiki_url)]})
            else:
                data = json.loads(page.read().decode().lower())
                pages = data['query']['pages']
                page = pages.popitem()[1]
                if page.get('revisions'):
                    text = page['revisions'][0]['*']
                    return self.__get_genres(text)
                else:
                    return []

    def __get_genres(self, text):
        """
        Parses text and returns genres in the given text
        :param text: HTML page text
        :return: genres[...]
        """
        genres = []
        try:
            # Genre will be inside of something like this:
            # | Genre               =[[Rock and roll]], [[power pop]], [[garage rock]], [[indie rock]]
            genre_pattern = re.compile(r'genre\s*=\s*([a-zA-Z\[\]\-, ]*)')
            # Get what comes after the equals for Genre
            uncleaned_genres = genre_pattern.findall(text)[0]
            # Split on comma and remove square braces
            genres = [genre.strip()[2:-2].replace("-", " ") for genre in uncleaned_genres.split(',')]
        except IndexError:
            # Try pattern like this:
            # | qualifier = on a united states indie rock band
            genre_pattern = re.compile(r'(united states indie rock)')
            if genre_pattern.findall(text):
                genres = ['indie rock']
            else:
                try:
                    """
                    Try patterns like this:
                    </ref> is an [[indie rock]] band formed in 2004 by [[robert schneider]] of
                    </ref> was an [[indie rock]] band formed
                    '''bob's yer uncle''' is a [[rock music|rock]] band founded
                    '''the beets''' are an [[indie rock]]/[[punk rock]] group from
                    """
                    genre_pattern = re.compile(r'(?:(?:is)|(?:was))\s*(?:(?:an)|(?:a))\s*\[*\[*([a-zA-Z| ]*)\]*\]*')
                    uncleaned_genres = genre_pattern.findall(text)[0]
                    if 'from' in uncleaned_genres:
                        genre_pattern = re.compile(r'([a-zA-Z ]*)\s+from\s*')
                        uncleaned_genres = genre_pattern.findall(uncleaned_genres)[0]
                    genres = [genre.strip() for genre in uncleaned_genres.split('|') if genre]
                except IndexError:
                    pass
        if self.verbose:
            with open('log.txt', mode='a') as log:
                start = '----------------------------start----------------------------\n\n'
                end = '-----------------------------end-----------------------------\n\n'
                lines = [start, 'TEXT:\n\n{}\n\n'.format(text), 'GENRES:\n\n{}\n\n'.format(genres), end]
                log.writelines(lines)
        return genres and genres or []

    @staticmethod
    def get_media_wiki_url(title):
        """
        Builds the url required by MediaWiki to use their API and get a json version of wiki page.
        :param title: Title of the wiki page you are trying to get the url for.
        :return: MediaWiki API url for given title
        """
        query = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'rvprop': 'content',
            'titles': title,
        }
        base_url = 'https://en.wikipedia.org/w/api.php'
        return urljoin(base_url, '?{}'.format(urlencode(query)))

    @staticmethod
    def get_wiki_url(extension):
        """
        Builds the url required by MediaWiki to use their API and get a json version of wiki page.
        :param extension: Extension of the wiki page you are trying to get the url for.
        :return: Wikipedia url for given extension
        """
        base_url = 'https://en.wikipedia.org'
        return urljoin(base_url, extension)


if __name__ == '__main__':
    mgs = MusicGenreClassifier(verbose=True)
    print("Done!")
