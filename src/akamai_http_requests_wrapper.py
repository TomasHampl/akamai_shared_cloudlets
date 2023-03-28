import json
from urllib.parse import urljoin

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from requests import Request
from src.akamai_project_constants import JSON_CONTENT_TYPE
from src.akamai_project_constants import DEFAULT_EDGERC_LOCATION


class AkamaiRequestWrapper(object):
    """
    Serves as a wrapper for the actual http requests (including the authentication) targeting the Akamai APIs
    """

    edgerc_location = DEFAULT_EDGERC_LOCATION

    def __init__(self, edgerc_location: str):
        if edgerc_location is None:
            self.edgerc_location = DEFAULT_EDGERC_LOCATION
        else:
            self.edgerc_location = edgerc_location
        self.session = requests.session()

    def get_info(self):
        print("This is a AkamaiRequestWrapper class")

    def __enter__(self):
        return self

    def close(self):
        self.session.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_edgerc_location(self):
        """
        Classical 'getter' function for 'edgerc_location' property in the class
        @return: location of the 'edgerc_location'
        """
        return self.edgerc_location

    def set_edgerc_location(self, value):
        """
        Setter method of the 'edgerc_location' attribute in this class
        @param value: location of the edgerc_location to store in this class
        """
        self.edgerc_location = value

    def sign_request(self):
        """
        Method to sign the session that is part of all the requests provided by this class
        @return: Session object that already contains the authentication to Akamai based on the
        edgerc_location attribute
        """
        edge_rc, section = self.get_edgerc_file(self.get_edgerc_location())
        self.session.auth = EdgeGridAuth.from_edgerc(edge_rc, section)
        return self.session

    def get_base_url(self):
        """
        Utility method that extracts the 'hostname' for our API call from the credentials file ('edgerc'). If the
        credentials file location is not provided, it defaults to ~/.edgerc
        """
        try:
            return 'https://%s' % self.read_edge_grid_file("cloudlets", "host")
        except BaseException:
            print("Cannot find section 'cloudlets' in EdgeRc file, falling back to 'default'")
            return 'https://%s' % self.read_edge_grid_file("default", "host")

    def read_edge_grid_file(self, section: str, key: str) -> str:
        """
        Reads the credentials file and provides the value of the specified section. If such section does not exist,
        we try to return the value related to 'default' section (assuming that at least THAT should always exist in
        Akamai credentials file)
        @param section: is an identifier of a 'section' in the Akamai credentials file
        @param key: is the 'key' in the section (such as host or secret_token)
        @return: the value associated with the provided host within the section, or, if missing, then that section
        from the 'default' section
        """
        edgerc = EdgeRc(self.edgerc_location)
        if edgerc.has_section(section):
            section_to_get = section
        else:
            section_to_get = 'default'
        return edgerc.get(section_to_get, key)

    def get_edgerc_file(self, edgerc_location: str):
        """
        Simple method that provides the EdgeRc object plus the section that is available in the file - it prefers the
        'cloudlets' section to 'default' or any other. However, if no 'cloudlets' section exists, then it provides
        the 'default'
        @return: a tuple of an instance of EdgeRc object and section
        """
        if edgerc_location is None:
            self.edgerc_location = DEFAULT_EDGERC_LOCATION

        edge_rc = EdgeRc(edgerc_location)

        if edge_rc.has_section('cloudlets'):
            section = 'cloudlets'
        else:
            section = 'default'
        return edge_rc, section

    def send_get_request(self, path: str, query_params: dict):
        """
        Serves as GET request abstraction
        @param path: is the path where we want to send the request. It is assumed
        the hostname (aka base_url) would come from the EdgeGrid file
        @param query_params: a dictionary of additional query parameters, may be empty dictionary
        @return: raw response provided by Akamai, if you want json, do it yourself ;)
        """
        if query_params is None:
            query_params = {}
        base_url = self.get_base_url()
        session = self.sign_request()
        session.headers.update(query_params)
        return session.get(urljoin(base_url, path))

    def send_post_request(self, path: str, post_body: dict):
        """
        Serves as an abstraction of most of the 'post' http requests. Sets the 'accept' & 'content-type' headers to
        'application/json'
        @param path: is the path where we want to send the request. It is assumed the hostname (aka base_url) would come
        from the EdgeGrid file
        @param post_body: is a dictionary that represents the post body
        @return: raw response from Akamai, if you want json, do it yourself ;)
        """
        request_headers = {
            "accept": JSON_CONTENT_TYPE,
            "content-type": JSON_CONTENT_TYPE
        }
        base_url = self.get_base_url()
        destination = urljoin(base_url, path)
        request = Request('POST', destination, data=json.dumps(post_body), headers=request_headers)
        session = self.sign_request()

        prepared_request = session.prepare_request(request)
        return session.send(prepared_request)

    def send_delete_request(self, path: str):
        """
        Serves as an abstraction of 'delete' request. Contains no logic to assess the correctness of the data provided
        or response returned.
        @param path: is the path where we want to send the request. It is assumed the hostname (aka base_url) would come
        from the EdgeGrid file
        @return: raw response from Akamai, if you want json (or other processing), you need to do it yourself
        """
        request_headers = {
            "accept": "application/problem+json"
        }
        base_url = self.get_base_url()
        destination = urljoin(base_url, path)
        request = Request('DELETE', destination, headers=request_headers)
        session = self.sign_request()
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request)

    def send_put_request(self, path: str, body: dict):
        """
        Serves as an abstraction of PUT request. Contains no logic to assess the correctness of the data provided or
        response returned
        @param path: is the path where we want to send the request, It is assumed the hostname (aka base_url) would come
        from the EdgeGrid file
        @param body: a dict of put body, may be empty (if there's nothing you want to pass)
        @return: raw response from Akamai, if you want json (or other processing), you need to do it yourself
        """
        request_headers = {
            "accept": JSON_CONTENT_TYPE,
            "content-type": JSON_CONTENT_TYPE
        }
        base_url = self.get_base_url()
        destination = urljoin(base_url, path)
        request = Request('PUT', destination, data=json.dumps(body), headers=request_headers)
        session = self.sign_request()
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request)


if __name__ == '__main__':
    with AkamaiRequestWrapper(DEFAULT_EDGERC_LOCATION) as wrapper:
        print(wrapper.get_info())
