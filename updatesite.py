#!/usr/bin/env python3
# Creates a static HTML document from source material in the
# FOIA The Dead database.

import dominate, os, sqlite3, time, urllib, yaml
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

    h.body.add(div(id=name) for name in ["header",
        "content","footer"])

    h.body[0].add(a(img(src=logo_url, id="logo"),href=home))

    h.body[2].add(div("© 2017 FOIA The Dead", id="copyright"))
    return h

def create_homepage(entries):
    pagecount = sum([get_pagecount(entry['documentcloud_id']) 
        for entry in entries])
    entrycount = len(entries)

    h = create_boilerplate_html()

    with h.head:
        meta(name="twitter:title", content="FOIA The Dead")
        meta(name="twitter:description", content="A transparency project requesting and releasing the FBI files of notable indivuals found in the obituary pages.")

    h.body[0].add(h1("FOIA The Dead has released {pagecount:,} pages of FBI records on {entrycount} public figures.".format(**locals()), id="headline"))
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
        meta(name="twitter:description", content="FBI file and information about " + entry['name'])

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

def create_entries_list(cursor):

    #TODO: Store the current state of some of this stuff
    # (especially page count, which changes never) so builds
    # can be more incremental

    entries = []
    for values in cursor.execute('select name, slug, obit_headline, obit_url, documentcloud_id, short_description, long_description from requests where documentcloud_id is not null order by id desc'):
        keys = ['name', 'slug', 'headline', 'obit_url',
            'documentcloud_id', 'short_desc', 'long_desc']  
        entry = dict(zip(keys,values))
        entry['documentcloud_url'] = urllib.parse.urljoin(
            "https://www.documentcloud.org/documents/",
            entry['documentcloud_id'])
#        entry['pages'] = get_pagecount(entry['documentcloud_id'])

        entries.append(entry)
    return entries

def get_pagecount(doc):
    print("Fetching pagecount for {}.".format(doc))
    time.sleep(1)
    return dc.documents.get(doc).pages

def main(hp=True, posts=False, error=False):
    db = config['db']
    conn = sqlite3.connect(db)
    c = conn.cursor()

    entries = create_entries_list(c)

    if hp:
        create_homepage(entries)

    if posts:
        populate_posts(entries)

    if error:
        create_error_page()


if __name__ == '__main__':
    main()