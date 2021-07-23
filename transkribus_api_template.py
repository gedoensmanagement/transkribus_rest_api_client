#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Template for using the Transkribus API. (Python 3.6+) """

import requests
import sys
from lxml import objectify

# Define building blocks for the endpoints:
api_base_url = "https://transkribus.eu/TrpServer/rest/"
login_endpoint = "auth/login"
collections_endpoint = "collections/list"
logout_endpoint = "auth/logout"

# Log in:
## Prepare the payload for the POST request:
credentials = {'user': 'YOUR_USER_NAME',
               'pw': 'YOUR_PASSWORD'}
## Create the POST request (the requests package converts the credentials into JSON automatically):
response = requests.post(api_base_url + login_endpoint, data=credentials)

## Evaluate the response:
if response:
    r = objectify.fromstring(response.content)
    print(f"TRANSKRIBUS: User {r.firstname} {r.lastname} ({r.userId}) logged in successfully.")
    session_id = str(r.sessionId)
else:
    sys.exit("TRANSKRIBUS: Login failed. Check your credentials!")

# Get the list of collections (using a GET request):
cookies = dict(JSESSIONID=session_id)
response = requests.get(api_base_url + collections_endpoint, cookies=cookies)
if response:
    collections = response.json()
    print("TRANSKRIBUS: Your collections:")
    for collection in collections:
        print(f"– {collection['colName']}, ({collection['nrOfDocuments']} document(s))")
else:
    sys.exit("TRANSKRIBUS: Could not retrieve collections.")

# Log out (using a POST request):
response = requests.post(api_base_url + logout_endpoint, cookies=cookies)
if response:
    print("TRANSKRIBUS: Logged out successfully!")
else:
    sys.exit("TRANSKRIBUS: Logout failed.")
