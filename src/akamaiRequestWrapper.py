import json
from urllib.parse import urljoin

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from requests import Request


def sign_request(edgerc_location: str = '~/.edgerc'):
    session = requests.Session()
    edge_rc, section = get_edgerc_file(edgerc_location)
    session.auth = EdgeGridAuth.from_edgerc(edge_rc, section)
    return session


def get_base_url(edgerc_location: str = '~/.edgerc'):
    """
    Utility method that extracts the 'hostname' for our API call from the credentials file ('edgerc'). If the
    credentials file location is not provided, it defaults to ~/.edgerc
    """
    try:
        return 'https://%s' % read_edge_grid_file("cloudlets", "host", edgerc_location)
    except:
        print("Cannot find section 'cloudlets' in EdgeRc file, falling back to 'default'")
        return 'https://%s' % read_edge_grid_file("default", "host", edgerc_location)


def read_edge_grid_file(section: str, key: str, edgerc_location: str = '~/.edgerc') -> str:
    """
    Reads the credentials file and provides the value of the specified section. If such section does not exist,
    we try to return the value related to 'default' section (assuming that at least THAT should always exist in
    Akamai credentials file)
    """
    edgerc = EdgeRc(edgerc_location)
    if edgerc.has_section(section):
        section_to_get = section
    else:
        section_to_get = 'default'
    return edgerc.get(section_to_get, key)


def get_edgerc_file(edgerc_location: str):
    """
    Returns the 'edgerc' file based on the location.
    """
    if edgerc_location is None:
        edgerc_location = '~/.edgerc'

    edge_rc = EdgeRc(edgerc_location)

    if edge_rc.has_section('cloudlets'):
        section = 'cloudlets'
    else:
        section = 'default'
    return edge_rc, section


def send_get_request(path: str, query_params: dict, edgerc_location: str = '~/.edgerc'):
    """
    Serves as an abstraction of most of the 'get' http requests
    """
    base_url = get_base_url(edgerc_location)
    session = sign_request(edgerc_location)
    session.headers.update(query_params)
    return session.get(urljoin(base_url, path))


def send_post_request(path: str, post_body: dict, edgerc_location: str = '~/.edgerc'):
    """
    Serves as an abstraction of most of the 'post' http requests
    """
    request_headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    base_url = get_base_url(edgerc_location)
    destination = urljoin(base_url, path)
    request = Request('POST', destination, data=json.dumps(post_body), headers=request_headers)
    session = sign_request(edgerc_location)

    prepared_request = session.prepare_request(request)
    return session.send(prepared_request)


def send_delete_request(path: str, edgerc_location: str = '~/.edgerc'):
    """
    Serves as an abstraction of 'delete' request. Contains no logic to assess the correctness of the data provided or
    response returned.
    """
    request_headers = {
        "accept": "application/problem+json"
    }
    base_url = get_base_url(edgerc_location)
    destination = urljoin(base_url, path)
    request = Request('DELETE', destination, headers=request_headers)
    session = sign_request(edgerc_location)
    prepared_request = session.prepare_request(request)
    return session.send(prepared_request)
