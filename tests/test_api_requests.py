import os
import unittest

from akamai_shared_cloudlets.src import akamai_http_requests_wrapper as wrapper


class TestAkamaiRequestWrapper(unittest.TestCase):

    def test_read_edgerc_file(self):
        edgerc_location = self.get_working_dir() + "sample_edgerc"
        request_wrapper = wrapper.AkamaiRequestWrapper(edgerc_location)
        edgerc = request_wrapper.get_edgerc_file(edgerc_location)
        self.assertTrue(edgerc[1] == "default")

        edgerc_signer = edgerc[0]
        has_cloudlets = edgerc_signer.has_section("cloudlets")
        self.assertFalse(has_cloudlets)

    def test_get_base_url(self):
        edgerc_location = self.get_working_dir() + "sample_edgerc"

        request_wrapper = wrapper.AkamaiRequestWrapper(edgerc_location)
        base_url = request_wrapper.get_base_url()
        self.assertTrue(base_url, "https://akab-wmjabebv6bfjx6zw-uakssaeiqimho6qi.aaaaa.dddddd.net")

    def test_get_base_url_cloudlet(self):
        edgerc_location = self.get_working_dir() + "sample_edgerc_cloudlet"
        request_wrapper = wrapper.AkamaiRequestWrapper(edgerc_location)
        base_url = request_wrapper.get_base_url()
        self.assertTrue(base_url, "dummy.cloudlets.base.url")

    def test_sign_request(self):
        edgerc_location = self.get_working_dir() + "sample_edgerc"
        request_wrapper = wrapper.AkamaiRequestWrapper(edgerc_location)
        signed_session = request_wrapper.sign_request()
        access_token = signed_session.auth.ah.access_token
        self.assertTrue(access_token, "akab-dummy-dummy-dummy-dummy")

    @staticmethod
    def get_working_dir():
        if "tests" in os.getcwd():
            return os.getcwd() + "/"
        else:
            return os.getcwd() + "/" + "tests" + "/"


if __name__ == '__main__':
    unittest.main()
