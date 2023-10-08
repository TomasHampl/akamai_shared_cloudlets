import unittest
from . import common_test_func as test_common
from src.akamai_shared_cloudlets.http_requests import *


class TestAkamaiRequestWrapper(unittest.TestCase):

    def test_read_edgerc_file(self):
        edgerc_location = test_common.get_sample_edgerc()
        edgerc = get_edgerc_file(edgerc_location)
        self.assertTrue(edgerc[1] == "default")

        edgerc_signer = edgerc[0]
        has_cloudlets = edgerc_signer.has_section("cloudlets")
        self.assertFalse(has_cloudlets)

    def test_get_base_url(self):
        edgerc_location = test_common.get_sample_edgerc()
        base_url = get_base_url(edgerc_location)
        self.assertTrue(base_url, "https://dummy.luna.akamaiapis.net")

    def test_get_base_url_cloudlet(self):
        edgerc_location = test_common.get_sample_edgerc("sample_edgerc")
        base_url = get_base_url(edgerc_location)
        self.assertTrue(base_url, "dummy.cloudlets.base.url")

    def test_sign_request(self):
        edgerc_location = test_common.get_sample_edgerc()
        signed_session = sign_request(edgerc_location)
        access_token = signed_session.auth.ah.access_token
        self.assertTrue(access_token, "akab-dummy-dummy-dummy-dummy")


if __name__ == '__main__':
    unittest.main()
