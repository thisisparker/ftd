#!/usr/bin/env python3
# Grabs the last 10 NYT obits, prepares the text of a FOIA 
# request for their FBI files, and sends that request to the FBI.

import os, requests, json, datetime, sqlite3
import yaml, pdfkit, html
import boto3
from datetime import datetime
from slugify import slugify

config = yaml.load(open("config.yaml"))

db = config['db']
conn = sqlite3.connect(db)

def edit_name(headline):
    name_check = "n"
    while name_check == "n":
        print("\nOK, you can edit the name. Here's what the headline says:\n".format(**locals()))
        print("{headline}\n".format(**locals()))
        new_name = input("What's the name? ")
        name_check = input("\nRoger that. Does {new_name} look good? (Y/n) ".format(**locals()))
    return new_name

def nyt_api_request(key):
    """Query NYT API and return recent obits."""
    api_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?fq=type_of_material:%28%22Obituary%20%28Obit%29%22%29&sort=newest&fl=headline,web_url,snippet,pub_date&api-key=" + key

    res = requests.get(api_url)
    res.raise_for_status()

    api_results = json.loads(res.text)

    return api_results['response']['docs']

def get_past_requests():
    """Query db and return two lists: past names and headlines."""
    past_requests_tuples = list(conn.execute(
        'select name,obit_headline from requests order by id desc'))
    return map(list, zip(*past_requests_tuples))

def process_obit(obit, past_names, past_headlines):
    obit_source = "The New York Times" 
    # May be more sources in the future, for now just NYT.
    obit_headline = html.unescape(obit['headline']['main'])

    # This line converts NYT's ISO formatted pub_date 
    # to a human-readable format.
    obit_date = datetime.strftime(datetime.strptime(obit['pub_date'],"%Y-%m-%dT%H:%M:%S%z"),"%B %-d, %Y")
    pdf_date = datetime.strftime(datetime.strptime(obit['pub_date'],"%Y-%m-%dT%H:%M:%S%z"),"%Y%m%d")

    # guesses the name of the person by the headline up 
    # until the comma. 
    # Brittle, but matches NYT syntax mostly without fail so far.
    dead_person = obit_headline.split(",")[0] 

    obit_url = obit['web_url']

    doc_request = "A copy of all documents or FBI files pertaining to {dead_person}, an obituary of whom was published in {obit_source} on {obit_date} under the headline \"{obit_headline}\". Please see attached PDF copy of that obituary, which may also be found at {obit_url}.".format(**locals())

    print("\nPreparing a fax with the following request:\n")

    print(doc_request)

    if dead_person in past_names:
        print("\nBut it looks like you've already sent a request for {dead_person}.".format(**locals()))
    elif obit_headline in past_headlines:
        print("\nBut it looks like you've already sent a request for the obit \"{obit_headline}\".".format(**locals()))

    should_request = input("\nLook good? (Y)es/(e)dit/(s)kip/(q)uit ")

    if should_request == "" or should_request == "y" or should_request == "Y":

        now_string = str(datetime.utcnow())

        return [dead_person, doc_request, obit_url, 
            obit_headline, now_string, pdf_date]

    elif should_request == "e":
        new_name = edit_name(obit_headline)
        doc_request = "A copy of all documents or FBI files pertaining to {new_name}, an obituary of whom was published in {obit_source} on {obit_date} under the headline \"{obit_headline}\". Please see attached PDF copy of that obituary, which may also be found at {obit_url}.".format(**locals())
        now_string = str(datetime.utcnow())
        return [new_name, doc_request, obit_url, 
            obit_headline, now_string, pdf_date]

    elif should_request == "s":
        return None

    elif should_request == "q":
        return "q"

def send_muckrock(request):
    mr_url = config['mr_url']
    mr_token = config['mr_token']
    jurisdiction = config['mr_pk']
    agency = config['mr_agency']

    req_name = request[0]
    req_request = request[1]
    req_url = request[2]
    req_headline = request[3]
    req_time = request[4]
    req_date = request[5]

    print("\nHandcrafting a PDF of the obituary of {req_name}.".format(**locals()))

    slug = slugify(req_name)

    req_pdf_filename = slug + "-nyt-obit-" + req_date + ".pdf"

    try:
        pdfkit.from_url(req_url,
                "pdfs/" + req_pdf_filename,
                options={'quiet': '', 'disable-javascript': '', 'no-outline': '',
                         'no-images': '', 'page-size': 'letter'})
    except OSError as error:
        if "code 1" in str(error):
            print("\nAn OSError occurred, but it's probably not a big deal.")
        else:
            print("\n!!! NOT SENDING a request for {req_name}, due to this error:\n {error}".format(**locals()))
            return

    s3 = boto3.resource('s3')
    
    with open('pdfs/' + req_pdf_filename, 'rb') as f:
        s3.meta.client.upload_fileobj(f, "ftd-pdfs", 
            req_pdf_filename, 
            ExtraArgs = {'ContentType':'application/pdf'})

        print("\nUploading PDF to S3 as {req_pdf_filename}.".format(**locals()))

    req_pdf_url = config['s3_root'] + req_pdf_filename

    print("\nSending FOIA request for {req_name} file via Muckrock.".format(**locals()))

    mr_data = json.dumps({
        'jurisdiction': jurisdiction,
        'agency': agency,
        'title': req_name + ", FBI file",
        'document_request': req_request,
        'attachments': [req_pdf_url]})

    mr_headers = {'Authorization': 'Token {}'.format(mr_token),
        'content-type': 'application/json'}

    r = requests.post(mr_url + 'foia/',
        headers = mr_headers,
        data = mr_data)

    response = r.json()

    if response['status'] == 'FOI Request submitted':
        conn.execute("""
        insert into requests (name, obit_headline, obit_url, requested_at, slug)
        values ('{req_name}', '{req_headline}', '{req_url}', '{req_time}','{slug}')
        """.format(**locals()))

        conn.commit()

def main():
    docs = nyt_api_request(config['nyt_api_key'])

    past_names, past_headlines = get_past_requests()

    to_send = []

    for obit in docs:
        request = process_obit(obit, past_names, past_headlines)

        if request == "q":
            break
        elif request is not None:
            to_send.append(request)

    for request in to_send:
        send_muckrock(request)

    conn.close()

    print("\nAll done. Pleasure doing business with you.")

if __name__ == '__main__':
    main()
