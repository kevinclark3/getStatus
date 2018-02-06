import unittest
import requests
import datetime

class GetStatus(unittest.TestCase):

  # ----------------------------------------------------------------
  # outputResults:
  # Helper function to print out the results and return pass/fail

  def outputResults(self, name, uri, c, result):
    print('\n================================================')
    print(name + ':  ' + uri)
    print('================================================')
    print('Response Status Code: ' + str(c))
    if result == 1:
      print(name + ' Status:  OPERATIONAL')
    else:
      print(name + ' Status:  Repository may be down or has issues...')

    # Check status code
    self.assertEqual(c, 200)
    # Is the repository up?
    self.assertEqual(result, 1)


  # ----------------------------------------------------------------
  # test_Bitbucket:
  # Check if Bitbucket is operational

  def test_Bitbucket(self):
    repo = 'Bitbucket'
    repoURL = 'https://status.bitbucket.org'
    r = requests.get(repoURL, timeout=5)
   
    found = 0 
    textList = r.text.split("\n")
    # We are looking for a single instance of pattern
    pattern = 'All Systems Operational'
    for item in textList:
      if pattern in item:
        found = 1
        break
    self.outputResults(repo, repoURL, r.status_code, found)
   
  # ----------------------------------------------------------------
  # test_GitLab
  # Check if GitLab is operational

  def test_GitLab(self):
    repo = 'GitLab'
    repoURL = 'https://status.gitlab.com'
    r = requests.get(repoURL, timeout=5)

    found = 0
    textList = r.text.split("\n")
    # We are looking for four counts of both patterns
    pattern1 = 'label label-success'
    pattern2 = 'OK'
    count = 0
    expectCount = 4
    for item in textList:
      if pattern1 in item and pattern2 in item:       
        count = count + 1
      if count == expectCount:
        found = 1
        break
    self.outputResults(repo, repoURL, r.status_code, found)
    
  # ----------------------------------------------------------------
  # testGitHub
  # Check if GitHub is operational

  def test_GitHub(self):
    repo = 'GitHub'
    repoURL = 'https://status.github.com/messages'
    r = requests.get(repoURL, timeout=5)
    now = datetime.datetime.now()

    found = 0
    textList = r.text.split("\n")
    # GitHub has two success messages we need to look for...
    pattern1 = 'All systems reporting at 100'
    pattern2 = 'Everything operating normally.'
    currentDate = now.strftime("%Y-%m-%dT")
    for item in textList:
      if currentDate in item and pattern1 in item or pattern2 in item:
        # print('Found it!\n' + item)
        found = 1
        break
    self.outputResults(repo, repoURL, r.status_code, found)

  # ----------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
