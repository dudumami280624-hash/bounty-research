import unittest
from global_bounties import extract, platform

class GlobalBountyTests(unittest.TestCase):
    def test_only_positive_bounty(self):
        data={"programs":[
            {"name":"A","url":"https://hackerone.com/a","bounty":True},
            {"name":"B","url":"https://bugcrowd.com/b","bounty":False},
            {"name":"A duplicate","url":"https://hackerone.com/a","bounty":True},
            {"name":"Insecure","url":"http://hackerone.com/c","bounty":True},
        ]}
        found=extract(data)
        self.assertEqual(len(found),1)
        self.assertEqual(found[0]["platform"],"HackerOne")
        self.assertFalse(found[0]["cash_payment_verified"])
        self.assertFalse(found[0]["open_and_authorized_verified"])
    def test_other_platform(self):
        self.assertEqual(platform("https://app.intigriti.com/programs/a"),"Intigriti")
        self.assertEqual(platform("https://example.org/policy"),"Independent / other")
    def test_invalid_data(self):
        with self.assertRaises(ValueError):
            extract({"programs":{}})
if __name__=="__main__":
    unittest.main()
