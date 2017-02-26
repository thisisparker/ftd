#!/usr/bin/env python3
# Creates a static HTML document from source material in the
# FOIA The Dead database.

import dominate, os, sqlite3, urllib
from documentcloud import DocumentCloud
from dominate.tags import *

def create_boilerplate_html():
    h = dominate.document()
    h.title = "FOIA The Dead: a morbid transparency project"
    return h

def create_entries_list(cursor):
    entries = []
    for values in cursor.execute('select name, obit_headline, obit_url, documentcloud_id from requests where documentcloud_id is not null order by id desc'):
        keys = ['name','headline','obit_url','documentcloud_id']  
        entry = dict(zip(keys,values))
        entry['documentcloud_url'] = urllib.parse.urljoin(
            "https://www.documentcloud.org/documents/",
            entry['documentcloud_id'])
        entries.append(entry)
    return entries

def get_pagecount(docs, dc):
    pagecount = 0
    for doc in docs:
        pagecount += dc.documents.get(doc).pages
    return pagecount

def main():
#    db = config['db']
    db = "bak.db"
    conn = sqlite3.connect(db)
    c = conn.cursor()

    dc = DocumentCloud()

    entries = create_entries_list(c)
    
    docs = [entry['documentcloud_id'] for entry in entries]

    pagecount = get_pagecount(docs, dc)
    entrycount = len(entries)

    h = create_boilerplate_html()
    h.body.add(h1("FOIA The Dead has released {pagecount} pages of files on {entrycount} public figures.".format(**locals()), id="headline"))
    l = h.body.add(ul(id="results-list"))        

    for item in entries:
        entry = l.add(li(h2(item['name'])))
        obit_link = a(item['headline'], 
            href=item['obit_url'])
        file_link = a("FBI file", href=item['documentcloud_url'])
        entry.add(p("New York Times obit: ",
            __pretty = False)).add(obit_link)
        entry.add(p(file_link, __pretty = False))

    print(h)

    with open("index.html","w") as f:
        f.write(h.render())

if __name__ == '__main__':
    main()
