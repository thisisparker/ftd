#!/usr/bin/env python3
# Grabs the last 10 NYT obits and prepares the text of a FOIA request for
# their FBI files, then sends that request to the FBI

import os, requests, json, datetime, smtplib, email.utils, sqlite3
import yaml, pdfkit, html
import ftd_tweets
from datetime import datetime

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

config = yaml.load(open("config.yaml"))

db = config['db']
conn = sqlite3.connect(db)

# Note: as the db gets bigger, this should take a slice.
# For now, it's fine and fast enough to just check against all past requests.

recent_requests_tuples = list(conn.execute('select name,obit_headline from requests order by id desc'))
recent_requests_names, recent_requests_headlines = map(list, zip(*recent_requests_tuples))

nyt_api_key = config['nyt_api_key']

api_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?fq=type_of_material:%28%22Obituary%22%29&sort=newest&fl=headline,web_url,snippet,pub_date&api-key=" + nyt_api_key

res = requests.get(api_url)
res.raise_for_status()

api_results = json.loads(res.text)

docs = api_results['response']['docs']

from_name = config['from_name']
from_address = config['from_address']
email_pw = config['email_pw']
mailing_address = config['mailing_address']

recipient_name = config['recipient_name']
recipient_address = config['recipient_address']

server = smtplib.SMTP(config['smtp_server'],587,timeout=120)

to_send = []

def editname(headline):
    name_check = "n"
    while name_check == "n":
        print("\nOK, you can edit the name. Here's what the headline says:\n".format(**locals()))
        print("{headline}\n".format(**locals()))
        new_name = input("What's the name? ")
        name_check = input("\nRoger that. Does {new_name} look good? (Y/n) ".format(**locals()))
    return new_name

for obit in docs:
    obit_source = "The New York Times" # May be more sources in the future, for now just NYT.
    obit_headline = html.unescape(obit['headline']['main'])

    # This line converts NYT's ISO formatted pub_date to a human-readable format.
    obit_date = datetime.strftime(datetime.strptime(obit['pub_date'],"%Y-%m-%dT%H:%M:%SZ"),"%B %-d, %Y") 

    # guesses the name of the person by the headline up until the comma. 
    # Brittle, but matches NYT syntax mostly without fail so far.
    dead_person = obit_headline.split(",")[0] 

    obit_url = obit['web_url']
    # Removed the following line because it doesn't do well with non-standard headlines. 
    # Might try to figure out how to get it back in.
    # obit_description = obit_headline.split(", Dies")[0].split(dead_person + ", ")[1] 

    doc_request = "A copy of all documents or FBI files pertaining to {dead_person}, an obituary of whom was published in {obit_source} on {obit_date} under the headline \"{obit_headline}\". Please see attached PDF copy of that obituary, which may also be found at {obit_url}.".format(**locals())

    print("\nPreparing an email from {from_address} with the following request:\n".format(**locals()))

    print(doc_request)

    if dead_person in recent_requests_names:
        print("\nBut it looks like you've already sent a request for {dead_person}.".format(**locals()))
    elif obit_headline in recent_requests_headlines:
        print("\nBut it looks like you've already sent a request for the obit \"{obit_headline}\".".format(**locals()))

    should_request = input("\nLook good? (Y)es/(e)dit/(s)kip/(q)uit ")

    if should_request == "" or should_request == "y" or should_request == "Y":

        now_string = str(datetime.utcnow())

        to_send.append([dead_person,doc_request,obit_url,obit_headline,now_string])

# Below section would tweet, but holding off for now.

#        should_tweet = input("\nTweet this request? Y/n ")
#
#        if should_tweet == "" or should_tweet == "Y":
#            ftd_tweets.tweet_request(dead_person,obit_url)

    elif should_request == "e":
        new_name = editname(obit_headline)
        doc_request = "A copy of all documents or FBI files pertaining to {new_name}, an obituary of whom was published in {obit_source} on {obit_date} under the headline \"{obit_headline}\". Please see attached PDF copy of that obituary, which may also be found at {obit_url}.".format(**locals())
        now_string = str(datetime.utcnow())
        to_send.append([new_name,doc_request,obit_url,obit_headline,now_string])

    elif should_request == "s":
        continue

    elif should_request == "q":
        break

if to_send:
    server.starttls()
    server.ehlo()
    server.login(from_address, email_pw)

for request in to_send:

    req_name = request[0]
    req_request = request[1]
    req_url = request[2]
    req_headline = request[3]
    req_time = request[4]

    email_text = """
FBI
Record/Information Dissemination Section
Attn: FOI/PA Request
170 Marcel Drive
Winchester, VA 22602-4843

To whom it may concern:

This is a request under 5 U.S.C. § 552, the Freedom of Information Act. I hereby request the following records:

{req_request}

The requested documents will be made available to the general public, and this request is not being made for commercial purposes.

FOIA has always presumed that government records are open to public inspection, and the FOIA Improvement Act of 2016, Pub. L. 114-185, prohibits agencies from withholding records unless (1) "disclosure is prohibited by law" or (2) "the agency reasonably foresees that disclosure would harm an interest protected by" one of FOIA's exemptions. Id., §2, codified at 5 U.S.C. § 552(a)(8)(A). Thus, in addition to FOIA favoring disclosure and requiring its exemptions to be narrowly construed, Section 552(a)(8)(A) prohibits agencies from using their discretion to broadly withhold records merely because they believe an exemption could technically apply.

FOIA The Dead is a noncommercial organization that uses Freedom of Information Act requests to gather information of interest to a segment of the general public, and uses its editorial skills to turn those raw materials into distinct works. It distributes those works free of charge to the general public on its website, foiathedead.org. As such, I believe I qualify as a representative of the news media for the purposes of this request.

Additionally, because FOIA The Dead is a noncommercial organization, this request cannot be construed to be in its or my commercial interest. Finally, I believe that documents responsive to this request are likely to contribute significantly to public understanding of the operations or activities of the government by demonstrating how the FBI as a governmental agency collects, organizes, and stores information about the prominent individual in question.

Considering these three factors, my request should be furnished without charge or at a rate reduced below the standard charge, as described in 5 U.S.C. § 552(A)(4)(a)(iii). Failing that, fees should be limited to the reasonable standard charges for document duplication, as described in 5 U.S.C. § 552(A)(4)(a)(ii).

I am willing to pay up to $25 for the processing of this request. Please inform me if the estimated fees will exceed this limit before processing my request.

Thank you for your consideration in this matter. I look forward to receiving your response to this request within 20 business days, as the statute requires.

Parker Higgins
FOIA The Dead
{mailing_address}""".format(**locals())

    print("\nHandcrafting a PDF of the obituary of {req_name}.".format(**locals()))

    req_pdf_filename = req_name.lower().replace(" ","-") + "-nyt-obit.pdf"
    try:
        pdfkit.from_url(req_url, "pdfs/" + req_pdf_filename,options={'quiet':''})
    except OSError as error:
        if "code 1" in str(error):
            print("\nAn OSError occurred, but it's probably not a big deal.")
        else:
            print("\n!!! NOT SENDING a request for {req_name}, due to this error:\n {error}".format(**locals()))
            continue

    print("\nSending FOIA request for {req_name} file via email.".format(**locals()))

    email_subject = "FOIA Request, " + req_name

    msg = MIMEMultipart()
    msg['Subject'] = Header(email_subject, 'utf-8')
    msg['From'] = email.utils.formataddr((from_name,from_address))
    msg['To'] = email.utils.formataddr((recipient_name,recipient_address))

    msg.attach(MIMEText(email_text, 'plain', 'utf-8'))

    attachment = MIMEBase('application', "octet-stream", name=req_pdf_filename)
    attachment.set_payload(open("pdfs/" + req_pdf_filename,"rb").read())
    encoders.encode_base64(attachment)

    attachment.add_header('Content_Disposition','attachment',filename=req_pdf_filename)

    msg.attach(attachment)

    server.sendmail(from_address, [recipient_address,config['bcc_address']], msg.as_string())

    conn.execute("""
    insert into requests (name, obit_headline, obit_url, requested_at)
    values ('{req_name}','{req_headline}','{req_url}','{req_time}')
    """.format(**locals()))

    conn.commit()
    
server.quit()

conn.close()

print("\nAll done. Pleasure doing business with you.")
