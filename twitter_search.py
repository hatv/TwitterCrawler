# -*- coding: utf-8 -*-

# File: twitter_search.py
# Author: Victor Hatinguais
# Import as many tweets as possible with Twython
# Search by keywords
# Authors are kept in a separate file to be used with twitter_author.py

from twython import Twython
from twython.exceptions import TwythonRateLimitError, TwythonError
from time import gmtime, strftime, sleep
import urllib
import signal
import json

current_time = strftime("%Y%m%d_%H%M%S", gmtime())
output_file_name = 'search.output.' + current_time
output_file = open(output_file_name, mode='a', encoding='utf-8')
authors_id_set = set()
nb = 0


def terminate(signal, frame):
    print("Ctrl + C handler: close file!")
    output_file.close()
    print("File closed with about " + str(nb) + " lines")
    authors_id_file_name = 'authors_id.output.' + current_time
    authors_id_file = open(authors_id_file_name, mode='a', encoding='utf-8')
    for author_id in authors_id_set:
        authors_id_file.write(str(author_id) + '\n')
    authors_id_file.close()
    exit(0)

signal.signal(signal.SIGINT, terminate)

# Fill with your Twitter app details: https://apps.twitter.com/
APP_KEY = 'h8QAsVCofDKkecVhASsBc9fQ6'
APP_SECRET = 'WtrpDcCGrhFQsNRro1CCLhzMicZRjMERyPDKinRZ8Rs9GjHc2Z'
# OAUTH_TOKEN = '968583049-J4GO2Y5RIV2YLva7Kvyq0h0R0zdqBHaRpXLUXwMO'
# OAUTH_TOKEN_SECRET = 'XQXiRw5rIEAeLbIIkb96sRFhonJC5wgBaC33XGJA0XsEP'

twitter = Twython(APP_KEY, APP_SECRET)

# The Twitter API has a query string size limit
query = urllib.request.quote(
    'dengue OR dengo OR chikungunya OR mosquitos OR mosquito OR (severe headaches) OR (sudden high fever)'
    ' OR (pain bahind eyes) OR (severe joint muscle pain) OR (nausea feber) OR (feber skin rash) OR (mild bleeading)'
    ' OR (feber cabeça) OR (feber cabeca) OR (feber olhos) OR (feber musculares) OR (feber articulações)'
).encode('utf8')

last_id = -1
while True:
    try:
        if last_id == -1:
            json_results = twitter.search(q=query, count=100)
        else:
            json_results = twitter.search(q=query, count=100, max_id=last_id-1)
    except TwythonRateLimitError:
        print("TwythonRateLimitError: sleep 30 seconds")
        sleep(30)
        continue
    except TwythonError as e:
        print("TwythonError:", e.msg)
        if e.msg[2:21] == 'Connection aborted.':
            print("Try to get your connection back. Or Ctrl + C to stop with", nb, "tweets. Sleep 30 seconds...")
            sleep(30)
            continue
        else:
            print("Unknown problem occurred.")
            terminate(None, None)
            break

    if len(json_results["statuses"]) == 0:
        print("No more tweets.")
        terminate(None, None)
        break
    else:
        for json_result in json_results["statuses"]:
            nb += 1
            # output_file.write(str(json_result))
            json.dump(json_result, output_file, ensure_ascii=False)
            output_file.write('\n')
            last_id = json_result["id"]
            last_date = json_result["created_at"]
            authors_id_set.add(json_result["user"]["id"])

        print(last_id, last_date, nb)
