import unittest
from stackexchangequery import StackExchangeQuery

class Test_StackExchangeQuery(unittest.TestCase):
    def test_classVariables(self):
        # QUESTION:  is there a more pythonic way than to use class variables?
        assert(sequery.Query.BASE_URL == 'https://api.stackexchange.com'), "Base URL mismatch."
        assert(sequery.Query.VERSION == '2.2'), "Version mismatch, testing against 2.2."

    def test_instanceVariables(self):
        instance = sequery.Query('stackoverflow')
        self.assertEqual(instance.startURL, 'https://api.stackexchange.com/2.2')

    def test_setQueryType(self):
        instance = sequery.Query('stackoverflow')
        self.assertEqual(instance._queryType, 'questions')
        self.assertRaises(ValueError, instance.setQueryType, 'unimplemented')

    def test_getQueryType(self):
        instance = sequery.Query('stackoverflow')
        self.assertEqual(instance.getQueryType(), 'questions')

    def test_setSite(self):
        instance = sequery.Query('stackoverflow')
        self.assertEqual(instance.getSite(), 'stackoverflow')
        self.assertRaises(ValueError, sequery.Query, 'notAValidSite')

    def test_buildUrl(self):
        instance = sequery.Query('stackoverflow')
        self.assertEqual('https://api.stackexchange.com/2.2/questions', instance.buildUrl())

    
if __name__ == '__main__':
    unittest.main()
