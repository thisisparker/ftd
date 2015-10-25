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

    email_text = """
FBI
Record/Information Dissemination Section
Attn: FOI/PA Request
170 Marcel Drive
Winchester, VA 22602-4843

To whom it may concern:

This is a request under 5 U.S.C. § 552, the Freedom of Information Act. I hereby request the following records:

A copy of all documents or FBI files pertaining to {dead_person}, an obituary of whom was published in {obit_source} on {obit_date} under the headline \"{obit_headline}\" and can be found at {obit_URL}.

The requested documents will be made available to the general public, and this request is not being made for commercial purposes.

The noncommercial organization with which I am affiliated, FOIA The Dead, gathers through the Freedom of Information Act information of interest to a segment of the general public and uses its editorial skills to turn those raw materials into distinct works. It distributes those works free of charge to the general public on its website, foiathedead.org. As such, I believe I qualify as a representative of the news media for the purposes of this request.

Additionally, because FOIA The Dead is a noncommercial organization, this request cannot be construed to be in its or my commercial interest. Finally, I believe that documents responsive to this request are likely to contribute significantly to public understanding of the operations or activities of the government by demonstrating how the FBI as a governmental agency collects, organizes, and stores information about the prominent individual in question.

Considering these three factors, my request should be furnished without charge or at a rate reduced below the standard charge, as described in 5 U.S.C. § 552(A)(4)(a)(iii). Failing that, fees should be limited to the reasonable standard charges for document duplication, as described in 5 U.S.C. § 552(A)(4)(a)(ii).

I am willing to pay up to $25 for the processing of this request. Please inform me if the estimated fees will exceed this limit before processing my request.

Thank you for your consideration.

Parker Higgins
FOIA The Dead""".format(**locals())

    print(email_text)

    input()

