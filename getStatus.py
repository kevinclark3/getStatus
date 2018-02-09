import os
import datetime
from flask import Flask
import requests
import time

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
# Go get the status for each repository in turn

@app.route('/status')
def getStatus():

  # Repository information
  repo1    = 'Bitbucket'
  repo1URL = 'https://status.bitbucket.org'
  repo2    = 'GitHub'
  repo2URL = 'https://status.github.com/messages'
  repo3    = 'GitLab'
  repo3URL = 'https://status.gitlab.com'

  # Set up the proxy
  http_proxy='http://www-proxy.us.oracle.com'
  https_proxy='http://www-proxy.us.oracle.com'
  proxyDict = {
                     "http" : http_proxy,
                     "https" : https_proxy
              }

  output = '<H1>Git Repository Status</H1>'

  # Bitbucket Status
  #r = requests.get(repo1URL, timeout=5, proxies=proxyDict)
  r1 = requests.get(repo1URL, timeout=5)
  found = 0 
  textList = r1.text.split("\n")
  # We are looking for a single instance of pattern
  pattern = 'All Systems Operational'
  for item in textList:
    if pattern in item:
      found = 1
      break
  output += outputResults(repo1, repo1URL, r1.status_code, found)

  # GitHub Status 
  #r = requests.get(repo2URL, timeout=5, proxies=proxyDict)
  r2 = requests.get(repo2URL, timeout=5)
  now = datetime.datetime.now()
  found = 0
  textList = r2.text.split("\n")
  # GitHub has two different success messages to look for...
  pattern1 = 'All systems reporting at 100'
  pattern2 = 'Everything operating normally.'
  currentDate = now.strftime("%Y-%m-%dT")
  for item in textList:
    if ((currentDate in item) and ((pattern1 in item) or (pattern2 in item))):
      found = 1
      break
  output += outputResults(repo2, repo2URL, r2.status_code, found)
 
  # GitLab Status 
  #r = requests.get(repo3URL, timeout=5, proxies=proxyDict)
  r3 = requests.get(repo3URL, timeout=5)
  found = 0
  textList = r3.text.split("\n")
  # We are looking for four counts of both patterns
  pattern1 = 'label label-success'
  pattern2 = 'OK'
  count = 0
  expectCount = 4
  for item in textList:
    if (pattern1 in item) and (pattern2 in item):       
      count = count + 1
    if count == expectCount:
      found = 1
      break
  output += outputResults(repo3, repo3URL, r3.status_code, found)

  return output

# ----------------------------------------------------------------
# Main

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

