#!/usr/bin/env python3
# New blog posts from the FOIA The Dead Script.
# Currently posts digests of recent FOIA requests, with more blog types to come.

import yaml, sqlite3
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPost

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
    
    c.execute('select id, name, obit_headline, obit_url, requested_at from requests where request_blogged_at is null')
    unblogged = c.fetchall()

    post = WordPressPost()
    today = datetime.strftime(datetime.today(),'%B %-d, %Y')
    post.title = 'New requests for FBI files, ' + today    

    post.terms_names = {
        'category':['Requests'],
        'post_tag':[]
    }

    post.content = """We've recently requested the FBI files of the following individuals:

    <ul>"""
    

    for entry in unblogged:        
        name = entry[1]
        obit_headline = entry[2]
        obit_url = entry[3]
        
        post.content += "\n<li>{name} (<a href=\"{obit_url}\">New York Times obit</a>)</li>".format(**locals())
        post.terms_names['post_tag'].append(name.lower())

    post.post_status = 'publish'
    
    post_id = wp.call(NewPost(post))
    
    post_url = wp.call(GetPost(post_id)).link
    post_date = str(wp.call(GetPost(post_id)).date)    

    for entry in unblogged:
        entry_id = entry[0]
        c.execute('update requests set request_blogged_at = ?, request_blog_url = ? where id = ?',(post_date,post_url,entry_id))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
