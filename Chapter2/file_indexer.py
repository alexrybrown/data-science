"""
This program will index all the files in a user designated directory. It will construct a dictionary where
they keys are unique words and the values are the files that have those words. This program will pickle the result
for future use.

Usage: python file_indexer.py [directory]
"""
import os
import pickle
import re
import sys


def main(directory):
    # Grab everything from the directory and only keep it if it is a file
    files = [file for file in os.listdir(directory) if os.path.isfile(file)]
    pattern = re.compile(r'\w+')
    pairings = dict()
    for file in files:
        with open(file, mode='rb') as f:
            # If a decoding error occurs just skip the file and got to the next one.
            try:
                contents = f.read().decode().lower()
            except UnicodeDecodeError:
                print("Error decoding. Skipped {file}.".format(**locals()), file=sys.stderr)
                continue
            # We want all the unique words from the file
            words = list(set(pattern.findall(contents)))
            # For each word found either append the file to an existing key:value or create a key:value pair.
            for word in words:
                if pairings.get(word):
                    pairings[word].append(file)
                else:
                    pairings[word] = [file]
    # Pickle the pairings for later use
    with open('file_indexer.pickle', mode='wb') as oFile:
        pickle.dump(pairings, oFile)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Usage: python file_indexer.py [directory]", file=sys.stderr)
