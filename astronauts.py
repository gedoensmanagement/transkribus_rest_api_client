#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" List the astronauts that are currently on the ISS
    using the Open Notify API: http://api.open-notify.org/ """

import requests
import json

# Build the URL using the "astros.json" endpoint:
api_base_url = "http://api.open-notify.org/"
endpoint = "astros.json"
url = api_base_url + endpoint

# Make a GET request and store the response:
response = requests.get(url)

# Evaluate the response:
if response:
    try:
        json_response = response.json()
        print("The raw JSON response sent by the server:")
        print(json.dumps(json_response))   
        print("\nPeople on the ISS:")
        for astronaut in json_response['people']:
            if astronaut['craft'] == "ISS":
                print("– " + astronaut['name'])
    except:
        print(f"ERROR: Something went wrong. {response.content}")
else:
    print(f"ERROR: Something went wrong. HTTP status code: {response.status_code}")
