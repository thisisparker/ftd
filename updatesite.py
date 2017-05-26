#!/usr/bin/env python3
# Creates a set of static HTML documents from source material in 
# the FOIA The Dead database.

import dominate
import html2text
import json
import markdown
import os
import sys
import sqlite3
import time
import urllib
import yaml
from documentcloud import DocumentCloud
from dominate.tags import *
from dominate.util import text

config = yaml.load(open("config.yaml"))
dc = DocumentCloud(config['dc_user'],config['dc_password'])

home = "https://foiathedead.org"

def create_boilerplate_html():
    h = dominate.document()
    h.title = "FOIA The Dead: a morbid transparency project"

    logo_url = urllib.parse.urljoin(home, "imgs/ftd-logo.png")

    with h.head:
        meta(charset="utf-8")
        meta(
            name="viewport", 
            content="width=device-width, initial-scale=1")
        link(
            rel="stylesheet", 
            href= urllib.parse.urljoin(home, "normalize.css"))
        link(
            rel="stylesheet",
            href= urllib.parse.urljoin(home, "main.css"))

        meta(name="twitter:card", content="summary")
        meta(name="twitter:site", content="@FOIAtheDead")
        meta(name="twitter:image", content=logo_url)

        meta(property="og:image", content=logo_url)

    h.body.add(
        div(id=name) for name in ["header","content","footer"])

    h.body[0].add(a(img(src=logo_url, id="logo"),href=home))

    h.body[2].add(div(id="copyright"))

    cc_by_img_url = urllib.parse.urljoin(home, "imgs/cc-by.png")

    with h.body.getElementById('copyright'):
        text('<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="{}" /></a>  FOIA The Dead is licensed under <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons BY 4.0</a>.'.format(cc_by_img_url), escape = False)

    return h

def create_homepage(entries):
    print("Updating homepage.")
    pagecount = sum([entry['pages'] for entry in entries])
    entrycount = len(entries)

    h = create_boilerplate_html()

    with h.head:
        meta(
            name="description",
            content="A transparency project requesting and releasing the FBI files of notable individuals found in the obituary pages.")

        meta(name="twitter:title", content="FOIA The Dead")
        meta(
            name="twitter:description",
            content="A transparency project requesting and releasing the FBI files of notable individuals found in the obituary pages.")

        meta(property="og:url", content=home)
        meta(property="og:title", content=h.title)
        meta(
            property="og:description",
            content="A transparency project requesting and releasing the FBI files of notable individuals found in the obituary pages.")

        comment("Looking to scrape this page? Almost everything is available in entries.json.")
        

    headline = h1(
        "FOIA The Dead has released {pagecount:,} pages of FBI records on {entrycount} public figures. ".format(**locals()),
        id="headline", __pretty = False)
    about_link = a("read more »", href="about.html",
        id="about-link")

    h.body[0].add(headline).add(about_link)
    l = h.body[1].add(ul(id="results-list"))

    for entry in entries:
        post_link = urllib.parse.urljoin(
            "posts/", entry['slug'] + ".html")
        tile = l.add(li(h2(a(entry['name'], href=post_link))))
        obit_link = a(
            entry['headline'], href=entry['obit_url'])

        with tile:
            if entry['short_desc']:
                text(entry['short_desc'], escape = False)
            p(a("Read more »", href=post_link))
            p("New York Times obit: ",
                __pretty = False).add(obit_link)

    with open("site/index.html","w") as f:
        f.write(h.render())    

def populate_posts(entries):
    print("Updating posts.")
    for entry in entries:
        populate_post(entry)
    
def populate_post(entry):
    h = create_boilerplate_html()   
    h.title = entry['name'] + ": FOIA The Dead"

    with h.head:
        meta(name="twitter:title", content=h.title)
        meta(
            name="twitter:description", 
            content=entry['twitter_desc'])

        post_url = urllib.parse.urljoin(
            home, "posts/" + entry['slug'] + ".html")

        meta(property="og:url", content=post_url)
        meta(property="og:title", content=h.title)
        meta(property="og:description", content=entry['fb_desc'])

    h.body['class'] = "post-page"

    h.body[0].add(h1(a("FOIA The Dead", href=home)))
    h.body[0].add(h2(entry['name']))

    dc_embed = '<div class="DC-embed DC-embed-document DV-container"><div style="position:relative;padding-bottom:129.444444444%;height:0;overflow:hidden;max-width:100%;"><iframe src="https://www.documentcloud.org/documents/{}.html?embed=true&amp;responsive=false&amp;sidebar=false" title="{} (Hosted by DocumentCloud)" sandbox="allow-scripts allow-same-origin allow-popups" frameborder="0" style="position:absolute;top:0;left:0;width:100%;height:100%;border:1px solid #aaa;border-bottom:0;box-sizing:border-box;"></iframe></div></div>'.format(entry['documentcloud_id'],entry['name'])

    with h.body[1]:
        
        with div(id="description"):
            if entry['long_desc']:
                text(entry['long_desc'], escape=False)
            elif entry['short_desc']:
                text(entry['short_desc'], escape=False)

        obit_link = a(entry['headline'], href=entry['obit_url'])
        p("New York Times obit: ", __pretty = False).add(obit_link)

        
        text(dc_embed, escape=False)
        

    path = os.path.join("site/posts/",entry['slug'] + ".html")
    with open(path, "w") as f:
        f.write(h.render())

def create_error_page():
    print("Updating error page.")

    h = create_boilerplate_html()

    h.body[0].add(h1(a("FOIA The Dead", href=home)))

    h.body[1].add(h2(
        "Sorry, this page is broken :(", id="error-text"))

    with open("site/error.html", "w") as f:
        f.write(h.render())

def create_about_page():
    print("Updating about page.")

    h = create_boilerplate_html()

    h.title = "About FOIA The Dead"

    with h.head:
        meta(name="twitter:title", content=h.title)
        meta(
            name="twitter:description", 
            content="FOIA The Dead is a long-term transparency project using the Freedom of Information Act. It releases FBI records on recently deceased public figures.")

        about_url = urllib.parse.urljoin(home, "about.html")

        meta(property="og:url", content=about_url)
        meta(property="og:title", content=h.title)
        meta(
            property="og:description", 
            content="FOIA The Dead is a long-term transparency project using the Freedom of Information Act. It releases FBI records on recently deceased public figures.")

    h.body['class'] = "about-page"

    h.body[0].add(h1(a("FOIA The Dead", href=home)))
    h.body[0].add(h2("About this project"))

    with open("site/about.md","r") as f:
        about_text = f.read()
    
    about_html = markdown.markdown(about_text)

    with h.body[1]:
        text(about_html, escape=False)

    with open("site/about.html", "w") as f:
        f.write(h.render())

def create_entries_list(cursor):
    if not os.path.exists("site/entries.json"):
        with open("site/entries.json","w") as f:
            json.dump([],f)

    with open("site/entries.json", "r") as f:
        entries = json.load(f)

    db_entries = []

    for values in cursor.execute('select name, slug, obit_headline, obit_url, documentcloud_id, short_description, long_description from requests where documentcloud_id is not null order by id desc'):
        keys = ['name', 'slug', 'headline', 'obit_url',
                'documentcloud_id', 'short_desc', 'long_desc']  
        db_entry = dict(zip(keys,values))

        if db_entry['name'] not in (
            [entry['name'] for entry in entries]):
            entries.insert(0, add_new_entry(db_entry)) 

    with open("site/entries.json", "w") as f:
        json.dump(entries, f, indent=4, sort_keys=True)

    return entries

def add_new_entry(entry):
    entry['documentcloud_url'] = urllib.parse.urljoin(
            "https://www.documentcloud.org/documents/",
            entry['documentcloud_id'])

    entry['pages'] = get_pagecount(entry['documentcloud_id'])

    html_parser = html2text.HTML2Text(bodywidth=0)
    html_parser.ignore_links = True

    if entry['short_desc']:
        entry['twitter_desc'] = html_parser.handle(
            entry['short_desc']).strip()
    else:
        entry['twitter_desc'] = "FBI file and information about {}.".format(entry['name'])

    entry['fb_desc'] = entry['twitter_desc']

    return entry


def get_pagecount(doc):
    print("Fetching pagecount for {}.".format(doc))
    time.sleep(1)
    return dc.documents.get(doc).pages

def main(hp=True, about=True, posts=False, error=False):
    db = config['db']
    conn = sqlite3.connect(db)
    c = conn.cursor()

    entries = create_entries_list(c)

    if len(sys.argv) < 2:
        print("""By default this program will just update the list of entries tracked by the site. To update actual pages, add any of the following flags:
--home
--about
--posts
--error""")

    if "--home" in sys.argv:
        create_homepage(entries)

    if "--about" in sys.argv:
        create_about_page()

    if "--posts" in sys.argv:
        populate_posts(entries)

    if "--error" in sys.argv:
        create_error_page()

if __name__ == '__main__':
    main()
