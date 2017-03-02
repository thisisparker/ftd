#!/usr/bin/env python3
# Creates a set of static HTML documents from source material in 
# the FOIA The Dead database.

# TODO: Create command line flags for partial updates

import dominate, html2text, json, os, sqlite3, time, urllib, yaml
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
        meta(name="viewport", 
            content="width=device-width, initial-scale=1")
        link(rel="stylesheet", 
            href= urllib.parse.urljoin(home, "normalize.css"))
        link(rel="stylesheet",
            href= urllib.parse.urljoin(home, "main.css"))

        meta(name="twitter:card", content="summary")
        meta(name="twitter:site", content="@FOIAtheDead")
        meta(name="twitter:image", content=logo_url)

        meta(property="og:image", content=logo_url)

    h.body.add(div(id=name) for name in ["header",
        "content","footer"])

    h.body[0].add(a(img(src=logo_url, id="logo"),href=home))

    h.body[2].add(div("© 2017 FOIA The Dead", id="copyright"))
    return h

def create_homepage(entries):
    pagecount = sum([entry['pages'] for entry in entries])
    entrycount = len(entries)

    h = create_boilerplate_html()

    with h.head:
        meta(name="twitter:title", content="FOIA The Dead")
        meta(name="twitter:description", content="A transparency project requesting and releasing the FBI files of notable individuals found in the obituary pages.")

        meta(property="og:url", content=home)
        meta(property="og:title", content=h.title)
        meta(property="og:description", content="A transparency project requesting and releasing the FBI files of notable individuals found in the obituary pages.")

        comment("Looking to scrape this page? Almost everything is available in entries.json.")
        

    headline = h1("FOIA The Dead has released {pagecount:,} pages of FBI records on {entrycount} public figures. ".format(**locals()), id="headline", __pretty = False)
    about_link = a("read more »", href="about.html",
        id="about-link")

    h.body[0].add(headline).add(about_link)
    l = h.body[1].add(ul(id="results-list"))

    for entry in entries:
        post_link = urllib.parse.urljoin("posts/", 
            entry['slug'] + ".html")
        tile = l.add(li(h2(a(entry['name'], href=post_link))))
        obit_link = a(entry['headline'], 
            href=entry['obit_url'])

        with tile:
            if entry['short_desc']:
                text(entry['short_desc'], escape=False)
            p(a("Read more »", href=post_link))
            p("New York Times obit: ",
                __pretty = False).add(obit_link)

    with open("site/index.html","w") as f:
        f.write(h.render())    

def populate_posts(entries):
    for entry in entries:
        populate_post(entry)
    
def populate_post(entry):
    h = create_boilerplate_html()   
    h.title = entry['name'] + ": FOIA The Dead"

    with h.head:
        meta(name="twitter:title", content=h.title)
        meta(name="twitter:description", 
            content=entry['twitter_desc'])

        post_url = urllib.parse.urljoin(home, "posts/" + 
            entry['slug'] + ".html")

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
    h = create_boilerplate_html()

    h.body[0].add(h1(a("FOIA The Dead", href=home)))

    h.body[1].add(h2("Sorry, this page is broken :(",
        id="error-text"))

    with open("site/error.html", "w") as f:
        f.write(h.render())

def create_about_page():
    h = create_boilerplate_html()

    h.title = "About FOIA The Dead"

    with h.head:
        meta(name="twitter:title", content=h.title)
        meta(name="twitter:description", 
            content="FOIA The Dead is a long-term transparency project using the Freedom of Information Act. It releases FBI records on recently deceased public figures.")

        about_url = urllib.parse.urljoin(home, "about.html")

        meta(property="og:url", content=about_url)
        meta(property="og:title", content=h.title)
        meta(property="og:description", 
            content="FOIA The Dead is a long-term transparency project using the Freedom of Information Act. It releases FBI records on recently deceased public figures.")

    h.body['class'] = "about-page"

    h.body[0].add(h1("About FOIA The Dead"))

    about_text="""<p>FOIA The Dead is a long-term transparency project that uses the <a href="https://en.wikipedia.org/wiki/Freedom_of_Information_Act_(United_States)">Freedom of Information Act (FOIA)</a> to request information from the FBI about the recently deceased.</p>

<p>That law requires certain government agencies to produce records upon a request from the public. One significant exception to that requirement is that, to protect the privacy of individuals, federal agencies may not release information about living people. But after their death, their privacy concerns are diminished, and those records can become available.</p>

<p>FOIA The Dead was founded to address that transition. When somebody's obituary appears in the <i>New York Times</i>, FOIA The Dead sends an automated request to the FBI for their (newly-available) records. In many cases, the FBI responds that it has no files on the individual. But in some cases it does, and can now release those files upon request. When FOIA The Dead receives it, the file gets published for the world to see.</p>

<p>This project is written and maintained by <a href="https://twitter.com/xor">Parker Higgins</a>. You can <a href="https://twitter.com/foiathedead">follow it on Twitter</a>. Source code is <a href="https://github.com/thisisparker/ftd/">available on GitHub</a>, and most of the site is <a href="https://foiathedead.org/entries.json">available as JSON</a>. Special thanks to <a href="https://twitter.com/trevortimm">Trevor Timm</a> and the <a href="https://freedom.press">Freedom of the Press Foundation</a> for their support.</p>"""

    with h.body[1]:
        text(about_text, escape=False)

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

    if hp:
        create_homepage(entries)

    if about:
        create_about_page()

    if posts:
        populate_posts(entries)

    if error:
        create_error_page()


if __name__ == '__main__':
    main()
