from getStatus import app
import unittest

class getStatusTestCase(unittest.TestCase):

  def test_index(self):
    tester = app.test_client(self)
    response = tester.get('/status')
    text = response.data

    pattern1  = '200'
    pattern2  = 'OPERATIONAL'
    codeCount = text.count(pattern1)
    opCount   = text.count(pattern2)
    print('----------------------------------------------------------------------')
    print('Test Results:')
    print('Expecting 3 instances of status code 200.  Found: ' + str(codeCount))
    print('Expecting 3 instances of OPERATIONAL.      Found: ' + str(opCount))
    print('----------------------------------------------------------------------')
  
    self.assertEqual(codeCount, 3)
    self.assertEqual(opCount, 3)

  # ----------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
