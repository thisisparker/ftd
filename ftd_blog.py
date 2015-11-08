#!/usr/bin/env python3
# New blog posts from the FOIA The Dead Script.
# Up first: just a digest of new requests.

import yaml, sqlite3
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

config = yaml.load(open("config.yaml"))

site = config['wp_site']
user = config['wp_user']
pw = config['wp_password']

wp = Client(site,user,pw)

db = config['db']
conn = sqlite3.connect(db)

def main():
    requests_digest()

def requests_digest():

    c = conn.cursor()
    
    c.execute('select name, obit_headline, obit_url, requested_at from requests where request_blogged_at is null')
    unblogged = c.fetchall()

    post_content = """We've recently requested the FBI files of the following individuals:

    <ul>"""

    for entry in unblogged:
        name = entry[0]
        obit_headline = entry[1]
        obit_url = entry[2]
        
        post_content += "\n<li>{name} (<a href=\"{obit_url}\">New York Times obit</a>)</li>".format(**locals())

    post = WordPressPost()
    today = datetime.strftime(datetime.today(),'%B %-d, %Y')
    post.title = 'New requests for FBI files, ' + today    
    post.content = post_content

    post.terms_names = {
        'category':['Requests']
    }
    
    wp.call(NewPost(post))

    #todo update the db with request_blogged_at and request_blog_url values

if __name__ == "__main__":
    main()
