import json
from configparser import NoSectionError
from urllib.parse import urljoin
from pathlib import Path

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from requests import Request

from . import akamai_project_constants
from . import akamai_project_constants as constants
from . import exceptions
from . import shared as common


def sign_request(edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Method to sign the session that is part of all the requests provided by this class
    @param edgerc_location: location of the edgerc file, default to {@code ~/.edgerc} if not provided.
    @return: Session object that already contains the authentication to Akamai based on the
    edgerc_location attribute
    """
    edge_rc, section = get_edgerc_file(edgerc_location)
    session = requests.session()
    session.auth = EdgeGridAuth.from_edgerc(edge_rc, section)
    return session


def get_base_url(edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Utility method that extracts the 'hostname' for our API call from the credentials file ('edgerc'). If the
    credentials file location is not provided, it defaults to ~/.edgerc
    """
    try:
        return 'https://%s' % read_edge_grid_file("cloudlets", "host", edgerc_location)
    except NoSectionError:
        print("Cannot find section 'cloudlets' in EdgeRc file, falling back to 'default'")
        return 'https://%s' % read_edge_grid_file("default", "host", edgerc_location)
    except exceptions.EdgeRcFileMissing:
        print(f"Unable to find the 'edgerc' file at provided location {edgerc_location}")


def read_edge_grid_file(
        section: str,
        key: str,
        edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION) -> str:
    """
    Reads the credentials file and provides the value of the specified section. If such section does not exist,
    we try to return the value related to 'default' section (assuming that at least THAT should always exist in
    Akamai credentials file)
    @param edgerc_location: location of the edgerc file, if not provided, defaults to {@code ~/.edgerc}
    @param section: is an identifier of a 'section' in the Akamai credentials file
    @param key: is the 'key' in the section (such as host or secret_token)
    @return: the value associated with the provided host within the section, or, if missing, then that section
    from the 'default' section
    """
    path = Path(edgerc_location)
    if path.is_file():
        edgerc = EdgeRc(edgerc_location)
        if edgerc.has_section(section):
            section_to_get = section
        else:
            section_to_get = 'default'
        return edgerc.get(section_to_get, key)
    raise exceptions.EdgeRcFileMissing(f"File {edgerc_location} could not be found. This is NOT ok.")


def get_edgerc_file(edgerc_location: str):
    """
    Simple method that provides the EdgeRc object plus the section that is available in the file - it prefers the
    'cloudlets' section to 'default' or any other. However, if no 'cloudlets' section exists, then it provides
    the 'default'
    @return: a tuple of an instance of EdgeRc object and section or None if the credentials file does not exist
    in the initialized location
    """
    if edgerc_location is None:
        edgerc_location = akamai_project_constants.DEFAULT_EDGERC_LOCATION

    if does_edgegrid_file_exist(edgerc_location) is True:
        edge_rc = EdgeRc(edgerc_location)

        if edge_rc.has_section('cloudlets'):
            section = 'cloudlets'
        else:
            section = 'default'
        return edge_rc, section

    raise exceptions.EdgeRcFileMissing(f"Could not find the edgerc file in {edgerc_location}")


def does_edgegrid_file_exist(edge_file_location: str):
    path = Path(edge_file_location)
    if path.is_file():
        return True
    return False


def send_get_request(
        path: str,
        query_params: dict,
        edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Serves as GET request abstraction
    @param edgerc_location: is the location of Akamai credentials file, if not provided, defaults to ~/.edgerc
    @param path: is the path where we want to send the request. It is assumed
    the hostname (aka base_url) would come from the EdgeGrid file
    @param query_params: a dictionary of additional query parameters, may be empty dictionary
    @return: raw response provided by Akamai, if you want json, do it yourself ;)
    """
    if query_params is None:
        query_params = {}
    real_edgerc_location = common.get_home_folder(edgerc_location)
    base_url = get_base_url(real_edgerc_location)
    session = sign_request(real_edgerc_location)
    session.headers.update(query_params)
    final_url = urljoin(base_url, path)
    print("Sending request to Akamai...")
    return session.get(final_url)


def send_post_request(
        path: str,
        post_body: dict,
        edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Serves as an abstraction of most of the 'post' http requests. Sets the 'accept' & 'content-type' headers to
    'application/json'
    @param edgerc_location: is the location of Akamai credentials file, if not provided, defaults to ~/.edgerc
    @param path: is the path where we want to send the request. It is assumed the hostname (aka base_url) would come
    from the EdgeGrid file
    @param post_body: is a dictionary that represents the post body
    @return: raw response from Akamai, if you want json, do it yourself ;)
    """
    request_headers = {
        "accept": constants.JSON_CONTENT_TYPE,
        "content-type": constants.JSON_CONTENT_TYPE
    }
    real_edgerc_location = common.get_home_folder(edgerc_location)
    base_url = get_base_url(real_edgerc_location)
    destination = urljoin(base_url, path)
    request = Request('POST', destination, data=json.dumps(post_body), headers=request_headers)
    session = sign_request(real_edgerc_location)

    prepared_request = session.prepare_request(request)
    return session.send(prepared_request)


def send_delete_request(path: str, edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Serves as an abstraction of 'delete' request. Contains no logic to assess the correctness of the data provided
    or response returned.
    @param edgerc_location: is the location of Akamai credentials file, if not provided, defaults to ~/.edgerc
    @param path: is the path where we want to send the request. It is assumed the hostname (aka base_url) would come
    from the EdgeGrid file
    @return: raw response from Akamai, if you want json (or other processing), you need to do it yourself
    """
    request_headers = {
        "accept": "application/problem+json"
    }
    real_edgerc_location = common.get_home_folder(edgerc_location)
    base_url = get_base_url(real_edgerc_location)
    destination = urljoin(base_url, path)
    request = Request('DELETE', destination, headers=request_headers)
    session = sign_request(real_edgerc_location)
    prepared_request = session.prepare_request(request)
    return session.send(prepared_request)


def send_put_request(path: str, body: dict, edgerc_location: str = akamai_project_constants.DEFAULT_EDGERC_LOCATION):
    """
    Serves as an abstraction of PUT request. Contains no logic to assess the correctness of the data provided or
    response returned
    @param edgerc_location: is the location of Akamai credentials file, if not provided, defaults to ~/.edgerc
    @param path: is the path where we want to send the request, It is assumed the hostname (aka base_url) would come
    from the EdgeGrid file
    @param body: a dict of put body, may be empty (if there's nothing you want to pass)
    @return: raw response from Akamai, if you want json (or other processing), you need to do it yourself
    """
    request_headers = {
        "accept": constants.JSON_CONTENT_TYPE,
        "content-type": constants.JSON_CONTENT_TYPE
    }
    real_edgerc_location = common.get_home_folder(edgerc_location)
    base_url = get_base_url(real_edgerc_location)
    destination = urljoin(base_url, path)
    request = Request('PUT', destination, data=json.dumps(body), headers=request_headers)
    session = sign_request(real_edgerc_location)
    prepared_request = session.prepare_request(request)
    return session.send(prepared_request)
