from src import akamai_api_requests_abstractions as ak
from src import akamai_http_requests_wrapper as wrapper
import unittest
import warnings


class ApiRequestsTests(unittest.TestCase):

    def test_get_policy(self):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        edgerc_location = '~/.edgerc'
        with wrapper.AkamaiRequestWrapper(edgerc_location) as wr:
            redirect_policy = ak.get_shared_policy_by_name("test", edgerc_location)
        self.assertTrue(redirect_policy is None)

    def test_get_policy_approximate_name(self):
        edgerc_location = '~/.edgerc'
        with wrapper.AkamaiRequestWrapper(edgerc_location) as wr:
            redirect_policy = ak.get_shared_policies_by_approximate_name("test", edgerc_location)
        self.assertTrue(len(redirect_policy) == 0)


if __name__ == '__main__':
    unittest.main()
