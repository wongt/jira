#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import datetime
import iso8601
import json
import requests
import sys

from requests.auth import HTTPBasicAuth

reload(sys)
sys.setdefaultencoding('utf-8')

MAX_RESULTS=250
# customfield_10201 = Severity
# customfield_11400 = Priority
# customfield_11605 = Department
# customfield_10004 = Story Points

FIELDS="fields=key,id,assignee,issuetype,summary,reporter,status,resolution,created,updated,customfield_10201,customfield_11605,resolutiondate,project,labels,customfield_10004"

DOMAIN=""
JIRA_URL="https://"+ DOMAIN + ".atlassian.net/rest/api/2"
JQL_QUERY="/search?jql="

LOGIN=""
PASSWORD=""

def getJiraIssues(jqlQuery, startAt, maxResults, fields):

	url = JIRA_URL + jqlQuery + "&startAt=" + str(startAt) + "&maxResults=" + str(maxResults) + "&fields=" + fields
	return requests.get(url, auth=HTTPBasicAuth(LOGIN, PASSWORD))

def writeDictToCSV(csvFile, listDictData):

	keys = listDictData[0].keys()

	with open(csvFile, 'wb') as outputFile:
		dict_writer = csv.DictWriter(outputFile, keys)
		dict_writer.writeheader()
		dict_writer.writerows(listDictData)

def extractField(issue):

	a = {}
	a['issue_key'] = issue['key']
	a['issue_type'] = issue['fields']['issuetype']['name']
	a['issue_id'] = issue['id']
	a['summary'] = issue['fields']['summary']

	if 'customfield_10004' in issue['fields']:
		a['story_points'] = issue['fields']['customfield_10004']
	else:
		a['story_points'] = None

	if issue['fields']['assignee'] is None:
		a['assignee'] = None
	else:
		a['assignee'] = issue['fields']['assignee']['displayName']

	a['reporter'] = issue['fields']['reporter']['displayName']
	a['status'] = issue['fields']['status']['name']

	if issue['fields']['resolution'] is None:
		a['resolution'] = None
	else:
		a['resolution'] = issue['fields']['resolution']['name']
	
	if issue['fields']['resolutiondate'] is None:
		a['resolutiondate'] = ""
	else:
		a['resolutiondate'] = iso8601.parse_date(issue['fields']['resolutiondate']).replace(tzinfo=None)

	a['created'] = iso8601.parse_date(issue['fields']['created']).replace(tzinfo=None)
	a['updated'] = iso8601.parse_date(issue['fields']['updated']).replace(tzinfo=None)
	
	if issue['fields']['customfield_10201'] is None:
		a['severity'] = None
	else:
		a['severity'] = issue['fields']['customfield_10201']['value']

	a['labels'] = ','.join(map(str, issue['fields']['labels']))
	a['project_key'] = issue['fields']['project']['key']
	a['project_name'] = issue['fields']['project']['name']

	if issue['fields']['customfield_11605'] is None:
		a['department'] = None
	else:
		a['department'] = issue['fields']['customfield_11605']['value']

	#Get timestamp when issue transitioned to In Progress
	if a['resolutiondate'] != "" and a['status'] == "Done":
		a['startdate'] = getTimestampInProgress(issue)
	else:
		a['startdate'] = None

	return a

def getIssueHistories(issueKey):
	"""
	"""
	url = JIRA_URL + "/issue/" + issueKey +"?expand=changelog&fields=created"

 	return requests.get(url, auth=HTTPBasicAuth(LOGIN, PASSWORD))

def getTimestampInProgress(issue):
	"""
	"""

	timeReference = datetime.datetime.now()
	inProgressTimeStamp = timeReference

	response = getIssueHistories(issue['key'])
	data = response.json()
	histories = data['changelog']['histories']

	for history in histories:
		for item in history['items']:
			if item['field'] == "status" and item['toString'] == "In Progress" and item['fromString'] != "Done" and item['fromString'] != "Fixed" and item['fromString'] != "To Be Checked":
				timestamp = iso8601.parse_date(history['created']).replace(tzinfo=None)

				if timestamp < inProgressTimeStamp:
					inProgressTimeStamp = timestamp

	if timeReference == inProgressTimeStamp:
		inProgressTimeStamp = None
	
	return inProgressTimeStamp


def main():

	jiraIssues = []

	## Retrieve 1 result, to get Total amount of Issues
	response = getJiraIssues(JQL_QUERY, 0, 1, FIELDS)
	data = response.json()

	totalIssues = int(data['total'])
	#totalIssues = 10
	startAt = int(data['startAt'])
	
	while startAt <= totalIssues:
		response = getJiraIssues(JQL_QUERY, startAt, MAX_RESULTS, FIELDS)
		data = response.json()

		for issue in data['issues']:
			jiraIssues.append(extractField(issue))

		#Increment to next page
		startAt = startAt + MAX_RESULTS

	writeDictToCSV('jiraIssues.csv', jiraIssues)

	

if __name__ == '__main__':

	main()
