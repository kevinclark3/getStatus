import sys, os, datetime, requests
from flask import Flask
from flask import Response
from flask import json

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

def pushCachet(id, name, status, url, token):
  
  # Cachet Status Codes
  # 1 - Operational
  # 2 - Performance issues
  # 3 - Partial Outage
  # 4 - Major outage

  cachetURL = "http://" + url + "/api/v1/components/" + id
  headers = {
    'Content-Type':'application/json', 
    'X-Cachet-Token':token
  } 
  payload = {"name":name,"status":str(status)}

  #print(cachetURL)
  print(payload)
  #print(headers)
  response = requests.put(cachetURL, data=json.dumps(payload), headers=headers)

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
  # Environment variables
  propFile = "properties.txt"
  line = 1

  # Get the path to the properties file
  propFile = os.path.dirname(os.path.abspath(sys.argv[0])) + "/" + propFile
  if not os.path.exists(propFile):
    raise IOException("Can't find file:  " + propFile)

  # Scan the properties file
  with open(propFile) as pf:
    line = pf.readline()
    while line:
      # Strip out the newline
      line,junk = line.split('\n')

      # Ignore comments
      if "#" in line:
        line = line
 
      # Capture any environmental variables
      elif "CACHET_URL" in line:
        junk,cachetURL = line.split("::")
        print("Setting URL to " + cachetURL)
      elif "CACHET_TOKEN" in line: 
        junk,cachetToken = line.split("::")
        print("Setting token to " + cachetToken)

      # Send request and get repository status
      else:
        repoName,repoURL,repoID = line.split("::")
        #r = requests.get(repoURL, timeout=5, proxies=proxyDict)
        r  = requests.get(repoURL, timeout=5)

        # Call a function to parse the information returned from the 
        # repoName status page.
        # 
        # IN FUTURE:  If new repos are added, just create a new function
        # called:  parseXX -- where XX is the name of the repo.
        cmd = "parse" + repoName + "(r.text)"
        status = eval(cmd)

        # Output results
        #output += outputResults(repoName, repoURL, r.status_code, status)
        output += "Updating " + repoName + " to status: " + str(status) + "<BR>"

        # Push results to Cachet
        resp = pushCachet(repoID, repoName, status, cachetURL, cachetToken)
        output += "Cachet: " + str(resp) + "<BR>"

      line = pf.readline() 
      # End while loop
  #####################################################

  return output

# ----------------------------------------------------------------
# Main

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

