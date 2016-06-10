import unittest
import core

class Test_StackExchangeQuery(unittest.TestCase):
    def test_ClassVariables(self):
        assert(core.StackExchangeQuery.BASE_URL == 'https://api.stackexchange.com'), "Base URL mismatch."
        assert(core.StackExchangeQuery.VERSION == '2.2'), "Version mismatch, testing against 2.2."

    def test_InstanceVariables(self):
        instance = core.StackExchangeQuery()
        self.assertEqual(instance.startURL, 'https://api.stackexchange.com/2.2')
        
    def test_InstanceParameters(self):
        # Empty parameters.
        instance = core.StackExchangeQuery()
        self.assertFalse(instance.parameters.getParameterString()), "instance.parameters should be empty, but it is not."
        self.assertEqual(instance.parameters.getSize(), 0), "instance.parameters should have 0 keys."
        # Parameters passed in during construction.
        params = {"tagged":"ptvs", "pagesize":"1"}
        instance = core.StackExchangeQuery(params)
        self.assertEqual(instance.parameters.getSize(), 2), "instance.parameters should have 2 keys."
        instance.parameters.addParameter("site", "stackoverflow")
        self.assertEqual(instance.parameters.getSize(), 3), "instance.parameters should have 3 keys."

if __name__ == '__main__':
    unittest.main()
