#!/usr/bin/env python
#
# This illustrates the call-flow required to complete an OAuth request
# against the discogs.com API, using python3-discogs-client libary.
# The script will download and save a single image and perform and
# an API search API as an example. See README.md for further documentation.

#Generate an HTML table containing collection information to insert into a web page. The table can be retrieved from tmp/table.txt

import sys

import discogs_client
from discogs_client.exceptions import HTTPError
from collections import Counter

class Tee:
    def write(self, *args, **kwargs):
        self.out1.write(*args, **kwargs)
        self.out2.write(*args, **kwargs)
    def __init__(self, out1, out2):
        self.out1 = out1
        self.out2 = out2
    def flush(self):
        pass


# Your consumer key and consumer secret generated and provided by Discogs.
# See http://www.discogs.com/settings/developers . These credentials
# are assigned by application and remain static for the lifetime of your discogs
# application. the consumer details below were generated for the
# 'discogs-oauth-example' application.
# NOTE: these keys are typically kept SECRET. I have requested these for
# demonstration purposes.

consumer_key = ''
consumer_secret = ''

# A user-agent is required with Discogs API requests. Be sure to make your
# user-agent unique, or you may get a bad response.
user_agent = 'update_me_test/2.0'

# instantiate our discogs_client object.
discogsclient = discogs_client.Client(user_agent)

# prepare the client with our API consumer data.
discogsclient.set_consumer_key(consumer_key, consumer_secret)
token, secret, url = discogsclient.get_authorize_url()

print(' == Request Token == ')
print(f'    * oauth_token        = {token}')
print(f'    * oauth_token_secret = {secret}')
print()
print(f'Please browse to the following URL {url}')

# Waiting for user input. Here they must enter the verifier key that was
# provided at the unqiue URL generated above.
oauth_verifier = input('Verification code : ')


try:
    access_token, access_secret = discogsclient.get_access_token(oauth_verifier)
except HTTPError:
    print('Unable to authenticate.')
    sys.exit(1)

# fetch the identity object for the current logged in user.
user = discogsclient.identity()
print(user)

print
print(' == User ==')
print(f'    * username           = {user.username}')
print(f'    * name               = {user.name}')
print(' == Access Token ==')
print(f'    * oauth_token        = {access_token}')
print(f'    * oauth_token_secret = {access_secret}')
print(' Authentication complete. Future requests will be signed with the above tokens.')

#identifier for item in table
itemNum = 1

#collection_folder examples supporting custom folders
#these values are unique to my discogs profile
#0 is all
#1 is my custom buy folder
#2 is custom review folder for debugging
#
sys.stdout = Tee(open("tmp/table.txt", "w"), sys.stdout)

#Generate table
print("<table><thead>", end="")
print("<tr><th></th><th>TITLE</th><th>ARTISTS</th><th>GENRE</th><th>CAT#</th><th></th><th>ADD</th></tr></thead><tbody>")

for item in user.collection_folders[1].releases:

    #set variables to store information on each release
    image = item.release.images[0]['uri']
    artist = item.release.artists[0]
    genre = item.release.genres[0]
    style = item.release.styles[0]
    label = item.release.labels[0]

    #extra table tags
    print("<tr>", end="")
    print("<td>", end="")
    print(itemNum, end="")
    print("</td>", end="")    
    #title
    print("<td>", end="")
    print(item.release.title, end="")
    print("</td>", end="")
    #artist
    print("<td>", end="")
    print(artist.name, end="")
    print("</td>", end="")
    #genre, style gives a more detailed genre compared to genre
    print("<td>", end="")
    #print(genre, end="")
    print(style, end="")
    print("</td>", end="")
    #cat num
    print("<td>", end="")
    print(label.catno, end="")
    print("</td>", end="")
    #image and discogs link
    print("<td>", end="")
    print("<a target='_blank' href='", end="")
    print(item.release.fetch('uri'), end="")
    print("'>", end="")
    print("<img href='shop.html' src='", end="")
    print(item.release.images[0]['uri'], end="")
    print("' width='100' height='80'>", end="")
    print("</a>", end="")
    #buy checkbox, contains title, value and id
    print("<td>", end="")
    print("<input type='checkbox' name='addToCart' ", end="")
    print("value='", end="")
    #print(id, end="")
    print(item.release.title, end="")
    print("' ", end="")
    print("id='", end="")
    print(label.catno, end="")
    print("'>", end="")
    print("</td>", end="")
    print("</td></tr>")

    itemNum += 1
    
print("</tbody></table>", end="")

content, resp = discogsclient._fetcher.fetch(None, 'GET', image,
                headers={'User-agent': discogsclient.user_agent})
