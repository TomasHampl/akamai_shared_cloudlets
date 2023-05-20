import json
from os import path

from akamai.edgegrid import EdgeRc

from akamai_shared_cloudlets.src.akamai_api_requests_abstractions import AkamaiApiRequestsAbstractions


def get_request_loc():
    return "akamai_shared_cloudlets.src.akamai_http_requests_wrapper.AkamaiRequestWrapper.send_get_request"


def get_sample_json(api_call):
    file_name = path.normpath(f"supplemental/{api_call}.json")
    if path.isfile(file_name):
        with open(file_name, mode="r") as json_file:
            return json.load(json_file)
    else:
        raise FileNotFoundError(f"Could not find the file {file_name}")


def new_negative_send_get_request(path: str, query_params: dict, *args, **kwargs):
    return get_sample_json('list_shared_policies')


def get_akamai_host(edgerc_path):
    edge_rc = EdgeRc(edgerc_path)
    return edge_rc.get('default', 'host')


def test_list_shared_policies(requests_mock):
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.list_shared_policies()
    assert response is not None


def test_list_shared_policies_negative(requests_mock):
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", status_code=404)
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.list_shared_policies()
    assert response is None


def test_find_shared_policy_by_name(requests_mock):
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.get_shared_policy_by_name("static_assets_redirector")
    assert response == 1001


def test_find_shared_policy_by_name_negative(requests_mock):
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.get_shared_policy_by_name("not_present")
    assert response is None


def test_find_shared_policy_by_approximate_name(requests_mock):
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.get_shared_policies_by_approximate_name("assets")
    assert response == {"static_assets_redirector": 1001}


def test_find_shared_policy_by_approximate_name_negative(requests_mock):
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies", json=get_sample_json("list_shared_policies"))
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.get_shared_policies_by_approximate_name("ssssss")
    assert response == {}


def test_get_policy_by_id(requests_mock):
    policy_id = "1001"
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}",
                      json=get_sample_json("get_a_policy"))
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.get_policy_by_id("1001")
    assert response is not None


def test_get_policy_by_id_negative(requests_mock):
    policy_id = "1001"
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}",
                      status_code=401)
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.get_policy_by_id("1001")
    assert response is None


def test_list_policy_versions(requests_mock):
    policy_id = "1001"
    api_destination = get_akamai_host('supplemental/sample_edgerc')
    requests_mock.get(f"https://{api_destination}/cloudlets/v3/policies/{policy_id}/versions",
                      json=get_sample_json('list_policy_versions'))
    api = AkamaiApiRequestsAbstractions('supplemental/sample_edgerc')
    response = api.list_policy_versions(policy_id, 3, 100)
    assert response is not None
    content = response["content"]
    assert content[0]["description"] == "Initial version"
