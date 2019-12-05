#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests
import sys

from requests.auth import HTTPBasicAuth


DOMAIN="ssense"
CONFLUENCE_URL="https://" + DOMAIN + ".atlassian.net/wiki/rest/api/content"

CQL_EXPAND="history"

CQL_CUSTOM='space+%3D+"IT"+and+label+%3D+"incident-response"'
CQL_QUERY="/search?cql=" + CQL_CUSTOM 
CQL_PAGE_LIMIT=500

LOGIN=""
PASSWORD=""


def getConfluencePages(cqlQuery, cqlExpand):

    url = CONFLUENCE_URL + cqlQuery + "&expand=" + cqlExpand + "&limit=" + str(CQL_PAGE_LIMIT) 
    print url

    return requests.get(url, auth=HTTPBasicAuth(LOGIN, PASSWORD))

def main():
    confluencePages = []

    response =  getConfluencePages(CQL_QUERY, CQL_EXPAND)

    payload = response.json()

    print str(payload['size'])

if __name__ == '__main__':

    main()
