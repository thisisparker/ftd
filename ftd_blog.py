#!/usr/bin/env python3
# New blog posts from the FOIA The Dead Script.
# Up first: just a digest of new requests.

import yaml
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

config = yaml.load(open("config.yaml"))

site = config['wp_site']
user = config['wp_user']
pw = config['wp_password']

wp = Client(site,user,pw)

def main():
    requests_digest()

def requests_digest():

    post = WordPressPost()
    today = datetime.strftime(datetime.today(),'%B %-d, %Y')
    post.title = 'New requests for FBI files, ' + today    
    post.content = "We've recently requested the FBI files of the following individuals:"
    #todo: the hard work of pulling in the recent requests via the db
    post.terms_names = {
        'category':['Requests']
    }
    
    wp.call(NewPost(post))

if __name__ == "__main__":
    main()
