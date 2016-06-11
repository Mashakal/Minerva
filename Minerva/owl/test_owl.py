import unittest
from owl import stackexchangeparameters as separams, stackexchangequery as sequery

class Test_Owl(unittest.TestCase):
    # Class StackExchangeQuery.
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

    
    # Class Parameters.
    def test_constructionWithoutParameters(self):
        instance = separams.Parameters()
        self.assertFalse(instance.getAsQueryString()), "instance.parameters should be Falsy, but it is not."
        self.assertEqual(instance.getSize(), 0), "instance.parameters should have 0 keys."
    
    def test_constructionWithParameters(self):
        params = {"tagged":"ptvs", "pagesize":"1"}
        instance = separams.Parameters(params)
        self.assertEqual(instance.getSize(), 2), "instance.parameters should have 2 keys."

    def test_addParameter(self):
        params = {"tagged":"ptvs", "pagesize":"1"}
        instance = separams.Parameters(params)
        instance.addParameter("site", "stackoverflow")
        self.assertEqual(instance.getSize(), 3), "instance.parameters should have 3 keys."
        self.assertDictContainsSubset({"site": "stackoverflow"}, instance.get())

    def test_tagCount(self):
        params = {"tagged":"ptvs;ironpython"}
        instance = separams.Parameters(params)
        self.assertEqual(instance._tagCount, 2)
        instance.addTag("debug")
        self.assertEqual(instance._tagCount, 3)
        instance.removeTag('ptvs')
        self.assertEqual(2, instance._tagCount)
        instance.removeTag('debug')
        instance.removeTag('ironpython')
        self.assertEqual(0, instance._tagCount)
    
    def test_getParameter(self):
        params = {"tagged":"ptvs"}
        instance = separams.Parameters(params)
        self.assertEquals("ptvs", instance.getParameter("tagged"))
        self.assertFalse(instance.getParameter("site"))


    def test_addTag(self):
        params = {"tagged":"ptvs"}
        instance = separams.Parameters(params)
        instance.addTag("ironpython")
        self.assertNotIn("django", instance.getParameter("tagged"))
        self.assertIn("ironpython", instance.getParameter("tagged"))
        instance.addTag("django")
        self.assertIn("django", instance.getParameter("tagged"))
        instance.addTag("fourth")
        instance.addTag("fifth")
        self.assertFalse(instance.addTag("sixth")) # separams.MAX_TAGS currently set to 5

    def test_getAsQueryString(self):
        instance = separams.Parameters()
        self.assertFalse(bool(instance.getAsQueryString())) # Query string should be the empty string, ''.
        instance.addParameter("tagged", "ptvs")
        self.assertEqual("tagged=ptvs", instance.getAsQueryString())
        instance.addTag("python")
        self.assertEqual(instance.getAsQueryString(), 'tagged=ptvs;python')
        instance.addParameter("site", "stackoverflow")
        self.assertRegex(instance.getAsQueryString(), '(tagged=ptvs;python&site=stackoverflow)|(site=stackoverflow&tagged=ptvs;python)')

    def test_removeTag(self):
        params = {'tagged':'ptvs;python;debug'}
        instance = separams.Parameters(params)
        instance.removeTag('ptvs')
        self.assertEqual(instance.getParameter('tagged'), 'python;debug')
        instance.removeTag('python')
        instance.removeTag('debug')
        self.assertFalse(instance.removeTag('noMoreTagsToRemove'))
        self.assertFalse(instance.getParameter('tagged'))
        self.assertEqual(instance._tagCount, 0)
        print(instance.get())
        self.assertEqual(instance.getSize(), 0)
        


if __name__ == '__main__':
    unittest.main()
