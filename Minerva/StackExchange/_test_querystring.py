import unittest
from querystring import StackExchangeQueryString

class Test_StackExchangeQueryString(unittest.TestCase):
    # NOTE:  'site':'stackoverflow' is a default key/value in dict separams.StackExchangeQueryString.parameters
    def test_constructionWithoutStackExchangeQueryString(self):
        instance = StackExchangeQueryString()
        self.assertEqual(instance.getSize(), 1), "instance.parameters should have default 'site' key."
    
    def test_constructionWithStackExchangeQueryString(self):
        params = {"tagged":"ptvs", "pagesize":"1"}
        instance = StackExchangeQueryString(params)
        self.assertEqual(instance.getSize(), 3), "instance.parameters should have 3 keys."

    def test_addPair(self):
        params = {"tagged":"ptvs", "pagesize":"1"}
        instance = StackExchangeQueryString(params)
        self.assertEqual(3, instance.getSize())
        instance.addPair("site", "meta")  # 'site' explicitly set here, parameter count is still 3...
        self.assertEqual(instance.getSize(), 3), "instance.parameters should have 3 keys."  # ...as proven here.
        self.assertDictContainsSubset({"site": "meta"}, instance.parameters)

    def test_tagCount(self):
        params = {"tagged":"ptvs;ironpython"}
        instance = StackExchangeQueryString(params)
        self.assertEqual(instance._tagCount, 2)
        instance.addTag("debug")
        self.assertEqual(instance._tagCount, 3)
        instance.removeTag('ptvs')
        self.assertEqual(2, instance._tagCount)
        instance.removeTag('debug')
        instance.removeTag('ironpython')
        self.assertEqual(0, instance._tagCount)
    
    def test_retrieve(self):
        params = {"tagged":"ptvs"}
        instance = StackExchangeQueryString(params)
        self.assertEquals("ptvs", instance.retrieve("tagged"))
        self.assertEqual('stackoverflow', instance.retrieve("site"))

    def test_addTag(self):
        params = {"tagged":"ptvs"}
        instance = StackExchangeQueryString(params)
        instance.addTag("ironpython")
        self.assertNotIn("django", instance.retrieve("tagged"))
        self.assertIn("ironpython", instance.retrieve("tagged"))
        instance.addTag("django")
        self.assertIn("django", instance.retrieve("tagged"))
        instance.addTag("fourth")
        instance.addTag("fifth")
        self.assertFalse(instance.addTag("sixth")) # separams.MAX_TAGS currently set to 5

    def test_getFullString(self):
        instance = StackExchangeQueryString()
        instance.addPair("tagged", "ptvs")
        instance.addTag("python")
        self.assertRegex(instance.getFullString(), '(tagged=ptvs;python&site=stackoverflow)|(site=stackoverflow&tagged=ptvs;python)')

    def test_removeTag(self):
        params = {'tagged':'ptvs;python;debug'}
        instance = StackExchangeQueryString(params)
        instance.removeTag('ptvs')
        self.assertEqual(instance.retrieve('tagged'), 'python;debug')
        instance.removeTag('python')
        instance.removeTag('debug')
        self.assertFalse(instance.removeTag('noMoreTagsToRemove'))
        self.assertFalse(instance.retrieve('tagged'))
        self.assertEqual(instance._tagCount, 0)
        self.assertEqual(instance.getSize(), 1)
        


if __name__ == '__main__':
    unittest.main()
