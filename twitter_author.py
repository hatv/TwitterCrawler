# -*- coding: utf-8 -*-

# File: twitter_author.py
# Author: Victor Hatinguais
# Import all tweets from a given list of authors
# Specify a file name containing one author id per row on the command line

from twython import Twython
from twython.exceptions import TwythonRateLimitError, TwythonError
from time import gmtime, strftime, sleep
from os import path
import signal
import sys
import json

if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "author_ids_file_name")
    exit(0)
else:
    if path.isfile(sys.argv[1]):
        input_file_name = sys.argv[1]
        print("Input file:", input_file_name)
    else:
        print("File", sys.argv[1], "not found")
        exit(0)

current_time = strftime("%Y%m%d_%H%M%S", gmtime())
output_file_name = 'authors.output.' + current_time
output_file_name_authors_explored = 'authors_id_explored.output.' + current_time
output_file = open(output_file_name, mode='a', encoding='utf-8')
output_file_authors_explored = open(output_file_name_authors_explored, mode='a', encoding='utf-8')

input_file = open(input_file_name, mode='r', encoding='utf-8')
nb = 0


def terminate(signal, frame):
    print("Ctrl + C handler: close file!")
    output_file.close()
    output_file_authors_explored.close()
    print("File closed with about " + str(nb) + " lines")
    exit(0)

signal.signal(signal.SIGINT, terminate)

# Fill with your Twitter app details: https://apps.twitter.com/
APP_KEY = ''
APP_SECRET = ''

twitter = Twython(APP_KEY, APP_SECRET)

nb_tweets = 0
authors = input_file.readlines()
nb_authors = len(authors)
author_id_nb = 0
for author_id in authors:
    author_id = author_id[:-1]
    last_id = -1
    author_id_nb_tweets = 0
    author_id_nb += 1
    while True:
        try:
            if last_id == -1:
                user_tweets = twitter.get_user_timeline(user_id=author_id, include_rts=True, count=200)
            else:
                user_tweets = twitter.get_user_timeline(
                    user_id=author_id, include_rts=True, count=200, max_id=last_id-1)
        except TwythonRateLimitError:
            print("TwythonRateLimitError: sleep 30 seconds...")
            sleep(30)
            continue
        except TwythonError as e:
            print("TwythonError:", e.msg)
            if e.msg[2:21] == 'Connection aborted.':
                print("Try to get your connection back. Or Ctrl + C to stop with", nb, "tweets from about",
                      author_id_nb, "authors. Sleep 30 seconds...")
                sleep(30)
                continue
            else:
                print("Maybe a problem with author", author_id)
                break
        if len(user_tweets) == 0:
            print("Author", author_id, "(", author_id_nb, "/", nb_authors, ") :", author_id_nb_tweets, "tweets. Total:",
                  nb, "tweets.")
            break
        else:
            for tweet in user_tweets:
                nb += 1
                author_id_nb_tweets += 1
                # output_file.write(str(tweet))
                json.dump(tweet, output_file, ensure_ascii=False)
                output_file.write('\n')
                last_id = tweet["id"]
                last_date = tweet["created_at"]
            # print(author_id, last_id, last_date, nb)
    output_file_authors_explored.write(author_id + '\n')

terminate(None, None)