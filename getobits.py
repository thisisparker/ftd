#! python3
# Grabs the last 10 NYT obits and prepares the text of a FOIA request for their FBI files.

import os, requests, json, datetime, re
from datetime import datetime

nyt_api_key = os.environ["NYT_API_KEY"]

api_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?fq=type_of_material:%28%22Obituary%22%29&sort=newest&fl=headline,web_url,snippet,pub_date&api-key=" + nyt_api_key

res = requests.get(api_url)
res.raise_for_status()

api_results = json.loads(res.text)

docs = api_results['response']['docs']

for i in docs:
    obit_source = "The New York Times" # May be more sources in the future, for now just NYT.
    obit_headline = i['headline']['main']
    obit_date = datetime.strftime(datetime.strptime(i['pub_date'],"%Y-%m-%dT%H:%M:%SZ"),"%B %d, %Y") # Dates are annoying, right? This line converts NYT's ISO formatted pub_date to a human-readable format.
    dead_person = re.match("[^,]*",obit_headline).group() # guesses the name of the person by the headline up until the comma. Brittle, but matches NYT syntax without fail so far.
    obit_URL = i['web_url']

    print("A copy of all documents or FBI files pertaining to " + dead_person + ", an obituary of whom was published in " + obit_source + " on " + obit_date + " under the headline \"" + obit_headline + "\" and can be found at " + obit_URL + ".")
