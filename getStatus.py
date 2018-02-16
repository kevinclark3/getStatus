import os
import datetime
from flask import Flask
from flask import Response
from flask import json
import requests

app = Flask(__name__)

# ----------------------------------------------------------------
@app.route('/')
def index():
    return "Hello World!"

# ----------------------------------------------------------------
# Sample way to get the wercker-cli to work behind Oracle's VPN
@app.route('/test')
def test():

    http_proxy='http://www-proxy.us.oracle.com'
    https_proxy='http://www-proxy.us.oracle.com'
    proxyDict = {
                     "http" : http_proxy,
                     "https" : https_proxy
                }
    r = requests.get('https://stackoverflow.com', proxies=proxyDict)
    return r.text;

# ----------------------------------------------------------------
# outputResults:
# Helper function to pretty-print the results of the pings

def outputResults(name, uri, c, result):
  t = ''
  t += '<H3>' + name + '</H3>'
  t += '<A HREF=\"' + uri + '\">' + uri + '</A><BR>'
  t += 'Response Status Code: ' + str(c) + '<BR>'
  if result == 1:
    t += 'Current Status:  <b><font color=green>OPERATIONAL</font></b><BR>'
  else:
    t += 'Current Status:  <b><font color=red>Repository may be down or has issues...</font></b><BR>'
  t += '================================================'
  return t;


# ----------------------------------------------------------------
# pushCachet
# Helper function to automatically push repo status to Catchet

def pushCachet(id, status):
  
  # Cachet Status Codes
  # 1 - Operational
  # 2 - Performance issues
  # 3 - Partial Outage
  # 4 - Major outage

  cachetURL = "http://10.159.144.8"
  fullURL   = cachetURL + "/api/v1/components/" + id

  token = "WWOJ6kLnh7KnvAFr7atn"
  headers = {
    'Content-Type':'application/json', 
    'X-Cachet-Token':token
  } 
  payload = {"status":str(status)}

  print(fullURL)
  print(payload)
  print(headers)
  response = requests.put(fullURL, data=json.dumps(payload), headers=headers)

  return response.text;

# ----------------------------------------------------------------
# Parse Bitbucket

def parseBitbucket(text):
  pattern = 'All Systems Operational'
  status = 4

  textList = text.split("\n")
  # We are looking for a single instance of pattern
  for item in textList:
    if pattern in item:
      status = 1
      break

  return status;

# ----------------------------------------------------------------
# Parse GitHub

def parseGitHub(text):
  pattern1 = 'All systems reporting at 100'
  pattern2 = 'Everything operating normally.'
  status = 4

  now = datetime.datetime.now()
  textList = text.split("\n")
  currentDate = now.strftime("%Y-%m-%dT")
  for item in textList:
    if ((currentDate in item) and ((pattern1 in item) or (pattern2 in item))):
      status = 1
      break

  return status;

# ----------------------------------------------------------------
# Parse GitLab

def parseGitLab(text):
  pattern1 = 'label label-success'
  pattern2 = 'OK'
  count = 0
  expectCount = 4
  status = 4

  textList = text.split("\n")
  for item in textList:
    if (pattern1 in item) and (pattern2 in item):
      count = count + 1
      status = 3
    if count == expectCount:
      status = 1
      break

  return status;

# ----------------------------------------------------------------
# Go get the status for each repository in turn

@app.route('/status')
def getStatus():

  # Set up the proxy
  http_proxy='http://www-proxy-hqdc.us.oracle.com:80'
  https_proxy=http_proxy
  proxyDict = {
                     "http" : http_proxy,
                     "https" : https_proxy
              }

  output = '<H1>Git Repository Status</H1>'
 
  #################################################### 
  # Scan the properties file
  propFile = "/scratch/kdclark/work/getStatus/properties.txt"
  
  with open(propFile) as pf:
    line = pf.readline()
    while line:
      # Strip out the newline
      line,junk = line.split('\n')
      repoName,repoURL,repoID = line.split("::")

      #r = requests.get(repoURL, timeout=5, proxies=proxyDict)
      r  = requests.get(repoURL, timeout=5)

      # Parse the requests
      if repoName == "Bitbucket":
        status = parseBitbucket(r.text)
      if repoName == "GitHub":
        status = parseGitHub(r.text)
      if repoName == "GitLab":
        status = parseGitLab(r.text)

      # Output results
      #output += outputResults(repoName, repoURL, r.status_code, status)
      
      output += repoName + ": " + str(status) + "<BR>"

      # Push results to Cachet
      returnCode = pushCachet(repoID, status)
    
      output += "Result of pushing to Cachet: " + str(returnCode) + "<BR>"
 
      line = pf.readline()
      # End while loop
  #####################################################

  return output

# ----------------------------------------------------------------
# Main

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

