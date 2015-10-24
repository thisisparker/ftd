#! python3
# currently prints the last 10 NYT obit headlines. But more is to come.

import os, requests, json

nyt_api_key = os.environ["NYT_API_KEY"]

api_url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?fq=type_of_material:%28%22Obituary%22%29&sort=newest&fl=headline,web_url,snippet,pub_date&api-key=" + nyt_api_key

res = requests.get(api_url)
res.raise_for_status()

api_results = json.loads(res.text)

docs = api_results['response']['docs']

for i in docs:
    print(i['headline']['main'])
