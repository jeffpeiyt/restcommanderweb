#!/usr/bin/env python
# --------------------------------------
# Author : yangli8@ebay.com
# Date : 01/11/2014
# Description : 
# This script is a sample basic workflow to check the health status for a list of servers, 
# returns the aggregated health report. For those unhealthy servers, send server restart command
# to bring them back to normal status. 
# This script can be easily configured as a crontab job to be executed regularly.
# --------------------------------------

import sys
import json
import urllib
import urllib2
import time

if sys.version_info < (3, 0):
	from urllib2 import urlopen
else:
	from urllib.request import urlopen

def main():
	#list all the servers need to send request to
	hosts = ["www.restcommander.com","www.yangli907.com","www.jeffpei.com"]

	superman_server = "http://localhost:9000/"
	complete_uri = superman_server+"commands/genUpdateSendCommandWithReplaceVarMapNodeSpecificAdhocJson" #URL to the REST Superman API
	serverHealthJson = getServerHealthStatus(complete_uri, hosts) # Call REST Superman API to get server health status json response
	unhealthyNodeList = getUnhealthyNodeList(serverHealthJson) # Parse the aggregated json response to get unhealthy node list 
	restartBadNodeList(unhealthyNodeList,superman_server) # Call REST Superman API to restart unhealthy servers

def getServerHealthStatus(server, targets):
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	data={}
	data["targetNodes"]=targets #define the target group
	
	#the following attributes defined the agent command parameters
	data["useNewAgentCommand"]="true"
	data["newAgentCommandLine"]="GET_VALIDATE_INTERNALS GET http 80 /validateInternals.html 0 0 5000 SUPERMAN_GLOBAL"
	data["newAgentCommandContentTemplate"]="$AM_FULL_CONTENT"

	#The following attribtes defined the response aggregation preference
	data["willAggregateResponse"]="true" #to aggregate the raw response
	data["aggregationType"]="PATTERN_SERVER_HEALTH" #parsing regex Content-type
	data["useNewAggregation"]="true"
	raw_regex=".*<td>Server-Is-Healthy</td>\s*<td>(.*?)</td>[\s\S]*"
	data["newAggregationExpression"]=urllib.quote_plus(raw_regex)
	print "The json body for request is: \n %s" % json.dumps(data, sort_keys=True, indent=3, separators=(',', ':'))
	#Define the request post body and headers
	req = urllib2.Request(server, json.dumps(data), headers)
	response = urllib2.urlopen(req)
	#parse the server response to json format
	responseJson = json.load(response)
	return responseJson


def getUnhealthyNodeList(response):
#
#Parse the aggregated server json response, 
#put all nodes with unhealthy status to a list
#
	print "The aggregated json response returned from Superman is \n %s" % json.dumps(response, sort_keys=True, indent=3, separators=(',', ':'))
	healthyNodeList=[]
	unhealthyNodeList=[]
	try:
		for group in response["aggregationValueToNodesList"]:
			hosts = group["nodeList"]
			status = group["value"]
			if status == "False":
				for host in hosts:
					unhealthyNodeList.append(host)
			elif status == "True":
				for host in hosts:
					healthyNodeList.append(host)
		print "The healthy nodes are: %s" % healthyNodeList
		print "The unhealthy nodes are: %s" % unhealthyNodeList
		return unhealthyNodeList
	except KeyError:
		print("ERROR: unable to parse the response")
		sys.exit(1)

def restartBadNodeList(hosts,servers):
#This function is a sample to demostrate using Superman to send restart command to unhealthy servers
#The post command is for demo purpose only, no actual request is posted for server restart
	print "*******starting restart server********"

	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	data={}
	data["targetNodes"]=hosts #define the target group
	
	data["useNewAgentCommand"]="true"
	data["newAgentCommandLine"]="POST_RESTART_SERVER POST http 80 /restart 0 0 5000 SUPERMAN_GLOBAL"
	data["newAgentCommandContentTemplate"]="$AM_FULL_CONTENT"

	req = urllib2.Request(servers, json.dumps(data), headers)
	#response = urllib2.urlopen(req)
	#responseJson = json.load(response)
	time.sleep(3)
	print "*******finished restart server********"


if __name__ == "__main__":
	main()