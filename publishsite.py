#!/usr/bin/env python3
# Publishes static site created by updatesite.py to Amazon S3.

import boto3, mimetypes, os

def main():
    s3 = boto3.resource('s3')

    os.chdir('site')

    contents = [os.path.join(root, leaf) for root, folders, files in os.walk(".") for leaf in files]
    keys = [leaf.lstrip("./") for leaf in contents]

    for index in range(len(contents)):
        print("Uploading " + keys[index])
    
        mime = mimetypes.guess_type(keys[index])

        s3.meta.client.upload_file(contents[index],
            "foiathedead.org", keys[index], ExtraArgs =         
            {'ContentType':mime[0]})

    print("All uploaded.")

if __name__ == "__main__":
    main()
