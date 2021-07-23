#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Provides the Transkribus_Web object to communicate with
    the Transkribus REST-API. """

import requests
import json
from lxml import objectify, etree
from pprint import pprint

class Transkribus_Web():
    """ The Transkribus_Web class implements the communication with the 
        Transkribus REST API. 
        
        All available endpoints: https://transkribus.eu/TrpServer/Swadl/wadl.html
        Documentation: https://readcoop.eu/transkribus/docu/rest-api/
        Official TranskribusPyClient: https://github.com/Transkribus/TranskribusPyClient """
    
    def __init__(self, api_base_url="https://transkribus.eu/TrpServer/rest/"):
        self.cols = {}
        self.api_base_url = api_base_url
        self.session_id = False
        self.cache = False
    
    # Internal helper functions:
    
    def _url(self, endpoint):
        """ Helper function that returns a full URL for requests to the REST API, 
            i.e. the API base URL + the relative path of the endpoint. """
        
        return self.api_base_url + endpoint
    
    # Core functionality: login, logout, send GET requests
    
    def login(self, username, password):
        """ Performs a login and stores the SESSIONID in the "session_id" variable
            of this class. """
        
        credentials = {'user': username,
                       'pw': password}
        response = requests.post(self._url("auth/login"), data=credentials)
        if response:
            r = objectify.fromstring(response.content)
            print(f"TRANSKRIBUS: User {r.firstname} {r.lastname} ({r.userId}) logged in successfully.")
            self.session_id = str(r.sessionId)
            return str(r.sessionId)
        else:
            print("TRANSKRIBUS: Login failed. HTTP status:", response.status_code)
            return False
    
    def logout(self):
        """ Logs out and sets the "session_id" variable to False. """
        
        cookies = dict(JSESSIONID=self.session_id)
        response = requests.post(self._url("auth/logout"), cookies=cookies)
        if response:
            self.session_id = False
            print("TRANSKRIBUS: Logged out successfully.")
            return True
        else:
            print("TRANSKRIBUS: Logout failed. HTTP status:", response.status_code, response.content)
            return False

    def verify(self, username, password):
        """ Logs in and logs out to check whether the credentials
            are valid on the Transkribus server. 
            Returns True or False. """
        
        session_id = self.login(username, password)
        if session_id:
            self.logout(session_id)
            return True
        else: 
            return False        
        
    def request_endpoint(self, endpoint):
        """ Sends a GET request to a Transkribus API endpoint, the 
            "endpoint" argument being a relative path to the REST API endpoint

            Cf. the list of available endpoints:
            https://transkribus.eu/TrpServer/Swadl/wadl.html

            Depending on the content type (JSON or XML), 
            the function tries to decode the raw content of the response.
            It returns a json object or an "objectify" object (lxml). If
            the conversion fails the raw content is returned. """

        cookies = dict(JSESSIONID=self.session_id)
        
        response = requests.get(self._url(endpoint), cookies=cookies)

        if response:
            try:
                json = response.json()
                return json
            except:
                try:
                    xml = objectify.fromstring(response.content)
                    return xml
                except:
                    return response.content  # fallback option if the server returns just text
        else:
            print(f'TRANSKRIBUS: ERROR when requesting "{endpoint}". HTTP status:', response.status_code)
            return False
    
    # Convenience functions to query certain endpoints: 
    
    def get_collections(self):
        """ Get the metadata of the owner's collections. 
            Returns a dict if successful or False if not. """
        
        endpoint = "collections/list"
        collections = self.request_endpoint(endpoint)
        return collections if collections else False
    
    def get_documents_in_collection(self, colId):
        """ Get the metadata of a collection. 
            Returns a dict if successful or False if not.
            
            colId -- collection ID in Transkribus (int) """
        
        endpoint = f"collections/{colId}/list"
        documents = self.request_endpoint(endpoint)
        return documents if documents else False

    def get_pages_in_document(self, colId, docId):
        """ Get the basic metadata of the pages in a document. 
            Returns a dict if successful or False if not.
           
            colId -- collection ID in Transkribus (int) 
            docId -- document ID in Transkribus (int) 
            pageNr -- page ID in Transkribus (int) """
        
        endpoint = f"collections/{colId}/{docId}/pages"
        pages = self.request_endpoint(endpoint)
        return pages if pages else False
        
    def get_page_xml(self, colId, docId, pageNr):
        """ Get the XML content of a page. 
            Returns an "objectify" object (lxml) or False if not successful. 
            
            colId -- collection ID in Transkribus (int) 
            docId -- document ID in Transkribus (int) 
            pageNr -- page ID in Transkribus (int) 
            
            The returned object X has two attributes: X.Metadata and X.Page. 
            X.Page is empty if there are no transcripts yet. 
            If there exists a transcription X.Page has further attributes
            (i and j are list indices counting from 0):
            
            X.Page.Metadata
                  .ReadingOrder
                  .values()   -> list containing imgFileName, width (px), height (px)
                  .TextRegion[i].Coords.attrib['points']               -> coordinates of the whole text region (1)
                                .TextEquiv.Unicode                     -> utf-8 string of the transcription of the whole text region
                                .TextLine[j].Coords.attrib['points']   -> coordinates of this line (1) (2)
                                            .BaseLine.attrib['points'] -> coordinates of this baseline (2)
                                            .TextEquiv.Unicode         -> utf-8 string of the transcription
            
            (1) Instead of .attrib['points'] you can say .values()[0].
            (2) The line is a polygon around the line of text, the BaseLine is a line below the text.
            
            You can check for the existence of attributes: if hasattr(X.Page, "TextRegion")…
            Get a list of existing attributes: X.Page.__dict__

            """
        
        endpoint = f"collections/{colId}/{docId}/{pageNr}/text"
        page_xml = self.request_endpoint(endpoint)
        return page_xml if page_xml is not None else False
        
    def upload_page_xml(self, colId, docId, pageNr, new_status, page_xml):
        """ Upload page XML data to the Transkribus server using a POST request. 
            Returns True or False.
        
            colId -- collection ID in Transkribus (int) 
            docId -- document ID in Transkribus (int) 
            pageNr -- page ID in Transkribus (int) 
            new_status -- new_status of the page. Possible values are NEW, IN_PROGRESS, DONE, FINAL, GT. 
            
            tsId = transcript ID of the last version of this transcription (int).
            After the upload Transkribus will generate a new transcription Id and save 
            the old one as the 'parentTsId' of the new transcription. """

        # Get the transcript ID of the latest transcription:
        current_transcript = self.request_endpoint(f"collections/{colId}/{docId}/{pageNr}/curr")
        if current_transcript:
            tsId = current_transcript['tsId']
        else:
            return False
        
        headers = {'Content-Type': 'text/xml'} 
        cookies = dict(JSESSIONID=self.session_id)
        params = {'status': new_status,
                  'parent': tsId,
                  'overwrite': 'false'}
        # convert the page_xml object to a pretty utf-8 string:
        data = etree.tostring(page_xml, pretty_print=True, xml_declaration=True).decode("utf-8")

        response = requests.post(self._url(f"collections/{colId}/{docId}/{pageNr}/text"), 
                                 headers=headers,
                                 params=params,
                                 cookies=cookies, 
                                 data=data)

        if response:
            print(f"Uploaded page {colId}/{docId}/{pageNr} successfully: {response.status_code}")
            print(response.content.decode(encoding="utf-8"))
            return True
        else:
            print(f"ERROR while uploading {colId}/{docId}/{pageNr}: {response.status_code}")
            print(response.content.decode(encoding="utf-8"))
            return False

    def update_page_status(self, colId, docId, pageNr, new_status):
        """ Update the status of the transcript with the transcript ID tsId with new_status.
            Returns True or False. 
            
            colId -- collection ID in Transkribus (int) 
            docId -- document ID in Transkribus (int) 
            pageNr -- page ID in Transkribus (int) 
            new_status -- new_status of the page. Possible values are NEW, IN_PROGRESS, DONE, FINAL, GT. """

        # Get the transcript ID of the latest transcription:
        current_transcript = self.request_endpoint(f"collections/{colId}/{docId}/{pageNr}/curr")
        if current_transcript:
            tsId = current_transcript['tsId']
        else:
            return False
        
        cookies = dict(JSESSIONID=self.session_id)
        params = {'status': new_status}
        
        endpoint = f"collections/{colId}/{docId}/{pageNr}/{tsId}"
        response = requests.post(self._url(endpoint),
                                 params=params,
                                 cookies=cookies)
        
        if response:
            print(f"TRANSKRIBUS: Updated status of page {pageNr} to {new_status} in collection {colId}, document {docId}.")
            print(response.content.decode(encoding="utf-8"))
            return True
        else:
            print(f"TRANSKRIBUS: ERROR: Could not update status of page {pageNr} to {new_status} in collection {colId}, document {docId}.")
            print(response.content.decode(encoding="utf-8"))
            return False